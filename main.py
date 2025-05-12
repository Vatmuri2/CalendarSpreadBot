import datetime
from data_fetcher import DataFetcher
from indicators import Indicators
from trade_simulator import TradeSimulator
from trade_logger import TradeLogger
from dashboard import Dashboard

# Initialize the fetcher and simulator
fetcher = DataFetcher('tAj9_5sMUEaQt0Y_m5fYkfF24dzMsSUp')
simulator = TradeSimulator(initial_balance=1000)

# Define the tickers (SPY for calendar spread)
tickers = ["SPY"]

START_DATE = "2023-01-01"
END_DATE = datetime.datetime.today().strftime("%Y-%m-%d")

results = {}

# Loop through each ticker (we're only using SPY for now)
for ticker in tickers:
    print(f"Processing {ticker} ...")
    
    # Fetch historical data for SPY
    START_DATE = "2023-01-01"
    END_DATE = datetime.datetime.today().strftime("%Y-%m-%d")  # Ensure end date is set correctly

    df = fetcher.get_historical_data(ticker, START_DATE, END_DATE)
    if df.empty:
        print(f"No data returned for {ticker}. Skipping.")
        continue

    # Apply Indicators (SMA, RSI, MACD)
    df = Indicators.compute_sma(df, 50)
    df = Indicators.compute_sma(df, 200)
    df = Indicators.compute_rsi(df, 14)
    df = Indicators.compute_macd(df)
    
    # Calendar Spread Strategy
    calendar_spread_trades = []
    for index, row in df.iterrows():
        price_today = row["close"]
        date_today = index.date()
 
        # Check for move greater than 0.5%
        if index > 0:  # Skip the first row
            prev_row = df.iloc[index - 1]
            price_previous = prev_row["close"]

            price_move_pct = (price_today - price_previous) / price_previous * 100

            # If move is greater than 0.5%, assume a reversal the next day
            if abs(price_move_pct) > 0.5:
                expected_direction = "UP" if price_move_pct < 0 else "DOWN"
                
                # Record the trade as a potential Calendar Spread setup
                calendar_spread_trades.append({
                    "entry_date": date_today,
                    "entry_price": price_today,
                    "expected_direction": expected_direction,
                    "price_move_pct": price_move_pct
                })

    # Save the calendar spread trade history
    TradeLogger.save_trades(calendar_spread_trades, filename=f"logs/{ticker}_calendar_spread_trade_history.csv")

    # Save results for dashboard or other analysis
    results[ticker] = {
        "df": df,
        "calendar_spread_trades": calendar_spread_trades
    }

# 1) Print console summary
Dashboard.display_portfolio(results)

# 2) Plot charts for calendar spread strategy
Dashboard.plot_portfolio_charts(results)

# 3) Create HTML dashboard comparing Calendar Spread and Buy & Hold
Dashboard.create_html_dashboard(results, START_DATE, END_DATE, output_file="calendar_spread_dashboard.html")
