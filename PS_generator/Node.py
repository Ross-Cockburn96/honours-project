import random



class Node:
    xCoord = 0
    yCoord = 0 
    openTime = 0 
    closeTime = 0
    def __init__(self, id):
        self.id = id

    def random(self, minVal, maxVal): 
        self.xCoord = random.randint(minVal, maxVal)
        self.yCoord = random.randint(minVal, maxVal)

    @classmethod
    def deepCopy(cls,node1, node2):
        node2.xCoord = node1.xCoord
        node2.yCoord = node1.yCoord

    def __str__(self):
        return (f"{self.xCoord}, {self.yCoord}, {self.openTime}, {self.closeTime}")

        