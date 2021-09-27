import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.style.use('ggplot')

# Fetch the Apple stock data
data = pd.read_csv('tst.csv').set_index('Date')
data.index = pd.to_datetime(data.index)

def sma(data, n):
    sma = data.rolling(window = n).mean()
    return pd.DataFrame(sma)

n = [20, 50]
for i in n:
    data[f'sma_{i}'] = sma(data['Close'], i)
    
plt.plot(data['Close'], label = 'data', linewidth = 5, alpha = 0.3)
plt.plot(data['sma_20'], label = 'SMA 20')
plt.plot(data['sma_50'], label = 'SMA 50')
plt.title('sma (20, 50)')
plt.show()