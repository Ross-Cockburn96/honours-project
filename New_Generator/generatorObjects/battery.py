import parameters

class Battery:
    idCounter = 1 #increments by one each time a battery class is created
    def __init__(self): 
        self.id = Battery.idCounter
        Battery.idCounter += 1
        self.batteryDistance = parameters.batteryDistance #distance left on battery
    
    def __repr__(self): 
        return str(self)
    
    def __str__(self):
        return str(self.id)