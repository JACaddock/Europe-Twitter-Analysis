import orjson, os.path

def readData(link, type):
    inp = open(type+"/"+link+".json", 'rb')
    data = orjson.loads(inp.read())
    inp.close()

    return data


def sortJson(inplink, outlink = "", formatlink = "test", numberlines = 500):
    datafile = open("input/"+inplink+".json", 'rb')
    formatdata = readData(formatlink, "format")
    
    if (outlink != ""):
        out = open("output/"+outlink+".json", 'wb')

    newdata = {}
    linenumber = 0

    for line in datafile:
        data = orjson.loads(line)
        newdata = recursiveJson(data, formatdata, {})


        if (outlink != ""):
            out.write(orjson.dumps(newdata, option=orjson.OPT_APPEND_NEWLINE))

        if (linenumber >= numberlines):
            break

        linenumber += 1


    if (outlink != ""):
        out.close()



def recursiveJson(dataa, datab, newdata):
    for a in dataa:
        for b in datab:
            if (a == b):
                if (type(dataa[a]).__name__ == 'dict'):
                    for k in dataa[a]:
                        if (k in datab[b]):
                            if (type(datab[b]).__name__ == 'dict'):
                                if (len(dataa[a][k]) == 1):
                                    subdataa = dataa[a][k][0]
                                
                                else:
                                    subdataa = dataa[a][k]
                                
                                newdata[a] = { k : recursiveJson(subdataa, datab[b][k], {}) }
                        
                            else:
                                if not (a in newdata):
                                    newdata[a] = {k: dataa[a][k]}

                                else:                 
                                    newdata[a] = {**newdata[a],  **{k: dataa[a][k]}}
                else:
                    newdata[a] = dataa[a]

    return newdata




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