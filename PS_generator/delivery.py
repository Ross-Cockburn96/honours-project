class Delivery:

    def __init__(self, node, time=None, weight=None):
        self.node = node
        self.time = time #milliseconds
        self.weight = weight 

    def __repr__(self):
        return (f"Node: {self.node}, Time: {self.time}, Weight: {self.weight}")

    def __str__(self):
        return (f"Node: {self.node}, Time: {self.time}")