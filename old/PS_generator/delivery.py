class Action: 
    def __init__(self, node, prevDelivery, nextDelivery,time):
        self.node = node
        self.time = time #seconds
        self.prevDelivery = prevDelivery
        self.nextDelivery = nextDelivery
    
    def __repr__(self):
        return str(self)

    def __str__(self):
        return (f"Node: {str(self.node)}, Time: {self.time}")

class Delivery(Action):
    def __init__(self, node, prevDelivery = None, nextDelivery = None, time=None, weight=None):
        self.node = node
        self.time = time #seconds
        self.weight = weight 
        self.prevDelivery = prevDelivery
        self.nextDelivery = nextDelivery

    def __repr__(self):
        return (f"Node: {str(self.node)}, Time: {self.time}, Weight: {self.weight}")

'''
Takes a RechargeNode obj as node and represents the action of the drone switching batteries at the recharge station 
'''
class ChangeBattery(Action):
    def __init__(self, node, prevDelivery = None, nextDelivery = None, time=None):
        super().__init__(node, prevDelivery, nextDelivery, time)
