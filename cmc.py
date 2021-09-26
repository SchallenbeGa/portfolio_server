from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

symbol_str = 'BTC,ETH,BNB,XRP'

url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
parameters = {
  'symbol': symbol_str
}
headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': '722d15d6-9ee7-4e81-95c0-c05a67c3743b',
}

session = Session()
session.headers.update(headers)

try:
  response = session.get(url, params=parameters)
  data = json.loads(response.text)
except (ConnectionError, Timeout, TooManyRedirects) as e:
  print(e)


symbol_list = symbol_str.split(',')
file_to_open = 'coinmap.txt'
line_list = []
with open(file_to_open, 'w') as this_csv_file:
	for symbol in symbol_list:
	
		price= data['data'][symbol]['quote']['USD']['price']
		line=f'{cid}, {symbol},{price}'
		line_list.append(line)

	for line in line_list:
		this_csv_file.write(line)
		this_csv_file.write('\n')
