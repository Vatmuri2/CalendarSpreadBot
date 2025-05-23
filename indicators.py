# indicators.py
import pandas as pd

class Indicators:
    @staticmethod
    def compute_sma(df, window):
        """
        Calculate Simple Moving Average (SMA)
        """
        df[f"SMA{window}"] = df["close"].rolling(window=window).mean()
        return df

    @staticmethod
    def compute_rsi(df, period=14):
        """
        Calculate Relative Strength Index (RSI)
        """
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        df["RSI"] = 100 - (100 / (1 + rs))
        return df

    @staticmethod
    def compute_macd(df, short=12, long=26, signal=9):
        """
        Calculate MACD (Moving Average Convergence Divergence)
        """
        df["EMA12"] = df["close"].ewm(span=short, adjust=False).mean()
        df["EMA26"] = df["close"].ewm(span=long, adjust=False).mean()
        df["MACD"] = df["EMA12"] - df["EMA26"]
        df["MACD_Signal"] = df["MACD"].ewm(span=signal, adjust=False).mean()
        return df
