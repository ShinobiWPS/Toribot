
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

"""
0.18065 | 0.18090 """
""" BID
order cost= set_price * amount //// 18.065 euro
orde fee = (Limit order cost)/100 * 0.5 ///  0.09033
oder expanse = order cost + Order Fee // 18.15533


ASK
order value = 18.09 euro
order fee = 0.09045
18.09 - 0.09 = 18.00
 """
