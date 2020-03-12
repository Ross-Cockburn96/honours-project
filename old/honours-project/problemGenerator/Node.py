import random



class Node:
    xCoord = None
    yCoord = None 

    def random(self, minVal, maxVal): 
        self.xCoord = random.randint(minVal, maxVal)
        self.yCoord = random.randint(minVal, maxVal)

    @classmethod
    def deepCopy(cls,node1, node2):
        node2.xCoord = node1.xCoord
        node2.yCoord = node1.yCoord

    def str(self):
        return (self.xCoord, self.yCoord)    