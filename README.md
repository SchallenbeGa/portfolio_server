# AUTOMATE BINANCE BUY/SELL

CONFIG.PY

    API_KEY = '39ymxuizXkwZNpM7zkYOfGIbYX3zYwhyapW5EnoFRpLZ23H27ACks51Ll2IVWHhH'
    API_SECRET = 'yourbinanceapisecret'

VAR

    SOCKET = "wss://stream.binance.com:9443/ws/xrpusdt@kline_1m"
    TRADE_SYMBOL = 'XRPUSDT'
    TRADE_QUANTITY = 20

COMMAND

    python3 bot.py


IMPORT

      pip install python-binance (https://python-binance.readthedocs.io/en/latest/index.html)
      pip install websocket
      pip install json
      pip install aiofiles 
      pip install pandas (https://pandas.pydata.org/pandas-docs/stable/getting_started/install.html)
      pip install asyncio
