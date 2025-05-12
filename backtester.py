import pandas as pd
import logging

class CalendarSpreadBacktester:
    def __init__(self, initial_balance=10000, stop_loss_pct=0.1, target_pct=0.2):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.stop_loss_pct = stop_loss_pct
        self.target_pct = target_pct
        self.trades = []
        self.current_position = None
        self.in_progress_trade = None
        logging.basicConfig(filename="logs/calendar_spread_trades.log", level=logging.INFO)

    def execute_trade(self, signal, df, date_index):
        """
        Execute a calendar spread trade based on signal.
        """
        price = df.loc[date_index, 'close']
        cost = self.balance * 0.05  # Example: invest 5% of the balance
        shares = cost / price

        if signal == 'BUY_CALL_SPREAD':
            # Example call options: let's assume we buy a call at-the-money
            trade_type = 'CALL'
        elif signal == 'BUY_PUT_SPREAD':
            # Example put options: let's assume we buy a put at-the-money
            trade_type = 'PUT'
        else:
            return None

        self.balance -= cost
        self.current_position = {
            'entry_date': df.index[date_index],
            'entry_price': price,
            'shares': shares,
            'trade_type': trade_type,
            'cost_of_trade': cost,
            'status': 'OPEN'
        }

        logging.info(f"{trade_type} SPREAD entered at {price:.2f} on {df.index[date_index]}")

    def close_trade(self, df, date_index):
        """
        Close the current position based on price movement.
        """
        if self.current_position:
            exit_price = df.loc[date_index, 'close']
            profit_loss = (exit_price - self.current_position['entry_price']) * self.current_position['shares']
            self.balance += profit_loss  # Add P/L to balance

            self.trades.append({
                **self.current_position,
                'exit_date': df.index[date_index],
                'exit_price': exit_price,
                'profit_loss': profit_loss,
                'status': 'CLOSED'
            })

            logging.info(f"Trade closed at {exit_price:.2f} on {df.index[date_index]} | P/L: {profit_loss:.2f}")
            self.current_position = None

    def run_backtest(self, df):
        for i in range(1, len(df)):
            signal = df.iloc[i]['signal']
            if signal and not self.current_position:
                # If there's a signal and no open position, execute a new trade
                self.execute_trade(signal, df, i)

            if self.current_position:
                # Close trade after some condition (stop loss or target hit)
                price = df.iloc[i]['close']
                entry_price = self.current_position['entry_price']
                if price <= entry_price * (1 - self.stop_loss_pct) or price >= entry_price * (1 + self.target_pct):
                    self.close_trade(df, i)

        return self.trades, self.balance
