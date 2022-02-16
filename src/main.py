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


    looping = True
    while looping:
        hasformat = input("Do you have a specific format file to use?: ")

        if (hasformat.lower() == "yes" or hasformat.lower() == "y"):

            formatlink = input("Enter format file name: ")

            if (formatlink == ""):
                print("You haven't entered a name")
        
            elif not (os.path.exists("format/"+formatlink+".json")):
                print("This file does not exist")
                print("Make sure the format file exists")
            
            else:
                looping = False

        elif (hasformat.lower() == "no" or hasformat.lower() == "n"):
            looping = False
            formatlink = "test"

    looping = True
    while looping:
        specificnumber = input("Would you like to limit the number of lines read?: ")

        if (specificnumber.lower() == "yes" or specificnumber.lower() == "y"):
            numberoflines = int(input("Enter the number of lines: "))

            if numberoflines > 0:
                looping = False

            else:
                print("You didn't enter a valid number")

        elif (specificnumber.lower() == "no" or specificnumber.lower() == "n"):
            looping = False
            numberoflines = -1
            

    ds.sortJson(inputlink, outputlink, formatlink, numberoflines)