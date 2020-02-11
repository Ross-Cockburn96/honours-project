
'''
returns an easier to read version of the solution file.
each row represents a drone 
'''
def process(filePath):
    #read contents of solution file 
    with open(filePath) as file: 
        data = file.read() 
    
    elements = data.split(",")
    deliveriesForDrone = 0
    tripsForDrone = 0
    tripCountIdx = 0 
    outputString = []
    finished = False
    while not finished: 
        if tripCountIdx < len(elements):
            droneTrips = int(elements[tripCountIdx])
            outputString.append(str(droneTrips))

            tripCountIdx += 1

            while droneTrips > 0: 
                tripsForDrone += 1 
                deliveryCount = int(elements[tripCountIdx])
                outputString.append(str(deliveryCount))
                tripCountIdx += (deliveryCount * 2) + 1
                droneTrips -= 1
        
        else:
            finished = True 
            continue
        outputString.append('\n')
    return "".join([(str(x) + ", " if x != "\n" else "\n") for x in outputString])