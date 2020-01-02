class Problem: 
    customers = [] 

    def __init__(self, customers, solution=None): 
        self.customers = customers
        self.solution = solution 
    
    def generate(self):
        if self.solution != None: 
            drones = self.solution.drones 
        else: 
            print("Add solution to derive a problem ")
        allTrips = self.solution.getAllTrips()
        print(allTrips)
