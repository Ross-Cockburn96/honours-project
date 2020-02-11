import solutionProcessor 
import sys 


if __name__ == "__main__":
    solutionFilePath = sys.argv[1]
    print(solutionProcessor.process(solutionFilePath))