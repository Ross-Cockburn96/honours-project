class Package:
    def __init__(self, id):
        self.id = id 
        self.weight = None

    def __repr__(self):
        return str(self)
    
    def __str__(self):
        return str((self.id, self.weight))