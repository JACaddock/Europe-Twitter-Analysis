import orjson, sys, os, zipfile, shutil
from deep_translator import GoogleTranslator


keywords = {'en': ["covid", "pandemic"]}
supported_languages = ['en']




def readData(link, type):
    inp = open(type+"/"+link+".json", 'rb')
    data = orjson.loads(inp.read())
    inp.close()

    return data



def sortJson(inplink, filenumber, totalfiles, outlink = "", formatlink = "test", numberlines = -1):
    datafile = open("input/" + inplink, 'rb')
    formatdata = readData(formatlink, "format")
    
    if (outlink != ""):
        out = open("output/" + outlink, 'wb')

    newdata = {}

    for line in datafile:
        data = orjson.loads(line)
        newdata = sortData(data, formatdata, {})


        try:
            if (newdata["entities"]["user_mentions"] == []):
                newdata = {}
            else:
                lang = newdata["lang"]
                if not (lang in supported_languages):
                    supported_languages.append(lang)
                    translateKeywords(lang)

                newdata = contentCheck(newdata, lang)
        except:
            newdata = {}

        if (outlink != "" and newdata != {}):
            out.write(orjson.dumps(newdata, option=orjson.OPT_APPEND_NEWLINE))
            userProfile(newdata)

        if (numberlines == 0):
            break

        if (numberlines > 0):
            numberlines -= 1


    if (outlink != ""):
        filesize = out.tell()
        out.close()

        if (filesize < 1):
            os.remove("output/" + outlink)

        print("File Completed: " + str(filenumber) + "/" + str(totalfiles) )



def sortData(data, formatdata, newdata):
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
                                                newdata[a] = {k : [ sortData(l, m, {})] }

                                            else:
                                                newdata[a][k].append(sortData(l, m, {}))  


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



def sortFolder(dir, formatlink = "test", linelimit = -1):

    if not os.path.isdir("output/"+dir):
        os.mkdir("output/" + dir)
    else:
        shutil.rmtree("output/" + dir)
        os.mkdir("output/" + dir)

    if not os.path.isdir("output/profiles"):
        os.mkdir("output/profiles")
    else:
        shutil.rmtree("output/profiles")
        os.mkdir("output/profiles")

    if os.path.isdir("input/"+dir):
        shutil.rmtree("input/"+dir)

    filenumber = 0
    totalfiles = len([name for name in os.listdir(dir) if zipfile.is_zipfile(dir+"/"+name)])
    for path in os.listdir(dir):
        if(zipfile.is_zipfile(dir+"/"+path)):
            zip_ref = zipfile.ZipFile(dir+"/"+path, 'r')
            jsonpath = path.replace(".zip", ".json")
            zip_ref.extract(zip_ref.getinfo("geoEurope/"+jsonpath), 'input/'+dir)
            
            filenumber += 1
            sortJson(dir+"/geoEurope/"+jsonpath, filenumber, totalfiles, dir+"/"+jsonpath, formatlink, linelimit)

            os.remove("input/"+ dir + "/geoEurope/"+jsonpath)

    shutil.rmtree("input/"+dir)


def translateKeywords(lang):
    translated_words = []
    
    for word in keywords["en"]:
        translation = GoogleTranslator(source='auto', target=lang).translate(text=word)
        translated_words.append(translation)
    
    keywords[lang] = translated_words


def contentCheck(data, lang):
    text = data["text"]    

    for word in keywords[lang]:
        if word in text.lower():
            return data
    
    return {}


def userProfile(data):
    profile = open("output/profiles/" + str(data["user"]["id"]) + ".json", 'ab')
    
    if (False):
        text = data["text"]
        translation = GoogleTranslator(source='auto').translate(text=text)
        data["text"] = translation
    
    profile.write(orjson.dumps(data, option=orjson.OPT_APPEND_NEWLINE))
    profile.close()



if __name__ == '__main__':
    try:
        sortFolder("zips")
    except:
        print("fail")


    