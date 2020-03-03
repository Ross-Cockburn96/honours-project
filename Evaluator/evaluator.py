import sys 
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("--solution", "-s", nargs='?', type=str, help="Solution file address", required=True)
parser.add_argument("--problem", "-p", nargs='?', type=str, help="Problem file address", required=True)

try:
    args = parser.parse_args()
    args = vars(args)
except IOError as msg:
    parser.error(str(msg)) 
    exit(0)

solution = args["solution"]
problem = args["problem"]


with open(solution) as file: 
    solutionData = file.read() 

print(solutionData)

with open(problem) as file:
    problemData = file.read()

print(f"---------------------------------------------")
print(problemData)


