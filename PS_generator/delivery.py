class Delivery:

    def __init__(self, node, prevDelivery = None, nextDelivery = None, time=None, weight=None):
        self.node = node
        self.time = time #seconds
        self.weight = weight 
        self.prevDelivery = prevDelivery
        self.nextDelivery = nextDelivery

    def __repr__(self):
        return (f"Node: {str(self.node)}, Time: {self.time}, Weight: {self.weight}")

    def __str__(self):

        return (f"Node: {str(self.node)}, Time: {self.time}")