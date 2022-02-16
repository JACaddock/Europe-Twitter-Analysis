from asyncio.windows_events import NULL
import string
import orjson, os.path

def readData(link, type):
    inp = open(type+"/"+link+".json", 'rb')
    data = orjson.loads(inp.read())
    inp.close()

    return data


def sortJson(inplink, outlink = "", formatlink = "test", numberlines = -1):
    datafile = open("input/"+inplink+".json", 'rb')
    formatdata = readData(formatlink, "format")
    
    if (outlink != ""):
        out = open("output/"+outlink+".json", 'wb')

    newdata = {}

    for line in datafile:
        data = orjson.loads(line)
        newdata = recursiveJson(data, formatdata, {})


        if (outlink != "" and newdata != {}):
            out.write(orjson.dumps(newdata, option=orjson.OPT_APPEND_NEWLINE))

        if (numberlines == 0):
            break

        if (numberlines > 0):
            numberlines -= 1


    if (outlink != ""):
        out.close()



def recursiveJson(data, formatdata, newdata):
    for a in data:
        for b in formatdata:
            if (a == b):
                if (type(data[a]) is dict):
                    if (type(formatdata[b]) is dict):
                        for k in data[a]:
                            if (k in formatdata[b]):
                                if (type(formatdata[b]) is dict and type(formatdata[b][k]) is list) and formatdata[b][k] != None:
                                    for l in data[a][k]:
                                        for m in formatdata[b][k]:
                                            
                                            if not (a in newdata):
                                                newdata[a] = {k : [ recursiveJson(l, m, {})] }

                                            else:
                                                newdata[a][k].append(recursiveJson(l, m, {}))  


                                else:
                                    if (formatdata[b][k] != None):
                                        if (formatdata[b][k] == data[a][k]):
                                            if not (a in newdata):
                                                newdata[a] = {k: data[a][k]}

                                            else:                 
                                                newdata[a] = {**newdata[a],  **{k: data[a][k]}}

                                        else:
                                            return {}

                                    else:
                                        if not (a in newdata):
                                            newdata[a] = {k: data[a][k]}

                                        else:                 
                                            newdata[a] = {**newdata[a],  **{k: data[a][k]}}

                    else:
                        for c in formatdata[b]:
                            if not (a in newdata):
                                newdata[a] = {c: data[a][c]}

                            else:                 
                                newdata[a] = {**newdata[a],  **{c: data[a][c]}}

                else:
                    if(type(formatdata) is not list):
                        if (formatdata[b] != None):
                            if (formatdata[b] == data[a]):
                                newdata[a] = data[a]

                            else:
                                return {}

                        else:
                            newdata[a] = data[a]
                
                    else:
                        newdata[a] = data[a]

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
        isoutput = input("Would you like to output the results?: ")
        
        if (isoutput.lower() == "yes" or isoutput.lower() == "y"):
            insideLoop = True

            isinput = input("Would you like to use the same name as the input file?: ")
            if (isinput.lower() == "yes" or isinput.lower() == "y"):
                outputlink = inputlink
                insideLoop = False
                looping = False
            
            
            elif (isinput.lower() == "no" or isinput.lower() == "n"):
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

        
        elif (isoutput.lower() == "no" or isoutput.lower() == "n"):
            looping = False
            outputlink = ""


    sortJson(inputlink, outputlink)