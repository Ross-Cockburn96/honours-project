#list of deliveries
class Trip: 

    #can be instantiated with a list 
    def __init__(self, *args):
        self.deliveries = list(args)
        print(len(self.deliveries))
        if len(self.deliveries) > 1:
            self.deliveries[0].nextDelivery = self.deliveries[1] #first node 
            #forms a linked list with the deliveries in the trip
            #excludes first and last values of deliveries list
            for idx in range(1,len(self.deliveries) -1):
                print(f"linking node {self.deliveries[idx].node.id}")
                self.deliveries[idx].prevDelivery = self.deliveries[idx-1]
                self.deliveries[idx].nextDelivery = self.deliveries[idx+1]
            self.deliveries[len(self.deliveries)-1].prevDelivery = self.deliveries[len(self.deliveries)-2]


    def addDelivery(self, delivery):
        self.deliveries.append(delivery)

    #used for printing an individual Trip object
    def __str__(self):
        return(str(self.deliveries))
    
    #used for when printing a list of trip objects
    def __repr__(self):
        return(str(self.deliveries))
    