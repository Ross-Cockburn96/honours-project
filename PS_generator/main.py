
import parameters
import random
from drone import Drone 
from trip import Trip
from delivery import Delivery

customers = [] #each customer has a demand of 1 package 



def solutionGenerator():
    numOfTrips = random.randint(1,parameters.customers)
    numOfDrones = random.randint(1, numOfTrips)
    trips = [Trip(customers.pop(random.randrange(len(customers)))) for _ in range(numOfTrips)] #ensure that each trip has at least one delviery 
    

    for customer in customers: 
        trip = trips[random.randrange(numOfTrips)]
        trip.addDelivery(customer)

    drones = [Drone(trips.pop(random.randrange(len(trips)))) for _ in range(numOfDrones)] #ensure that each drone has at least one trip
    
    for trip in trips: 
        drone = drones[random.randrange(numOfDrones)]
        drone.addTrip(trip)

    for drone in drones: 
        minimumDeliveryTime = 100 
        for trip in drone.trips:
            for delivery in trip.deliveries:
                minimumDeliveryTime = random.randrange(minimumDeliveryTime, 10000)
                delivery.time = minimumDeliveryTime

    for idx, drone in enumerate(drones): 
        print(f"Drone No. {idx}: {drone}")
  
    
   



def populateCustomers():
    #populates list of customers with the deliveries that will satisfy their demands 
    for idx in range(parameters.customers):
        customers.append(Delivery(idx))

if __name__ == "__main__":
    print("Populating Customers...")
    populateCustomers()
    print("Generating Solution...")
    solutionGenerator()

    