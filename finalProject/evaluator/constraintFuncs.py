from generatorObjects.node import Depot, Node
from algorithms.parameters import params

#droneConstraints = [countUniquePackagesDelivered, countBatteriesUsed, countDroneChargeDepletion, droneCargoCount]
def countUniquePackagesDelivered(drones, detailed=True, NoOfPackages = None):
    packages = [] 

    #create a list of all packages delivered in the solution
    for drone in drones:
        for action in drone.getAllActions():
            if "Delivery" in str(type(action)):
                packages.append(action.package.id)
    if detailed:
        return len(set(packages))
    elif len(set(packages)) != NoOfPackages:
        return False 
    else:
        return True

#needs a deep copy of drone list because object states are changed
def checkCustomerDemandsSatisfied(drones, packages, detailed=True):
    packageDemandDic = dict(zip([pkg.id for pkg in packages], [pkg.destination for pkg in packages]))
    packagesDeliveredCorrectly = 0
    for drone in drones:
        for trip in drone.trips:
            for action in trip.actions[1:]:
                if not "ChangeBattery" in str(type(action)):
                    if "Delivery" in str(type(action)):
                        if action.node.id == packageDemandDic[action.package.id]:
                            packagesDeliveredCorrectly += 1
                    else:   
                        distanceTraveled = Node.distanceFinder(action.node, action.prevAction.node)
                        drone.battery.batteryDistance -= distanceTraveled
                else:
                    drone.battery = action.batterySelected
                if drone.battery.batteryDistance < 0:
                    break
            else:
                continue
            break
    if detailed:
        return packagesDeliveredCorrectly
    elif packagesDeliveredCorrectly != len(packages):
        return False
    else:
        return True
            

def countBatteriesUsed(drones, detailed=True, maxBatteries = None):
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
    if detailed:
        return len(set(batteries))
    elif len(set(batteries)) > maxBatteries:
        return False
    else:
        return True 

#needs a deep copy of drone list because object states are changed
def countDroneChargeDepletion(drones, detailed=True): 
    numberOfDepletions = 0
    for drone in drones: 
        for trip in drone.trips: 
            for action in trip.actions[1:]:
                distanceTraveled = Node.distanceFinder(action.node, action.prevAction.node) 
                drone.time += (distanceTraveled/params["droneSpeed"])
                if "Delivery" in str(type(action)) or "AtDepot" in str(type(action)):
                    drone.battery.batteryDistance -= distanceTraveled
                else:
                    drone.battery = action.batterySelected
                    if drone.battery.dockedTime != None: 
                        drone.battery.batteryDistance = min((drone.battery.batteryDistance +((drone.time - battery.dockedTime)*params["chargeRate"])), params["batteryDistace"])
                    chargingNode = action.node
                    for idx, battery in enumerate(action.node.batteriesHeld):
                        if battery.id == action.batterySelected.id:
                            chargingNode.batteriesHeld[idx] = action.batteryDropped
                if drone.battery.batteryDistance < 0: 
                    numberOfDepletions += 1
                    break
            else:
                continue 
            break
    if detailed:
        return numberOfDepletions
    elif numberOfDepletions > 0:
        return False
    else:
        return True

def droneCargoCount(drones, detailed=True):
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
    if detailed:
        return numberOfTripsWithTooManyPackages, tripCount
    elif numberOfTripsWithTooManyPackages > 0: 
        return False
    else:
        return True

def droneWeightCount(drones, detailed=True):
    numberOfTripswithTooHeavyPackages = 0 
    for drone in drones:
        for trip in drone.trips:
            weightTotal = 0
            for action in trip.actions:
                if "Delivery" in str(type(action)):
                    weightTotal += action.package.weight
            if weightTotal > 30: 
                numberOfTripswithTooHeavyPackages += 1
    if detailed:
        return numberOfTripswithTooHeavyPackages
    elif numberOfTripswithTooHeavyPackages > 0:
        return False
    else: 
        return True

def checkStartAndFinishPositions(drones, detailed=True): 
    tripsNotStartingAtDepot = 0 
    tripsNotFinishingAtDepot = 0 
    for drone in drones:
        for trip in drone.trips: 
            if trip.actions[0].node.getCoords() != (0,0):
                tripsNotStartingAtDepot += 1
            if trip.actions[-1].node.getCoords() != (0,0):
                tripsNotFinishingAtDepot += 1
    if detailed:
        return tripsNotFinishingAtDepot, tripsNotStartingAtDepot
    elif (tripsNotStartingAtDepot > 0) or (tripsNotFinishingAtDepot > 0):
        return False
    else:
        return True 

#needs a deep copy of drone list because object states are changed
def chargingStationsOverCapacity(drones, detailed=True): 
    chargingStationsOverCapacity = 0 
    for drone in drones:
        for trip in drone.trips:
            for action in trip.actions:
                if "ChangeBattery" in str(type(action)): 
                    chargingNode = action.node 
                    batteries = chargingNode.batteriesHeld 
                    for idx, battery in enumerate(batteries): 
                        if battery.id == action.batterySelected.id:
                            chargingNode.batteriesHeld[idx] = action.batteryDropped
                    if len(chargingNode.batteriesHeld) > chargingNode.capacity:
                        chargingStationsOverCapacity += 1
    if detailed:
        return chargingStationsOverCapacity
    elif chargingStationsOverCapacity > 0 :
        return False
    else:
        return True