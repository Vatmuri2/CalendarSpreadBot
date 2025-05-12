import pandas as pd
import logging
import datetime

logging.basicConfig(filename="logs/calendar_spread.log", level=logging.INFO)

class CalendarSpread:
    def __init__(self, initial_balance=1000, move_threshold_pct=0.005, stop_loss_pct=0.02, target_pct=0.05):
        self.initial_balance = initial_balance
        self.move_threshold_pct = move_threshold_pct  # Threshold for price move (0.5%)
        self.stop_loss_pct = stop_loss_pct
        self.target_pct = target_pct
        self.trades = []
        self.balance = initial_balance
        self.current_position = None
        self.in_progress_trade = None

    def simulate_spread(self, df):
        for index, row in df.iterrows():
            price = row["close"]
            date = index.date()

            # If there's an existing position, monitor exit conditions
            if self.current_position:
                self.handle_exit_conditions(price, date)
                continue  # Skip to next day if there's an open position

            # ENTRY: Check for a price move greater than 0.5% from previous day
            if index > 0:
                prev_price = df.iloc[index - 1]["close"]
                price_move_pct = (price - prev_price) / prev_price

                # If the price moves greater than 0.5% in one direction, we expect a move in the opposite direction next day
                if abs(price_move_pct) > self.move_threshold_pct:
                    direction = "UP" if price_move_pct < 0 else "DOWN"
                    logging.info(f"Detected {direction} move of {price_move_pct*100:.2f}% on {date}. Entering calendar spread.")

                    # Simulate selling a near-term option and buying a longer-term option
                    self.enter_calendar_spread(price, date)

        # If there's an open trade, track its progress
        if self.current_position:
            latest_price = df.iloc[-1]["close"]
            self.current_position["latest_price"] = latest_price
            self.current_position["profit_loss"] = (latest_price - self.current_position["entry_price"]) * self.current_position["shares"]
            self.in_progress_trade = self.current_position

        return self.trades, self.balance

    def enter_calendar_spread(self, price, date):
        """
        Simulate entering the calendar spread strategy by selling a short option and buying a long option.
        """
        cost = self.balance
        shares = cost / price
        self.balance -= cost  # Deduct cost immediately

        self.current_position = {
            "entry_date": date,
            "entry_price": price,
            "shares": shares,
            "stop_loss": price * (1 - self.stop_loss_pct),
            "target_price": price * (1 + self.target_pct),
            "status": "OPEN",
            "cost_of_trade": cost,
        }

        logging.info(f"Entered Calendar Spread at {price:.2f} on {date}. Balance after entry: {self.balance:.2f}")

    def handle_exit_conditions(self, price, date):
        """
        Check for exit conditions (stop loss or target price hit).
        """
        if price <= self.current_position["stop_loss"]:
            self.close_trade(price, date, reason="STOP-LOSS")
        elif price >= self.current_position["target_price"]:
            self.close_trade(price, date, reason="TARGET HIT")

    def close_trade(self, price, date, reason):
        """
        Close the current trade and calculate profit/loss.
        """
        profit_loss = (price - self.current_position["entry_price"]) * self.current_position["shares"]
        self.balance += self.current_position["shares"] * price

        # Save trade details
        self.trades.append({
            **self.current_position,
            "exit_date": date,
            "exit_price": price,
            "profit_loss": profit_loss,
            "status": "CLOSED",
            "reason": reason,
        })

        logging.info(f"{reason} hit at {price:.2f} on {date}, P/L: {profit_loss:.2f}")
        self.current_position = None
