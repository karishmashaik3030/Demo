# In-memory order list
orders = []

def get_order_info():
    return orders

def create_order(data):
    order_id = len(orders) + 1
    data["order_id"] = order_id
    orders.append(data)
    return {
        "message": "Order placed successfully",
        "order": data
    }
