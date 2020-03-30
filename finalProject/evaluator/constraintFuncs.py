from generatorObjects.node import Depot, Node
from generatorObjects.battery import Battery
from algorithms.parameters import params
import copy

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
    print("checking customer demands")
    tempDepotBatteries = copy.deepcopy(Depot.batteriesHeld)
    packageDemandDic = dict(zip([pkg.id for pkg in packages], [pkg.destination for pkg in packages]))
    for key, val in packageDemandDic.items():
        print(f"{key}, {val}")
    packagesDeliveredCorrectly = 0
    for drone in drones:
        drone.reset()
        for trip in drone.trips:
            for action in trip.actions[:-1]:
                distanceTraveled = int(Node.distanceFinder(action.node, action.nextAction.node))
                drone.time += (distanceTraveled/params["droneSpeed"])
                if not "ChangeBattery" in str(type(action)):
                    if "Delivery" in str(type(action)):
                        if action.node.id == packageDemandDic[action.package.id]:
                            print(f"{action.node.id} == {packageDemandDic[action.package.id]}")
                            packagesDeliveredCorrectly += 1
                        else:
                            print(f"{action.node.id} NOT {packageDemandDic[action.package.id]}")
                        drone.battery.batteryDistance -= distanceTraveled
                    else:   
                        drone.battery.batteryDistance -= distanceTraveled
                    if drone.battery.batteryDistance == -1:#account for rounding error 
                        drone.battery.batteryDistance = 0
                else:
                    
                    if "Depot" in str(type(action.node)):
                        for idx, battery in enumerate(tempDepotBatteries):
                            if action.batterySelected.id == battery.id:
                                drone.battery = action.batterySelected
                                tempDepotBatteries[idx] = action.batteryDropped
                                action.batteryDropped.dockedTime = drone.time
                    else:
                        for idx, battery in enumerate(action.node.batteriesHeld):
                            if action.batterySelected.id == battery.id:
                                drone.battery = action.batterySelected
                                action.node.batteriesHeld[idx] = action.batteryDropped
                                action.batteryDropped.dockedTime = drone.time 

                    if drone.battery.dockedTime != None:
                        drone.battery.batteryDistance = min((drone.battery.batteryDistance +((drone.time - drone.battery.dockedTime)*params["chargeRate"])), params["batteryDistance"])  
                if drone.battery.batteryDistance < 0:
                    print("breaking")
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
    #batteries.extend(Depot.batteriesHeld)
    for drone in drones:
        batteries.append(drone.battery)
        for trip in drone.trips:
            for action in trip.actions:
                if "ChangeBattery" in str(type(action)):
                    batteries.append(action.batterySelected)
    if detailed:
        return len(set(batteries))
    elif len(set(batteries)) > maxBatteries:
        return False
    else:
        return True 

#needs a deep copy of drone list because object states are changed
def countDroneChargeDepletion(drones, detailed=True): 
    tempDepotBatteries = copy.deepcopy(Depot.batteriesHeld)
    numberOfDepletions = 0
    for drone in drones: 
        drone.reset()
        for trip in drone.trips: 
            for action in trip.actions[:-1]:
                # print(action.node)
                # print(action.nextAction.node)
                distanceTraveled = int(Node.distanceFinder(action.node, action.nextAction.node))
                drone.time += (distanceTraveled/params["droneSpeed"])
                if "Delivery" in str(type(action)) or "AtDepot" in str(type(action)):
                    drone.battery.batteryDistance -= distanceTraveled
                    if drone.battery.batteryDistance == -1: #account for rounding error
                        drone.battery.batteryDistance = 0

                else:
                    if "Depot" in str(type(action.node)):
                        batteries = tempDepotBatteries
                        for idx, battery in enumerate(batteries):
                            if action.batterySelected.id == battery.id:
                                drone.battery = tempDepotBatteries[idx]
                                #print(f"(CB)battery level is {drone.battery.batteryDistance}")
                                break
                            elif idx == len(tempDepotBatteries) -1: 
                                print(action.node.id)
                                print(action.batterySelected.id)
                                print(tempDepotBatteries)
                                print("LOOKING FOR NONEXISTING BATTERY")

                    else:
                        batteries = action.node.batteriesHeld
                        for idx, battery in enumerate(batteries):
                            if action.batterySelected.id == battery.id:
                                drone.battery = action.node.batteriesHeld[idx]
                                #print(f"(CB)battery level is {drone.battery.batteryDistance}")
                                break
                            elif idx == len(action.node.batteriesHeld) -1: 
                                print(action.node.id)
                                print(action.batterySelected.id)
                                print(action.node.batteriesHeld[idx])
                                print("LOOKING FOR NONEXISTING BATTERY")
                    
        
                    action.batteryDropped.dockedTime = drone.time
                    if drone.battery.dockedTime != None: 
                        drone.battery.batteryDistance = min((drone.battery.batteryDistance +((drone.time - drone.battery.dockedTime)*params["chargeRate"])), params["batteryDistance"])
                    possibleBatteries = []
                    #if the change battery action is at depot
                    if ("ChangeBattery" in str(type(action)) and ("Depot" in str(type(action.node)))):
                        possibleBatteries = tempDepotBatteries
                        for idx, battery in enumerate(possibleBatteries):
                            if battery.id == action.batterySelected.id:
                                tempDepotBatteries[idx] = action.batteryDropped

                    else:   
                        possibleBatteries = action.node.batteriesHeld
                        for idx, battery in enumerate(possibleBatteries):
                            if battery.id == action.batterySelected.id:
                                action.node.batteriesHeld[idx] = action.batteryDropped

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
    tempDepotBatteries = copy.deepcopy(Depot.batteriesHeld)
    chargingStationsOverCapacity = 0 
    for drone in drones:
        for trip in drone.trips:
            for action in trip.actions:
                if "ChangeBattery" in str(type(action)): 
                    chargingNode = action.node 

                    if "Depot" in str(type(action.node)):
                        batteries = tempDepotBatteries
                    else:
                        batteries = chargingNode.batteriesHeld

                    for idx, battery in enumerate(batteries): 
                        if battery.id == action.batterySelected:
                            if "Depot" not in str(type(action.node)):
                                tempDepotBatteries[idx] = action.batteryDropped
                                if len(tempDepotBatteries > Depot.capacity):
                                    chargingStationsOverCapacity += 1
                            else:
                                chargingNode.batteriesHeld[idx] = action.batteryDropped
                                if len(chargingNode.batteriesHeld) > chargingNode.capacity:
                                    chargingStationsOverCapacity += 1
    if detailed:
        return chargingStationsOverCapacity
    elif chargingStationsOverCapacity > 0 :
        return False
    else:
        return True