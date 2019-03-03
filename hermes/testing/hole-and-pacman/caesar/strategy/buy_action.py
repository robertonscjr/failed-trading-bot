    def buy_action(self, client, pair, balance): 

        self.client = client
        self.pair = pair
        self.balance = balance
	self.buy_if = None	
	self.purchase_action() 

    def purchase_action(self):
      
        if not self.buy_order():
            self.buy()
            print "(%s) - Buy order placed at %.8f : %s" % (self.pair, 
                                                           self.buy_price,
                                                             self._time())

        else:
            self.order_book = self.client.returnOrderBook(self.pair, 2)
            self.last_buy_order = float(self.order_book['bids'][0][0]) 
            
            if self.buy_price < self.last_buy_order:
                self.client.cancelOrder(self.buy_id)
                self.buy()
                print "(%s) - Last buy order updated at %.8f : %s" % \
                                                           (self.pair,
                                                  self.last_buy_order,  
                                                         self._time())

    def buy(self):
        self.buy_price = self._highest_bid() + 0.00000001
        amount = (self.balance / self.buy_price)
  
        if amount * self.buy_price <= 0.0001:
            amount = 0.00011000 / self.buy_price
                     
        self.buy_id = str(self.client.buy(self.pair, 
                                          self.buy_price, 
                                          amount)['orderNumber'])
    
    def last_buy_price(self):
        trade_history = self.client.returnTradeHistory(self.pair, 1507842000, 9999999999)

        for trade in trade_history:
            if trade['type'] == 'buy':
                return float(trade_history[0]['rate'])
    
    def buy_order(self):
	self.order_book = self.client.returnOrderBook(self.pair)
	buy_orders  = self.order_book['bids'] 

	if(len(buy_orders) > 1) return True
	else return False

    def _highest_bid(self):
        return float(self.ticker['highestBid'])
