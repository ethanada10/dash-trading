import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- Configurer la page ---
st.set_page_config(page_title="Dashboard Trading", layout="wide")

# --- Auto-refresh automatique à 20h ---
now = datetime.now()
target = now.replace(hour=20, minute=0, second=0, microsecond=0)
if now > target:
    target += timedelta(days=1)
delay_ms = int((target - now).total_seconds() * 1000)
st.components.v1.html(
    f"""
    <script>
    setTimeout(function() {{
       window.location.reload();
    }}, {delay_ms});
    </script>
    """,
    height=0,
)

# --- Thème sombre complet (fond noir) ---
st.markdown(
    """
    <style>
    /* Fond de l'application */
    [data-testid="stAppViewContainer"] {
        background-color: #000000;
        color: #ffffff;
    }
    /* Fond de la sidebar */
    [data-testid="stSidebar"] {
        background-color: #1a1a1a;
        color: #ffffff;
    }
    /* Boutons */
    .stButton>button {
        background-color: #444444;
        color: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📊 Dashboard Trading - Stocks, Forex, Matières Premières & Or")

# --- Sélection du type d'actif ---
asset_type = st.sidebar.selectbox("Choisissez le type d'actif", 
                                  ["Stocks", "Forex", "Matières Premières", "Or"])

# --- Date de début et fin pour tous les actifs ---
start_date = st.sidebar.date_input("Date de début", datetime.now() - timedelta(days=180))
end_date = st.sidebar.date_input("Date de fin", datetime.now())

# Fonction de calcul du MACD
def calcul_macd(df, col='Close'):
    ema12 = df[col].ewm(span=12, adjust=False).mean()
    ema26 = df[col].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['Histogram'] = df['MACD'] - df['Signal']
    return df

# ===================================================================
# ============================= SECTION STOCKS ======================
# ===================================================================
if asset_type == "Stocks":
    st.header("Stocks - Top 100 entreprises mondiales")
    # Liste des 100 plus grosses entreprises (exemple)
    top_100_stocks = {
        "Apple": "AAPL", "Microsoft": "MSFT", "Amazon": "AMZN", "Alphabet": "GOOGL", "Meta": "META",
        "Tesla": "TSLA", "Berkshire Hathaway": "BRK-B", "NVIDIA": "NVDA", "JPMorgan Chase": "JPM", "Johnson & Johnson": "JNJ",
        "Visa": "V", "Procter & Gamble": "PG", "Mastercard": "MA", "Home Depot": "HD", "Bank of America": "BAC",
        "Walt Disney": "DIS", "Adobe": "ADBE", "Verizon": "VZ", "Comcast": "CMCSA", "Exxon Mobil": "XOM",
        "Coca-Cola": "KO", "PepsiCo": "PEP", "Pfizer": "PFE", "Oracle": "ORCL", "Intel": "INTC",
        "Cisco": "CSCO", "Merck": "MRK", "Abbott Laboratories": "ABT", "Chevron": "CVX", "Salesforce": "CRM",
        "McDonald's": "MCD", "Broadcom": "AVGO", "AT&T": "T", "Netflix": "NFLX", "Costco": "COST",
        "PayPal": "PYPL", "Amgen": "AMGN", "T-Mobile": "TMUS", "Qualcomm": "QCOM", "IBM": "IBM",
        "Union Pacific": "UNP", "Boeing": "BA", "Citigroup": "C", "Goldman Sachs": "GS", "Morgan Stanley": "MS",
        "Wells Fargo": "WFC", "American Express": "AXP", "3M": "MMM", "Caterpillar": "CAT", "General Electric": "GE",
        "Honeywell": "HON", "Lockheed Martin": "LMT", "Dow": "DOW", "Raytheon Technologies": "RTX", "Nike": "NKE",
        "Starbucks": "SBUX", "Booking Holdings": "BKNG", "Gilead Sciences": "GILD", "Intuit": "INTU", "S&P Global": "SPGI",
        "Schlumberger": "SLB", "Exelon": "EXC", "CME Group": "CME", "Eli Lilly": "LLY", "NextEra Energy": "NEE",
        "Southern Company": "SO", "Dominion Energy": "D", "Sempra Energy": "SRE", "Kinder Morgan": "KMI", "Phillips 66": "PSX",
        "Marathon Petroleum": "MPC", "ConocoPhillips": "COP", "Occidental Petroleum": "OXY", "Halliburton": "HAL", "Valero Energy": "VLO",
        "Archer Daniels Midland": "ADM", "DuPont de Nemours": "DD", "Colgate-Palmolive": "CL", "Mondelez International": "MDLZ",
        "General Motors": "GM", "Ford": "F", "CVS Health": "CVS", "UnitedHealth Group": "UNH", "Anthem": "ANTM",
        "Cigna": "CI", "Medtronic": "MDT", "Bristol Myers Squibb": "BMY", "Danaher": "DHR", "Amphenol": "APH",
        "Texas Instruments": "TXN", "Applied Materials": "AMAT", "Lam Research": "LRCX", "Micron Technology": "MU", "Advanced Micro Devices": "AMD",
        "Uber": "UBER", "Lyft": "LYFT", "Square": "SQ", "Dropbox": "DBX", "Zscaler": "ZS", "Workday": "WDAY"
    }
    
    stocks_selected = st.sidebar.multiselect(
        "Sélectionnez les actions", list(top_100_stocks.keys()), default=list(top_100_stocks.keys())[:2]
    )
    
    if not stocks_selected:
        st.warning("Veuillez sélectionner au moins une action.")
        st.stop()
    
    for stock in stocks_selected:
        ticker = top_100_stocks[stock]
        st.subheader(f"{stock} ({ticker})")
        
        try:
            df_stock = yf.download(ticker, start=start_date, end=end_date)
            df_stock.reset_index(inplace=True)
        except Exception as e:
            st.error(f"Erreur pour {stock} : {e}")
            continue
        
        if df_stock.empty:
            st.error(f"Aucune donnée trouvée pour {stock}")
            continue
        
        # Calcul des moyennes mobiles
        df_stock['SMA20'] = df_stock['Close'].rolling(window=20).mean()
        df_stock['SMA50'] = df_stock['Close'].rolling(window=50).mean()
        
        # Calcul du MACD
        df_stock = calcul_macd(df_stock, col='Close')
        
        # Signal de trading basé sur les SMA
        stock_signal = "HOLD"
        if df_stock['SMA20'].iloc[-1] > df_stock['SMA50'].iloc[-1]:
            stock_signal = "BUY"
        elif df_stock['SMA20'].iloc[-1] < df_stock['SMA50'].iloc[-1]:
            stock_signal = "SELL"
        st.metric(label="Signal SMA", value=stock_signal)
        
        # Graphique principal : chandeliers + SMA
        fig_stock = go.Figure()
        fig_stock.add_trace(go.Candlestick(
            x=df_stock['Date'],
            open=df_stock['Open'],
            high=df_stock['High'],
            low=df_stock['Low'],
            close=df_stock['Close'],
            name=ticker
        ))
        fig_stock.add_trace(go.Scatter(
            x=df_stock['Date'], y=df_stock['SMA20'], mode='lines', name='SMA20'
        ))
        fig_stock.add_trace(go.Scatter(
            x=df_stock['Date'], y=df_stock['SMA50'], mode='lines', name='SMA50'
        ))
        fig_stock.update_layout(
            title=f"{stock} ({ticker}) - Chart avec SMA",
            template="plotly_dark",
            xaxis_title="Date",
            yaxis_title="Prix ($)"
        )
        st.plotly_chart(fig_stock, use_container_width=True)
        
        # Graphique MACD
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(
            x=df_stock['Date'], y=df_stock['MACD'], mode='lines', name='MACD'
        ))
        fig_macd.add_trace(go.Scatter(
            x=df_stock['Date'], y=df_stock['Signal'], mode='lines', name='Signal'
        ))
        fig_macd.add_trace(go.Bar(
            x=df_stock['Date'], y=df_stock['Histogram'], name='Histogram'
        ))
        fig_macd.update_layout(
            title="MACD",
            template="plotly_dark",
            xaxis_title="Date",
            yaxis_title="MACD"
        )
        st.plotly_chart(fig_macd, use_container_width=True)
        
        st.subheader(f"Historique des données pour {stock}")
        st.dataframe(df_stock.tail(10))

# ===================================================================
# ============================= SECTION FOREX =======================
# ===================================================================
elif asset_type == "Forex":
    st.header("Forex")
    forex_pairs = {
        "EUR/USD": "EURUSD=X",
        "GBP/USD": "GBPUSD=X",
        "USD/JPY": "USDJPY=X",
        "AUD/USD": "AUDUSD=X",
        "USD/CAD": "USDCAD=X",
        "USD/CHF": "USDCHF=X",
        "NZD/USD": "NZDUSD=X"
    }
    pair_selected = st.sidebar.selectbox("Sélectionnez la paire de devises", list(forex_pairs.keys()))
    ticker = forex_pairs[pair_selected]
    
    st.subheader(f"{pair_selected}")
    try:
        df_forex = yf.download(ticker, start=start_date, end=end_date)
        df_forex.reset_index(inplace=True)
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données: {e}")
        st.stop()
        
    if df_forex.empty:
        st.error("Aucune donnée trouvée.")
    else:
        # Moyennes mobiles
        df_forex['SMA10'] = df_forex['Close'].rolling(window=10).mean()
        df_forex['SMA20'] = df_forex['Close'].rolling(window=20).mean()
        
        # MACD
        df_forex = calcul_macd(df_forex, col='Close')
        
        # Signal SMA
        forex_signal = "HOLD"
        if df_forex['SMA10'].iloc[-1] > df_forex['SMA20'].iloc[-1]:
            forex_signal = "BUY"
        elif df_forex['SMA10'].iloc[-1] < df_forex['SMA20'].iloc[-1]:
            forex_signal = "SELL"
        st.metric(label="Signal SMA", value=forex_signal)
        
        # Graphique principal : chandeliers + SMA
        fig_forex = go.Figure()
        fig_forex.add_trace(go.Candlestick(
            x=df_forex['Date'],
            open=df_forex['Open'],
            high=df_forex['High'],
            low=df_forex['Low'],
            close=df_forex['Close'],
            name=ticker
        ))
        fig_forex.add_trace(go.Scatter(
            x=df_forex['Date'], y=df_forex['SMA10'], mode='lines', name='SMA10'
        ))
        fig_forex.add_trace(go.Scatter(
            x=df_forex['Date'], y=df_forex['SMA20'], mode='lines', name='SMA20'
        ))
        fig_forex.update_layout(
            title=f"{pair_selected} - Chart avec SMA",
            template="plotly_dark",
            xaxis_title="Date",
            yaxis_title="Prix"
        )
        st.plotly_chart(fig_forex, use_container_width=True)
        
        # Graphique MACD
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(
            x=df_forex['Date'], y=df_forex['MACD'], mode='lines', name='MACD'
        ))
        fig_macd.add_trace(go.Scatter(
            x=df_forex['Date'], y=df_forex['Signal'], mode='lines', name='Signal'
        ))
        fig_macd.add_trace(go.Bar(
            x=df_forex['Date'], y=df_forex['Histogram'], name='Histogram'
        ))
        fig_macd.update_layout(
            title="MACD",
            template="plotly_dark",
            xaxis_title="Date",
            yaxis_title="MACD"
        )
        st.plotly_chart(fig_macd, use_container_width=True)
        
        st.subheader("Historique des dernières bougies")
        st.dataframe(df_forex.tail(15))

# ===================================================================
# ====================== SECTION MATIÈRES PREMIÈRES ==================
# ===================================================================
elif asset_type == "Matières Premières":
    st.header("Matières Premières")
    commodities_dict = {
        "Crude Oil": "CL=F",
        "Natural Gas": "NG=F",
        "Copper": "HG=F",
        "Silver": "SI=F",
        "Platinum": "PL=F",
        "Palladium": "PA=F"
    }
    commodities_selected = st.sidebar.multiselect(
        "Sélectionnez les matières premières", list(commodities_dict.keys()), default=["Crude Oil", "Copper"]
    )
    
    if not commodities_selected:
        st.warning("Veuillez sélectionner au moins une matière première.")
        st.stop()
    
    for commodity in commodities_selected:
        ticker = commodities_dict[commodity]
        st.subheader(f"{commodity} ({ticker})")
        try:
            df_comm = yf.download(ticker, start=start_date, end=end_date)
            df_comm.reset_index(inplace=True)
        except Exception as e:
            st.error(f"Erreur pour {commodity} : {e}")
            continue
        
        if df_comm.empty:
            st.error(f"Aucune donnée trouvée pour {commodity}")
            continue
        
        # Moyennes mobiles
        df_comm['SMA20'] = df_comm['Close'].rolling(window=20).mean()
        df_comm['SMA50'] = df_comm['Close'].rolling(window=50).mean()
        
        # MACD
        df_comm = calcul_macd(df_comm, col='Close')
        
        # Signal SMA
        comm_signal = "HOLD"
        if df_comm['SMA20'].iloc[-1] > df_comm['SMA50'].iloc[-1]:
            comm_signal = "BUY"
        elif df_comm['SMA20'].iloc[-1] < df_comm['SMA50'].iloc[-1]:
            comm_signal = "SELL"
        st.metric(label="Signal SMA", value=comm_signal)
        
        # Graphique principal : chandeliers + SMA
        fig_comm = go.Figure()
        fig_comm.add_trace(go.Candlestick(
            x=df_comm['Date'],
            open=df_comm['Open'],
            high=df_comm['High'],
            low=df_comm['Low'],
            close=df_comm['Close'],
            name=ticker
        ))
        fig_comm.add_trace(go.Scatter(
            x=df_comm['Date'], y=df_comm['SMA20'], mode='lines', name='SMA20'
        ))
        fig_comm.add_trace(go.Scatter(
            x=df_comm['Date'], y=df_comm['SMA50'], mode='lines', name='SMA50'
        ))
        fig_comm.update_layout(
            title=f"{commodity} ({ticker}) - Chart avec SMA",
            template="plotly_dark",
            xaxis_title="Date",
            yaxis_title="Prix"
        )
        st.plotly_chart(fig_comm, use_container_width=True)
        
        # Graphique MACD
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(
            x=df_comm['Date'], y=df_comm['MACD'], mode='lines', name='MACD'
        ))
        fig_macd.add_trace(go.Scatter(
            x=df_comm['Date'], y=df_comm['Signal'], mode='lines', name='Signal'
        ))
        fig_macd.add_trace(go.Bar(
            x=df_comm['Date'], y=df_comm['Histogram'], name='Histogram'
        ))
        fig_macd.update_layout(
            title="MACD",
            template="plotly_dark",
            xaxis_title="Date",
            yaxis_title="MACD"
        )
        st.plotly_chart(fig_macd, use_container_width=True)
        
        st.subheader(f"Historique des données pour {commodity}")
        st.dataframe(df_comm.tail(10))

# ===================================================================
# ============================== SECTION OR ==========================
# ===================================================================
elif asset_type == "Or":
    st.header("Or")
    ticker = "XAUUSD=X"  # Ticker pour l'or (spot)
    st.subheader("Gold (XAU/USD)")
    try:
        df_gold = yf.download(ticker, start=start_date, end=end_date)
        df_gold.reset_index(inplace=True)
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données: {e}")
        st.stop()
        
    if df_gold.empty:
        st.error("Aucune donnée trouvée.")
    else:
        # Moyennes mobiles
        df_gold['SMA20'] = df_gold['Close'].rolling(window=20).mean()
        df_gold['SMA50'] = df_gold['Close'].rolling(window=50).mean()
        
        # MACD
        df_gold = calcul_macd(df_gold, col='Close')
        
        # Signal SMA
        gold_signal = "HOLD"
        if df_gold['SMA20'].iloc[-1] > df_gold['SMA50'].iloc[-1]:
            gold_signal = "BUY"
        elif df_gold['SMA20'].iloc[-1] < df_gold['SMA50'].iloc[-1]:
            gold_signal = "SELL"
        st.metric(label="Signal SMA", value=gold_signal)
        
        # Graphique principal : chandeliers + SMA
        fig_gold = go.Figure()
        fig_gold.add_trace(go.Candlestick(
            x=df_gold['Date'],
            open=df_gold['Open'],
            high=df_gold['High'],
            low=df_gold['Low'],
            close=df_gold['Close'],
            name=ticker
        ))
        fig_gold.add_trace(go.Scatter(
            x=df_gold['Date'], y=df_gold['SMA20'], mode='lines', name='SMA20'
        ))
        fig_gold.add_trace(go.Scatter(
            x=df_gold['Date'], y=df_gold['SMA50'], mode='lines', name='SMA50'
        ))
        fig_gold.update_layout(
            title="Gold (XAU/USD) - Chart avec SMA",
            template="plotly_dark",
            xaxis_title="Date",
            yaxis_title="Prix"
        )
        st.plotly_chart(fig_gold, use_container_width=True)
        
        # Graphique MACD
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(
            x=df_gold['Date'], y=df_gold['MACD'], mode='lines', name='MACD'
        ))
        fig_macd.add_trace(go.Scatter(
            x=df_gold['Date'], y=df_gold['Signal'], mode='lines', name='Signal'
        ))
        fig_macd.add_trace(go.Bar(
            x=df_gold['Date'], y=df_gold['Histogram'], name='Histogram'
        ))
        fig_macd.update_layout(
            title="MACD",
            template="plotly_dark",
            xaxis_title="Date",
            yaxis_title="MACD"
        )
        st.plotly_chart(fig_macd, use_container_width=True)
        
        st.subheader("Historique des dernières bougies")
        st.dataframe(df_gold.tail(15))
