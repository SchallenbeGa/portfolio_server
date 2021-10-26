import math
import datetime
import time
import os
import json
import csv
from flask import Flask
from flask import render_template,redirect,request
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

def get_budget():
	with open('budget-example.csv', 'r') as file:
		budget = []
		reader = csv.DictReader(file)
		for row in reader:
			budget.append(row)
		print(budget)
		return dict(budget)

def save_budget(data):
	line_list=[]
	with open("budget-example.csv", 'w') as this_csv_file:
		line_list.append('name,hold,buy_price')
		for y in data:
			print(y["money"])
			line= str(y["money"])+","+str(y["quantity"])+","+str(y["buy_price"])
			line_list.append(line)
		for line in line_list:
			this_csv_file.write(line)
			this_csv_file.write('\n')

@app.route("/edit")
def edit():
	currencies = get_budget()
	trade = []
	for i,z,buy in currencies.values:
		tr = {"money":i,"quantity":z,"buy_price":buy}
		trade.append(tr)

	return render_template("edit.html",trade=trade)

@app.route('/edit',methods = ['POST'])
def save_d():

	money = request.form["money"].lower()
	buy_price = request.form['buy_price']
	quantity = request.form['quantity']

	trade = []
	for i,z,buy in currencies.values:
		if(i==money):
			i = money
			z = quantity
			buy = buy_price
		trade.append({"money":i,"quantity":z,"buy_price":buy})
	save_budget(trade)

	return redirect('edit')

@app.route('/trash',methods = ['POST'])
def trash():
	
	money = request.form["money"].lower()

	trade = []
	for i,z,buy in currencies.values:
		if(i!=money):
			trade.append({"money":i,"quantity":z,"buy_price":buy})
	save_budget(trade)	

	return redirect('edit')

@app.route('/new',methods = ['POST'])
def new():
	
	money = request.form["money"].lower()
	buy_price = request.form['buy_price']
	quantity = request.form['quantity']

	trade = []
	for i,z,buy in currencies.values:
		trade.append({"money":i,"quantity":z,"buy_price":buy})
	trade.append({"money":money,"quantity":quantity,"buy_price":buy_price})
	save_budget(trade)	

	return redirect('edit')

@app.route("/")
def home():
	print(get_budget())
	return render_template("index.html",trade=get_budget())

@app.route("/api")
def api():
	return json.dumps(get_budget())