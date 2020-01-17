#list of deliveries
class Trip: 

    #can be instantiated with a list 
    def __init__(self, *args):
        self.deliveries = list(args)

    def addDelivery(self, delivery):
        self.deliveries.append(delivery)

    #used for printing an individual Trip object
    def __str__(self):
        return(str(self.deliveries))
    
    #used for when printing a list of trip objects
    def __repr__(self):
        return(str(self.deliveries))
    