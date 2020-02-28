class Trip:
    
    def __init__(self, *args):
        self.actions = list(args)
        self.startTime = 0 #time the trip finishes 
        if len(self.actions) > 1:
            self.actions[0].nextDelivery = self.actions[1] #first node 
            #forms a linked list with the actions in the trip
            #excludes first and last values of actions list
            for idx in range(1,len(self.actions) -1):
                self.actions[idx].prevDelivery = self.actions[idx-1]
                self.actions[idx].nextDelivery = self.actions[idx+1]
            self.actions[len(self.actions)-1].prevDelivery = self.actions[len(self.actions)-2]

    def addAction(self, action):
        self.actions.append(actions)

    #used for printing an individual Trip object
    def __str__(self):
        return(str(self.actions))
    
    #used for when printing a list of trip objects
    def __repr__(self):
        return(str(self.actions))
    