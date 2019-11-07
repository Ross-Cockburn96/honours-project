class Node:
    def __init__(self, xCoord, yCoord):
        self.xCoord = xCoord
        self.yCoord = yCoord

    def str(self):
        return (self.xCoord, self.yCoord)     