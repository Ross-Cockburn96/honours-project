#there relationship between drone speed, customers and day length that creates this constraint:
#daylength/droneSpeed * customers > customers 
#so the minimum dayLength = customers^2 * droneSpeed

drones = 1
droneSpeed = 10 #m/s
customers = 10
droneCapacity = 30
dayLength = 1000
citySizeMax = 20 #km

