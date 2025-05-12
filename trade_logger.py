import pandas as pd
import os

class TradeLogger:
    @staticmethod
    def save_trades(trades, filename):
        # Ensure the directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        # Convert the trades list to a pandas DataFrame
        trades_df = pd.DataFrame(trades)

        # Save the DataFrame to a CSV file
        trades_df.to_csv(filename, index=False)
        print(f"Saved trade history to {filename}")
    
    @staticmethod
    def load_trades(filename):
        if os.path.exists(filename):
            trades_df = pd.read_csv(filename)
            return trades_df
        else:
            print(f"File {filename} not found.")
            return pd.DataFrame()  # Return an empty DataFrame if the file doesn't exist
