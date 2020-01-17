

drones = 1
droneSpeed = 10 #m/s

#Since the city is essentially a grid with each cell being a 1km^2 area and node coordinates are whole numebrs, 
#the minimum distance between each node should be 1km and so the time to travel that distance is 1000/droneSpeed
minimumDeliveryTime = int(1000/droneSpeed)
customers = 10
droneCapacity = 30 #lb
droneCargoSlots = 5
#there relationship between drone speed, customers and day length that creates this constraint:
#daylength/droneSpeed * customers > customers 
#so the minimum dayLength = customers^2 * droneSpeed
dayLength = 1000

citySizeMax = 20 #km

