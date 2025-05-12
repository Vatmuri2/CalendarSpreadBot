import pandas as pd
from polygon import BaseClient

class DataFetcher:
    def __init__(self, api_key):
        self.client = BaseClient(api_key)

    def get_options_data(self, symbol, expiration_date):
        try:
            # Get options contracts for the symbol
            options = self.client.list_options_contracts(underlying_ticker=symbol, expiration_date=expiration_date)
            records = [{
                "symbol": opt.symbol,
                "expiration_date": opt.expiration_date,
                "strike_price": opt.strike_price,
                "type": opt.contract_type,
                "ask": opt.ask_price,
                "bid": opt.bid_price,
                "mid": (opt.ask_price + opt.bid_price) / 2 if opt.ask_price and opt.bid_price else None
            } for opt in options]
            df = pd.DataFrame(records)
            return df
        except Exception as e:
            print(f"Error fetching options data for {symbol}: {e}")
            return pd.DataFrame()  # Return an empty DataFrame if there is an error

    def get_historical_data(self, symbol, start_date, end_date):
        # This can be used for fallback if you still want historical price data for SPY
        try:
            trades = self.client.get_trades(symbol, from_=start_date, to=end_date)
            records = [{
                "timestamp": pd.to_datetime(trade.timestamp, unit='ms'),
                "price": trade.price,
                "volume": trade.size
            } for trade in trades]
            df = pd.DataFrame(records)
            df.set_index("timestamp", inplace=True)
            return df
        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {e}")
            return pd.DataFrame()  # Return an empty DataFrame if there is an error
