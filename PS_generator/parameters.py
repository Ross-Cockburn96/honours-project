

drones = 1
droneSpeed = 10 #m/s

unit = 10 #represents a unit cell in the city which is a NxN grid of cells (meters)
#Since the city is essentially a grid with each cell being a 1km^2 area and node coordinates are whole numebrs, 

#the minimum distance between each node should be 1km and so the time to travel that distance is 1000/droneSpeed
minimumDeliveryTime = 1 #ensures that delivery times are not 0 (because it is impossible for a customer to be serviced at 0 seconds)
customers = 50
droneCapacity = 30 #lb
droneCargoSlots = 5
#there relationship between drone speed, customers and day length that creates this constraint:
#daylength/droneSpeed * customers > customers 
#so the minimum dayLength = customers^2 * droneSpeed
dayLength = 28800 #8 hours
citySizeMax = 20000 #meters

timeSlotStandardDev = 60 #the standard deviation used in the gaussian distribution to extract timeslot open ranges 