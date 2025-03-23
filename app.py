import streamlit as st
import pandas as pd
import ccxt
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# IMPORTANT : Appeler set_page_config en premier
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

st.title("📊 Dashboard Trading - Crypto, Stocks & Stratégies")

# --- Sélection du type d'actif ---
asset_type = st.sidebar.selectbox("Choisissez le type d'actif", ["Crypto", "Stocks"])

if asset_type == "Stocks":
    start_date = st.sidebar.date_input("Date de début", datetime.now() - timedelta(days=180))
    end_date = st.sidebar.date_input("Date de fin", datetime.now())
else:
    timeframe = st.sidebar.selectbox("Timeframe", ["1m", "5m", "15m", "1h", "4h", "1d"], index=3)

# ============================= SECTION CRYPTO =============================
if asset_type == "Crypto":
    st.header("Crypto")
    crypto_choice = st.sidebar.selectbox("Choisissez la crypto", ["Bitcoin (BTC)", "Ethereum (ETH)"])
    symbol = "BTC/USDT" if crypto_choice == "Bitcoin (BTC)" else "ETH/USDT"
    
    st.subheader(f"{crypto_choice} - {timeframe}")
    
    try:
        exchange = ccxt.binance()
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe)
        df_crypto = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df_crypto['timestamp'] = pd.to_datetime(df_crypto['timestamp'], unit='ms')
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données: {e}")
        st.stop()
    
    # Calcul des indicateurs SMA pour la stratégie
    df_crypto['SMA10'] = df_crypto['close'].rolling(window=10).mean()
    df_crypto['SMA20'] = df_crypto['close'].rolling(window=20).mean()
    
    # Signal de trading sur la dernière bougie
    signal = "HOLD"
    if df_crypto['SMA10'].iloc[-1] > df_crypto['SMA20'].iloc[-1]:
        signal = "BUY"
    elif df_crypto['SMA10'].iloc[-1] < df_crypto['SMA20'].iloc[-1]:
        signal = "SELL"
    st.metric(label="Signal SMA", value=signal)
    
    # Graphique interactif avec Plotly incluant les SMA
    fig_crypto = go.Figure()
    fig_crypto.add_trace(go.Candlestick(
        x=df_crypto['timestamp'],
        open=df_crypto['open'],
        high=df_crypto['high'],
        low=df_crypto['low'],
        close=df_crypto['close'],
        name=symbol
    ))
    fig_crypto.add_trace(go.Scatter(
        x=df_crypto['timestamp'], y=df_crypto['SMA10'], mode='lines', name='SMA10'
    ))
    fig_crypto.add_trace(go.Scatter(
        x=df_crypto['timestamp'], y=df_crypto['SMA20'], mode='lines', name='SMA20'
    ))
    fig_crypto.update_layout(
        title=f"{crypto_choice} - {timeframe} Chart avec stratégie SMA",
        template="plotly_dark",
        xaxis_title="Temps",
        yaxis_title="Prix (USDT)"
    )
    st.plotly_chart(fig_crypto, use_container_width=True)
    
    st.subheader("Historique des dernières bougies")
    st.dataframe(df_crypto.tail(15))

# ============================= SECTION STOCKS =============================
else:
    st.header("Stocks")
    
    stocks = st.sidebar.multiselect(
        "Choisissez les actions",
        ["Google", "Apple", "Amazon", "Meta", "Nvidia"],
        default=["Google", "Apple"]
    )
    
    ticker_dict = {
        "Google": "GOOGL",
        "Apple": "AAPL",
        "Amazon": "AMZN",
        "Meta": "META",
        "Nvidia": "NVDA"
    }
    
    if not stocks:
        st.warning("Veuillez sélectionner au moins une action.")
        st.stop()
    
    for stock in stocks:
        ticker = ticker_dict[stock]
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
        
        # Calcul des indicateurs SMA pour la stratégie
        df_stock['SMA20'] = df_stock['Close'].rolling(window=20).mean()
        df_stock['SMA50'] = df_stock['Close'].rolling(window=50).mean()
        
        # Signal de trading sur la dernière bougie
        stock_signal = "HOLD"
        if df_stock['SMA20'].iloc[-1] > df_stock['SMA50'].iloc[-1]:
            stock_signal = "BUY"
        elif df_stock['SMA20'].iloc[-1] < df_stock['SMA50'].iloc[-1]:
            stock_signal = "SELL"
        st.metric(label="Signal SMA", value=stock_signal)
        
        # Graphique interactif avec Plotly incluant les SMA
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
            title=f"{stock} ({ticker}) - Chart avec stratégie SMA",
            template="plotly_dark",
            xaxis_title="Date",
            yaxis_title="Prix ($)"
        )
        st.plotly_chart(fig_stock, use_container_width=True)
        
        st.subheader(f"Historique des données pour {stock}")
        st.dataframe(df_stock.tail(10))
