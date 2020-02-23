

maxDrones = 10
droneSpeed = 10 #m/s
batteryCharge = 3600 #seconds - 1 hour of travel  





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

seed = None #seed is None unless set otherwise 