class Package:
    def __init__(self, id):
        self.id = id 
        self.weight = None
        self.destination = None

    def __repr__(self):
        return str(self)
    
    def __str__(self):
        return f"{self.id},{self.weight}"
