from generatorObjects.node import Depot, Node


def countUniquePackagesDelivered(drones):
    packages = [] 

    #create a list of all packages delivered in the solution
    for drone in drones:
        for action in drone.getAllActions():
            if "Delivery" in str(type(action)):
                packages.append(action.package.id)
    return len(set(packages))

def checkCustomerDemandsSatisfied(drones, packages):
    packageDemandDic = dict(zip([pkg.id for pkg in packages], [pkg.destination for pkg in packages]))
    packagesDeliveredCorrectly = 0
    for drone in drones:
        for trip in drone.trips:
            for action in trip.actions:
                if "Delivery" in str(type(action)):
                    if action.node.id == packageDemandDic[action.package.id]:
                        packagesDeliveredCorrectly += 1

    return packagesDeliveredCorrectly


def countBatteriesUsed(drones):
    batteries = []
    #create a list of all batteries used in the solution
    batteries.extend(Depot.batteriesHeld)
    for drone in drones:
        batteries.append(drone.battery)
        for action in drone.getAllActions():
            if "ChangeBattery" in str(type(action)):
                #print(f"change battery action: {action}, {type(action)}")
                batteries.append(action.batterySelected)
    batteries.sort(key=lambda x : x.id)
    return len(set(batteries))

def countDroneChargeDepletion(drones): 
    numberOfDepletions = 0
    for drone in drones: 
        for trip in drone.trips: 
            for action in trip.actions[1:]: 
                if "Delivery" in str(type(action)) or "AtDepot" in str(type(action)):
                    distanceTraveled = Node.distanceFinder(action.node, action.prevAction.node)
                    drone.battery.batteryDistance -= distanceTraveled
                else:
                    drone.battery = action.batterySelected
                    #may need to calculate the charge of the battery selected
                if drone.battery.batteryDistance < 0: 
                    numberOfDepletions += 1
                    break
            else:
                continue 
            break
    return numberOfDepletions

def droneCargoCount(drones):
    numberOfTripsWithTooManyPackages = 0
    tripCount = 0
    for drone in drones:
        for trip in drone.trips:
            tripCount += 1
            packageCount = 0
            for action in trip.actions:
                if "Delivery" in str(type(action)):
                    packageCount += 1
            if packageCount > 5: 
                numberOfTripsWithTooManyPackages += 1
    return numberOfTripsWithTooManyPackages, tripCount

def droneWeightCount(drones):
    numberOfTripswithTooHeavyPackages = 0 
    for drone in drones:
        for trip in drone.trips:
            weightTotal = 0
            for action in trip.actions:
                if "Delivery" in str(type(action)):
                    weightTotal += action.package.weight
            if weightTotal > 30: 
                numberOfTripswithTooHeavyPackages += 1
    return numberOfTripswithTooHeavyPackages

def checkStartAndFinishPositions(drones): 
    tripsNotStartingAtDepot = 0 
    tripsNotFinishingAtDepot = 0 
    for drone in drones:
        for trip in drone.trips: 
            if trip.actions[0].node.getCoords() != (0,0):
                tripsNotStartingAtDepot += 1
            if trip.actions[-1].node.getCoords() != (0,0):
                tripsNotFinishingAtDepot += 1
    
    return tripsNotFinishingAtDepot, tripsNotStartingAtDepot