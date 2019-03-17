**Hole Strategy.**

A brief description about hole strategy.

**Attributes:**
    client: Exchange client.
    pair: Pair of coins. Ex: BTC_ETH .
    buy_order: If buy order was placed or not.
    sell_order: If sell order was placed or not.
    bought: If buy order was executed or not.
    sold: If sell order was executed or not.
    buy_price: The buy price in the moment order was placed.
    sell_price: The sell price in the moment order was placed.
    desired_hole: The desired percentage of hole.
    have_hole: If have a hole or not.
    buy_id: The order number of buy.
    sell_id: The order number of sell.
    first_coin: The first coin of pair.
    second_coin: The second coin of pair.
    last_buy_order: The value of last buy order.
    last_sell_order: The value of last sell order.

**Methods:**
    run: Operation starts.
    purchase_action: The actions of purchase.
    sale_action: The actions of sale.
    update: Update all values with Exchange data.
