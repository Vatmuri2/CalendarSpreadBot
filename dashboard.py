import pandas as pd
import matplotlib.pyplot as plt
import os

class Dashboard:
    @staticmethod
    def display_portfolio(results):
        """
        Display the portfolio performance summary in the console.
        """
        for ticker, result in results.items():
            print(f"Ticker: {ticker}")
            print(f"  Final Balance: ${result['balance']:.2f}")
            print(f"  Buy & Hold P/L: ${result['bnh_final_balance'] - 1000:.2f}")
            print(f"  Trades Executed: {len(result['trades'])}")
            print(f"  Final Portfolio Balance: ${result['balance']:.2f}")
            print(f"  ----------------------\n")

    @staticmethod
    def plot_portfolio_charts(results):
        """
        Plot portfolio performance for each ticker.
        """
        for ticker, result in results.items():
            trades = result['trades']
            balance_history = [1000]  # Start with an initial balance of 1000

            for trade in trades:
                # Track balance over time based on P/L from trades
                balance_history.append(balance_history[-1] + trade['profit_loss'])

            # Create the plot
            plt.figure(figsize=(10, 5))
            plt.plot(balance_history, label=f"{ticker} Portfolio", color="blue")
            plt.title(f"{ticker} Portfolio Performance")
            plt.xlabel("Trade Number")
            plt.ylabel("Portfolio Balance ($)")
            plt.legend()
            plt.grid(True)

            # Save the plot
            plot_file = f"plots/{ticker}_portfolio_performance.png"
            os.makedirs(os.path.dirname(plot_file), exist_ok=True)
            plt.savefig(plot_file)
            plt.close()

    @staticmethod
    def create_html_dashboard(results, start_date, end_date, output_file="dashboard.html"):
        """
        Create an HTML dashboard that compares strategy vs. Buy & Hold.
        """
        html_content = f"""
        <html>
        <head>
            <title>Backtest Dashboard - Calendar Spread Strategy</title>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 8px; text-align: left; border: 1px solid #ddd; }}
                th {{ background-color: #f2f2f2; }}
                .chart-container {{ display: flex; flex-wrap: wrap; }}
                .chart-container img {{ margin: 10px; max-width: 500px; }}
            </style>
        </head>
        <body>
            <h1>Backtest Results: Calendar Spread Strategy</h1>
            <h3>Backtest Period: {start_date} to {end_date}</h3>

            <h2>Portfolio Summary</h2>
            <table>
                <tr><th>Ticker</th><th>Final Balance</th><th>Buy & Hold P/L</th><th>Trades Executed</th></tr>
        """
        for ticker, result in results.items():
            html_content += f"""
            <tr>
                <td>{ticker}</td>
                <td>${result['balance']:.2f}</td>
                <td>${result['bnh_final_balance'] - 1000:.2f}</td>
                <td>{len(result['trades'])}</td>
            </tr>
            """
        html_content += "</table>"

        html_content += """
            <h2>Portfolio Performance Charts</h2>
            <div class="chart-container">
        """
        for ticker, result in results.items():
            plot_file = f"plots/{ticker}_portfolio_performance.png"
            html_content += f'<img src="{plot_file}" alt="{ticker} Portfolio Performance">'

        html_content += "</div></body></html>"

        # Save the HTML content to the specified file
        with open(output_file, "w") as file:
            file.write(html_content)

        print(f"Dashboard saved as {output_file}")
