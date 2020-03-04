import new_generator.parameters as parameters

class Battery:
    idCounter = 1 #increments by one each time a battery class is created

    def __init__(self, batteryID): 
        self.id = batteryID
        self.batteryDistance = parameters.batteryDistance #distance left on battery
    
    #use for problem and solution generation 
    @classmethod
    def createNew(cls):
        objectID = Battery.idCounter
        cls.idCounter += 1
        return cls(objectID)

    #use for evaluator to build a drone with a specific id 
    @classmethod
    def createWithID(cls, id):
        objectID = int(id)
        return cls(objectID)

    def __repr__(self): 
        return str(self)
    
    def __str__(self):
        return str(self.id)