# portfolio_server
config.py -> api key

VAR

    SOCKET = "wss://stream.binance.com:9443/ws/xrpusdt@kline_1m"
    TRADE_SYMBOL = 'XRPUSDT'
    TRADE_QUANTITY = 20

COMMAND

    python3 bot.py


IMPORT

  pip install python-binance (https://python-binance.readthedocs.io/en/latest/index.html)
              websocket
              json
              aiofiles 
              pandas (https://pandas.pydata.org/pandas-docs/stable/getting_started/install.html)
              asyncio
