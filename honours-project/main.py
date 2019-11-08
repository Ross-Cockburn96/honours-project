
import problemGenerator.Generator as Generator
import random
import numpy as np

if __name__ == "__main__":
    
    generator = Generator.Generator(noOfNodes= 150, nodemaxRangeRatio=1, distribution="clustered")
    generator.generateNodes()