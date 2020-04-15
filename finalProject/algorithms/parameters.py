params = {
    "cargoWeightLimit" : 30, #lb
    "cargoSlotNum" : 5,
    "numGenes" : None, # set in genetic.py
    "tournamentSize" : 3,
    "popSize" : 1,
    "mutationRate" : .05,
    "dayLength" : 28800, #s
    "droneSpeed": 10, #m/s
    "chargeRate": 2, #m/s
    "batteryDistance": 40000, #m,
    "batteryChargeThreshold" : 3000, #if a battery is below this threshold, it is considered low charge and will not be selected if charging and if currently held, a charging station will be searched for 
    "experimentRuns" : 4
}
