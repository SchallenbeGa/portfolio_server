import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.style.use('ggplot')

# Fetch the Apple stock data
data = pd.read_csv('tst.csv').set_index('Date')
data.index = pd.to_datetime(data.index)


def sma(data, n):
	sma = data.rolling(window=n).mean()
	return pd.DataFrame(sma)

n = [10,20,50]
for i in n:
	data[f'sma_{i}'] = sma(data['Close'], i)

def implement_sma_strategy(data, short_window, long_window,joker):

	sma0 = joker
	sma1 = short_window
	sma2 = long_window
	buy_price = []
	sell_price = []
	sma_signal = []
	last_signal = 0
	signal = 0

	for i in range(len(data)):
		if sma1[i] > sma2[i]:
			if signal != 1:
				buy_price.append(data[i])
				last_signal = data[i]
				sell_price.append(np.nan)
				signal = 1
				sma_signal.append(signal)
			else:
				buy_price.append(np.nan)
				sell_price.append(np.nan)
				sma_signal.append(0)
		elif sma2[i] > sma1[i]:
			if signal != -1:
				buy_price.append(np.nan)
				if(last_signal>data[i]):
					sell_price.append(np.nan)
					sma_signal.append(0)
				else:
					sell_price.append(data[i])
					signal = -1
					sma_signal.append(-1)
			else:
				buy_price.append(np.nan)
				sell_price.append(np.nan)
				sma_signal.append(0)
		else:
			buy_price.append(np.nan)
			sell_price.append(np.nan)
			sma_signal.append(0)

	return buy_price, sell_price, sma_signal

sma_10 = data['sma_10']
sma_20 = data['sma_20']
sma_50 = data['sma_50']

buy_price, sell_price, signal = implement_sma_strategy(data['Close'], sma_20, sma_10, sma_50)

plt.plot(data['Close'], alpha = 0.3, label = 'data')
plt.plot(sma_10, alpha = 0.6, label = 'SMA 10')
plt.plot(sma_20, alpha = 0.6, label = 'SMA 20')
plt.plot(sma_50, alpha = 0.6, label = 'SMA 50')
plt.scatter(data.index, buy_price, marker = '^', s = 200, color = 'darkblue', label = 'BUY SIGNAL')
plt.scatter(data.index, sell_price, marker = 'v', s = 200, color = 'crimson', label = 'SELL SIGNAL')
plt.legend(loc = 'upper left')
plt.title('data SMA CROSSOVER TRADING SIGNALS')
plt.show()