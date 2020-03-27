import sys
#from context import generatorObjects
from .generators import Generator 
import os 

from generatorObjects.node import CustomerNode, ChargingNode, Node, DepletionPoint, Depot
from generatorObjects.action import ChangeBattery
import matplotlib.pyplot as plt 
from .parameters import Parameters
import random
import new_generator.tools


if __name__ == "__main__": 

    if len(sys.argv) > 1: 
        print("setting seed")
        Parameters.seedVal = int(sys.argv[1])

    generator = Generator(distribution="uniform")  
    generator.generateNodes()
    #problem.generateRechargingStations()
    generator.generateTripsandDrones()
    
    depletionPoints = generator.calculateChargeDepletionPoints()

    rechargeStations = generator.calculateRechargeStations(depletionPoints)
    generator.includeChargingStations(depletionPoints, rechargeStations)
    generator.rechargeStations = rechargeStations
    depletionPoints = generator.calculateChargeDepletionPoints()
    print(f"depletionPoints {depletionPoints}")
    count = 0 
    #check that the distance added to trip from rerouting to charging stations doesn't cause new depletion points
    while len(depletionPoints) > 0:
        count += 1
        print(count)
        chargingStations = [] 
        
        currentDroneBatteries = {}
        for point in depletionPoints: 
            chargingStation = ChargingNode(point.xCoord, point.yCoord)
            chargingStations.append(chargingStation)
            print(f"id is {chargingStation.id}")

            if not currentDroneBatteries.get(point.drone, False):
                currentBattery = point.drone.battery
            else: 
                currentBattery = currentDroneBatteries[point.drone]

            changeBatteryAction = ChangeBattery(chargingStation, currentBattery)
            currentDroneBatteries[point.drone] = changeBatteryAction.batterySelected #update to the new battery held
            chargingStation.batteriesHeld.append(changeBatteryAction.batterySelected)
            trip = point.trip
            action = point.action
            insertionIndex = trip.actions.index(action)
            trip.insertAction(insertionIndex, changeBatteryAction)
        generator.rechargeStations.extend(chargingStations)

        #generator.includeChargingStationsF(depletionPoints, chargingStations)
        depletionPoints = generator.calculateChargeDepletionPoints()
       
    for station in rechargeStations:
        print(station.batteriesHeld)    
  
    
    generator.createTimeWindows() 

    generator.createSolutionFile()
    generator.createGenotype()
    generator.createProblemFile()
    
    for trip in generator.drones[2].trips:
        print(trip)

    # plt.sca(parameters.ax)
    # plt.show()
