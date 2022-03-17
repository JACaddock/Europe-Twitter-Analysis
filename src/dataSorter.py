import orjson, sys, os, zipfile, shutil

def readData(link, type):
    inp = open(type+"/"+link+".json", 'rb')
    data = orjson.loads(inp.read())
    inp.close()

    return data


def sortJson(inplink, outlink = "", formatlink = "test", numberlines = -1):
    datafile = open("input/" + inplink, 'rb')
    formatdata = readData(formatlink, "format")
    
    if (outlink != ""):
        out = open("output/" + outlink, 'wb')

    newdata = {}

    for line in datafile:
        data = orjson.loads(line)
        newdata = recursiveJson(data, formatdata, {})


        try:
            if (newdata["entities"]["user_mentions"] == []):
                newdata = {}
        except:
            newdata = {}

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



def sortFolder(dir, formatlink, linelimit = -1):

    if not os.path.isdir("output/"+dir):
        os.mkdir("output/" + dir)

    if os.path.isdir("input/"+dir):
        shutil.rmtree("input/"+dir)

    for path in os.listdir(dir):
        if(zipfile.is_zipfile(dir+"/"+path)):
            zip_ref = zipfile.ZipFile(dir+"/"+path, 'r')
            jsonpath = path.replace(".zip", ".json")
            zip_ref.extract(zip_ref.getinfo("geoEurope/"+jsonpath), 'input/'+dir)
            
            sortJson(dir+"/geoEurope/"+jsonpath, dir+"/"+jsonpath, formatlink, linelimit)

            os.remove("input/"+ dir + "/geoEurope/"+jsonpath)


    shutil.rmtree("input/"+dir)




def removeFolder(type, dir):
    if os.path.isdir(type+"/"+dir):
        shutil.rmtree(type+"/"+dir)





if __name__ == '__main__':
    try:
        removeFolder("input", "zips")
        removeFolder("output", "zips")
        sortFolder("zips", "gb")
        #globals()[sys.argv[1]](sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]))
    except:
        try:
            globals()[sys.argv[1]](sys.argv[2], sys.argv[3], sys.argv[4])
        except:
            globals()[sys.argv[1]](sys.argv[2], sys.argv[3])


    