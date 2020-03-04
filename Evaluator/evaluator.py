import sys 
import argparse
from generatorObjects.drone import Drone


parser = argparse.ArgumentParser()
parser.add_argument("--solution", "-s", nargs='?', type=str, help="Solution file address", required=True)
parser.add_argument("--problem", "-p", nargs='?', type=str, help="Problem file address", required=True)
parser.add_argument("--output", "-o", nargs='?', type=str, default="output.txt", help="Output file write address")



try:
    args = parser.parse_args()
    args = vars(args)
except IOError as msg:
    parser.error(str(msg)) 
    exit(0)

solution = args["solution"]
problem = args["problem"]
outputLocation = args["output"]

drones = []



def buildObjects(solutionElements):
    finished = False 
    solutionCountIdx = 1 #this index gives the number of trips in the first drone 
    while solutionCountIdx < len(elements):
        droneTrips = int(solutionElements[solutionCountIdx])
        drone = Drone()

        solutionCountIdx += 1

        for _ in range(droneTrip):
            tripActions = int(solutionElements[solutionCountIdx])
            actions = []
            f
            



with open(solution) as file: 
    solutionData = file.read() 
    solutionElements = solutionData.split(",")
    buildObjects(solutionElements)

with open(problem) as file:
    problemData = file.read()
    problemElements = problemData.split(",")

def checkPackagesDelivered():
    for element in solutionElements:


with open(outputLocation, "w") as file:
    file.seek(0)
    file.write(f"PROBLEM FILE DATA\n------------------------------------------------------------\n")
    file.write(f"Maximum Number of drones available: {problemElements[0]}\n")
    file.write(f"Maximum Number of batteries available: {problemElements[1]}\n")
    file.write(f"Number of customers in problem file: {problemElements[2]}\n")
    file.write(f"Number of packages to be delivered by drones: {problemElements[3]}\n")
    file.write(f"Number of recharging stations in the problem: {problemElements[4]}\n\n")
    
    result = None
    file.write(f"CHECKING SOLUTION FILE FOR HARD CONSTRAINT VIOLATIONS\n------------------------------------------------------------\n")
    if int(solutionElements[0]) <= int(problemElements[0]):
        result = "PASS"
    else: 
        result = "FAIL"
    file.write(f"Drones used in solution: {solutionElements[0]}: {result}")
    result = checkPackagesDelivered()




