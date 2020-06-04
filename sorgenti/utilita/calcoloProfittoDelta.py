
buy_price = float(0.18065)
amount=float(100.00000000)

#delta for profit
delta = float(0.00182) #e' circa il 1.05% del buy_price
# XRPdelta = float(0.00182)

#buy/bid

cost= buy_price * amount
buy_fee = (cost/100) * 0.5
buy_expanse = cost + buy_fee




#sell/ask
sell_price = buy_price+delta
income = sell_price*amount
sell_fee= (income/100)*0.5
sell_expanse=income-sell_fee


profit=round(sell_expanse-buy_expanse, 5)
print(profit)
