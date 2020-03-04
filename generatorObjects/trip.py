class Trip:
    
    def __init__(self, *args):
        self.actions = list(args)
        self.startTime = 0 #time the trip finishes 
        if len(self.actions) > 1:
            self.actions[0].nextAction = self.actions[1] #first node 
            #forms a linked list with the actions in the trip
            #excludes first and last values of actions list
            for idx in range(1,len(self.actions) -1):
                self.actions[idx].prevAction = self.actions[idx-1]
                self.actions[idx].nextAction = self.actions[idx+1]
            self.actions[len(self.actions)-1].prevAction = self.actions[len(self.actions)-2]

    def insertAction(self, index, action):
       
        if index != 0: 
            self.actions[index-1].nextAction = action 
            action.prevAction = self.actions[index-1]
        
        if index > len(self.actions) - 1:
            self.actions[-1].nextAction = action
            action.prevAction = self.actions[-1]
        else:
            self.actions[index].prevAction = action 
            action.nextAction = self.actions[index]
        
        self.actions.insert(index, action)

    #used for printing an individual Trip object
    def __str__(self):
        return(str(self.actions))
    
    #used for when printing a list of trip objects
    def __repr__(self):
        return(str(self.actions))
    