import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

st.set_page_config(layout="wide", page_title="Momentum Screener")
st.title("Top Momentum Stocks")

if not os.path.exists("top100_history.csv"):
  st.warning(
      "Data has not generated yet. Trigger the workflow in your GitHub Actions"
      " tab first!"
  )
  st.stop()

# Load screened data
history = pd.read_csv("top100_history.csv")
summary = pd.read_csv("top100_list.csv")
tickers = summary["ticker"].tolist()

# Pagination: 20 charts per page to maintain fluid responsiveness
page = st.selectbox(
    "Viewing Batch",
    [
        "Rank 1 - 20",
        "Rank 21 - 40",
        "Rank 41 - 60",
        "Rank 61 - 80",
        "Rank 81 - 100",
    ],
)
start_idx = [
    "Rank 1 - 20",
    "Rank 21 - 40",
    "Rank 41 - 60",
    "Rank 61 - 80",
    "Rank 81 - 100",
].index(page) * 20
active_tickers = tickers[start_idx : start_idx + 20]


def render_chart(df_sub, ticker_symbol, return_val):
  # Calculate cumulative % change from the first bar
  df_sub["pct_return"] = (
      (df_sub["Close"] - df_sub["Close"].iloc[0]) / df_sub["Close"].iloc[0]
  ) * 100
  df_sub["spy_pct"] = (
      (df_sub["SPY_Close"] - df_sub["SPY_Close"].iloc[0])
      / df_sub["SPY_Close"].iloc[0]
  ) * 100

  fig = make_subplots(specs=[[{"secondary_y": True}]])

  # 1. Grey Volume Bars
  fig.add_trace(
      go.Bar(
          x=df_sub["Date"],
          y=df_sub["Volume"],
          marker_color="rgba(140, 140, 140, 0.35)",
          name="Volume",
          showlegend=False,
      ),
      secondary_y=True,
  )

  # 2. Benchmark (SPY) Baseline
  fig.add_trace(
      go.Scatter(
          x=df_sub["Date"],
          y=df_sub["spy_pct"],
          mode="lines",
          line=dict(color="rgba(160, 160, 160, 0.45)", width=4),
          name="SPY Trend",
          showlegend=False,
      ),
      secondary_y=False,
  )

  # 3. Yellow Performance Curve
  fig.add_trace(
      go.Scatter(
          x=df_sub["Date"],
          y=df_sub["pct_return"],
          mode="lines+markers",
          line=dict(color="#ffe600", width=2),
          marker=dict(size=4, color="#ffe600"),
          name=ticker_symbol,
          showlegend=False,
      ),
      secondary_y=False,
  )

  # Styling matching your dark mode visual
  fig.update_layout(
      template="plotly_dark",
      plot_bgcolor="#050505",
      paper_bgcolor="#050505",
      margin=dict(l=35, r=15, t=30, b=25),
      height=280,
      title=dict(
          text=f"<b>{ticker_symbol} (+{return_val:.1f}%)</b>",
          font=dict(size=14, color="#ffffff"),
          x=0.03,
          y=0.92,
      ),
      xaxis=dict(
          showgrid=False,
          tickformat="%m/%d",
          tickangle=-45,
          tickfont=dict(size=9, color="#777"),
      ),
      yaxis=dict(
          ticksuffix="%",
          showgrid=True,
          gridcolor="#1f1f1f",
          zeroline=True,
          zerolinecolor="#333",
          tickfont=dict(size=9, color="#777"),
      ),
      yaxis2=dict(
          showgrid=False,
          showticklabels=False,
          range=[0, df_sub["Volume"].max() * 2.8],
      ),
  )
  return fig


# Render 2 charts side-by-side
cols = st.columns(2)
for i, ticker in enumerate(active_tickers):
  col = cols[i % 2]
  sub_df = history[history["Ticker"] == ticker].sort_values("Date")
  ret = summary[summary["ticker"] == ticker]["return_60d"].values[0]
  col.plotly_chart(
      render_chart(sub_df, ticker, ret),
      use_container_width=True,
      theme=None,
  )
