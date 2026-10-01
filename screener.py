import pandas as pd
import yfinance as yf

# 1. Broad US market watchlist (major active common equities)
# To keep runtime well under 5 minutes, we pull the S&P 500 + liquid mid-caps
sp500_url = (
    "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
)
try:
  tickers = pd.read_csv(sp500_url)["Symbol"].str.replace(".", "-").tolist()
except Exception:
  tickers = [
      "AAPL",
      "MSFT",
      "NVDA",
      "AMZN",
      "GOOGL",
      "META",
      "TSLA",
      "AMD",
      "AVGO",
      "NFLX",
  ]

# Add SPY benchmark for the chart trendline
tickers_to_pull = list(set(tickers + ["SPY"]))

# 2. Download the last 60 trading days (3 months) in one batch
print("Downloading market data...")
data = yf.download(
    tickers_to_pull, period="3mo", interval="1d", group_by="ticker"
)

# 3. Screen for stocks up > +10% over the last 60 trading bars
qualified = []
for t in tickers:
  try:
    sub = data[t].dropna()
    if len(sub) >= 40:  # Ensure sufficient trading history
      start_price = sub["Close"].iloc[0]
      current_price = sub["Close"].iloc[-1]
      ret_60d = ((current_price - start_price) / start_price) * 100

      if ret_60d >= 10.0:
        qualified.append({
            "ticker": t,
            "return_60d": ret_60d,
            "current_price": current_price,
        })
  except Exception:
    continue

# 4. Rank and take Top 100 momentum winners
df_qualified = (
    pd.DataFrame(qualified)
    .sort_values(by="return_60d", ascending=False)
    .head(100)
)
top_tickers = df_qualified["ticker"].tolist()

# 5. Export daily history for the top 100 + SPY for charting
records = []
dates = data["SPY"].dropna().index

for d in dates:
  # Grab benchmark (SPY) close
  spy_close = (
      data["SPY"].loc[d]["Close"] if d in data["SPY"].index else float("nan")
  )

  for t in top_tickers:
    if t in data and d in data[t].index:
      row = data[t].loc[d]
      records.append({
          "Date": d.strftime("%Y-%m-%d"),
          "Ticker": t,
          "Close": float(row["Close"]),
          "Volume": int(row["Volume"]),
          "SPY_Close": float(spy_close),
      })

output_df = pd.DataFrame(records)
output_df.to_csv("top100_history.csv", index=False)
df_qualified.to_csv("top100_list.csv", index=False)
print("Screen complete. Saved top100_history.csv")
