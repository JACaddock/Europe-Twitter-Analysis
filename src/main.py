import orjson, os.path

def readInput(inplink):
    inp = open("input/"+inplink+".json", 'rb')
    data = orjson.loads(inp.read())
    inp.close()

    return data


def sortJson(inplink, outlink = ""):
    data = readInput(inplink)
    newdata = {}

    for i in data:
        if (i == "place" or i == "entities" or i == "text" or i == "user" or i == 'id' or i == "created_at"):
            newdata[i] = data[i]


    if (outlink != ""):
        print("outputting")
        outputFile(outlink, newdata)

    else:
        print("no output")

    
def outputFile(outlink, data):
    out = open("output/"+outlink+".json", 'wb')
    out.write(orjson.dumps(data))
    out.close()




if __name__ == "__main__":
    looping = True
    while looping:
        inputlink = input("Enter input file name: ")

        if (inputlink == ""):
            print("You must use an input file")
        
        elif not (os.path.exists("input/"+inputlink+".json")):
            print("This file does not exist")
            
        else:
            looping = False


    looping = True
    while looping:
        answer = input("Would you like to output the results?: ")
        if (answer.lower() == "yes" or answer.lower() == "y"):
            insideLoop = True

            while insideLoop:
                outputlink = input("Enter output file name: ")

                if (outputlink == ""):
                    print("You haven't entered an output name")
                    answer = input("Are you sure you want to output to a file?: ")
                    if (answer.lower() == "no" or answer.lower() == "n"):
                        insideLoop = False
                        looping = False
                
                else:
                    insideLoop = False
                    looping = False
        
        elif (answer.lower() == "no" or answer.lower() == "n"):
            looping = False
            outputlink = ""


    sortJson(inputlink, outputlink)