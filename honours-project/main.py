
import problemGenerator.Generator as Generator
import random
import numpy as np

if __name__ == "__main__":
    
    generator = Generator.Generator(noOfNodes= 50, nodeRange=.25)
    generator.generateNodes()