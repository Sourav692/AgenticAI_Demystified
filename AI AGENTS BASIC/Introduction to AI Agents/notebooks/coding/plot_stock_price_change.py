# filename: plot_stock_price_change.py

import yfinance as yf
import matplotlib.pyplot as plt

# Define the tickers for the companies
# Since OpenAI is not publicly traded, we will use NVIDIA as a comparable AI company
companies = ['NVDA', 'AAPL']  # Substitute AAPL with any other stock of interest

# Define the period for the stock data
start_date = '2023-01-01'
end_date = '2023-10-01'

# Fetch the stock data
data = {}
for company in companies:
    data[company] = yf.download(company, start=start_date, end=end_date)

# Plot the stock data
plt.figure(figsize=(14, 7))
for company in companies:
    plt.plot(data[company].index, data[company]['Close'], label=company)

# Set plot title and labels
plt.title('Stock Price Change from Jan 2023 to Oct 2023')
plt.xlabel('Date')
plt.ylabel('Stock Price (USD)')
plt.legend()

# Save the plot
plt.savefig('stock_price_change.png')
plt.show()