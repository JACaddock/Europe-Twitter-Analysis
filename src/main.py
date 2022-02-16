import os.path
import dataSorter as ds


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


    ds.sortJson(inputlink, outputlink, "test", 1000)