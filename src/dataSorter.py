import orjson, os, zipfile, shutil, re, math
from deep_translator import GoogleTranslator


keywords = {'en': ["united kingdom", "uk", "brexit", "england", "brits", "britain"]}
supported_languages = ['en']
keywords_activated = True




def readData(link, type):
    inp = open(type+"/"+link+".json", 'rb')
    data = orjson.loads(inp.read())
    inp.close()

    return data



def sortJson(inplink, filenumber, totalfiles, outlink = "", formatlink = "test", doprofiles = True, numberlines = -1):
    datafile = open("input/" + inplink, 'rb')
    formatdata = readData(formatlink, "format")
    
    if (outlink != ""):
        out = open("output/" + outlink, 'wb')

    newdata = {}

    for line in datafile:
        try:
            data = orjson.loads(line)
            newdata = sortData(data, formatdata, {})
            

            try:
                if (newdata["entities"]["user_mentions"] == []):
                    newdata = {}
                elif keywords_activated:
                    lang = newdata["lang"]
                    if not (lang in supported_languages):
                        supported_languages.append(lang)
                        translateKeywords(lang)

                    newdata = contentCheck(newdata, lang)
            except:
                newdata = {}
                #print("no user mentions")

            if (outlink != "" and newdata != {}):
                out.write(orjson.dumps(newdata, option=orjson.OPT_APPEND_NEWLINE))

                if doprofiles:
                    userProfile(newdata)

            if (numberlines == 0):
                break

            if (numberlines > 0):
                numberlines -= 1
        
        except:
            print("Most likely a trailing character error due to empty lines")



    if (outlink != ""):
        filesize = out.tell()
        out.close()

        if (filesize < 1):
            os.remove("output/" + outlink)

        print("File Completed: " + str(filenumber) + "/" + str(totalfiles) )
        print("")



def sortData(data, formatdata, newdata):
    for a in data:
        for b in formatdata:
            if (a == b):
                if (a == "text"):
                    try:
                        newdata[a] = re.sub('@[\w]+|http\S+','',data["extended_tweet"]["full_text"])

                    except:
                        
                        newdata[a] = re.sub('@[\w]+|http\S+','',data[a])
                        

                    newdata[a] = newdata[a].strip()

                elif (type(data[a]) is dict):
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
                                            #print(a, "doesn't exist but coordinates:", data["coordinates"]["coordinates"], "do")
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
                                #print(a, "doesn't exist but coordinates:", data["coordinates"]["coordinates"], "do")
                                return {}

                        else:
                            newdata[a] = data[a]
                
                    else:
                        newdata[a] = data[a]

    return newdata



def sortFolder(dir, start, end, formatlink = "format", linelimit = -1):
    absdir = os.path.abspath(dir)

    if not os.path.isdir("output/data"):
        os.mkdir("output/data")

    if not os.path.isdir("output/profiles"):
        os.mkdir("output/profiles")

    filenumber = 0
    totalfiles = len([name for name in os.listdir(absdir) if zipfile.is_zipfile(absdir + "/" + name)])
    #totalfiles = 10260

    print("Created Folders and Estimated Total files: ", totalfiles)
    print("")

    for path in os.listdir(absdir):

        if(zipfile.is_zipfile(absdir +"/"+ path)):
            file_date = int(re.sub('\D', '', path))

            if file_date >= start and file_date <= end:
                print(file_date)
                zip_ref = zipfile.ZipFile(absdir +"/"+ path, 'r')
                jsonpath = path.replace(".zip", ".json")

                filenumber += 1

                if os.path.exists("input/data/geoEurope/" + jsonpath):
                    cleanupCrash(jsonpath)
                

                elif os.path.exists("output/data/" + jsonpath):
                    print("File Completed: " + str(filenumber) + "/" + str(totalfiles) )
                    print("")
                    continue
                    
                
                else:
                    zip_ref.extract(zip_ref.getinfo("geoEurope/"+jsonpath), 'input/data')

                    
                sortJson("data/geoEurope/"+jsonpath, filenumber, totalfiles, "data/"+jsonpath, formatlink, linelimit)
                
                os.remove("input/data/geoEurope/"+jsonpath)

        
        elif os.path.isdir(absdir +"/"+ path):
            for inner_path in os.listdir(absdir + '/' + path):
                if(zipfile.is_zipfile(absdir + '/' + path + '/' + inner_path)):
                    file_date = int(re.sub('\D', '', inner_path))

                    if file_date >= start and file_date <= end:
                        print(file_date)
                        zip_ref = zipfile.ZipFile(absdir +"/"+ path + "/" + inner_path, 'r')
                        jsonpath = inner_path.replace(".zip", ".json")

                        filenumber += 1
                        totalfiles += 1

                        if os.path.exists("input/data/geoEurope/" + jsonpath):
                            cleanupCrash(jsonpath)

                
                        elif os.path.exists("output/data/" + jsonpath):
                            print("File Completed: " + str(filenumber) + "/" + str(totalfiles) )
                            print("")
                            continue
                        
                        else:
                            zip_ref.extract(zip_ref.getinfo("geoEurope/"+jsonpath), 'input/data')
                            
                        
                        sortJson("data/geoEurope/"+jsonpath, filenumber, totalfiles, "data/"+jsonpath, formatlink, linelimit)

                        os.remove("input/data/geoEurope/"+jsonpath)


    shutil.rmtree("input/data")

    userLocationSetter()


def cleanupCrash(jsonpath):
    if os.path.exists("output/data/" + jsonpath):
        datafile = open("output/data/" + jsonpath, 'rb')

        for line in datafile:
            try:
                data = orjson.loads(line)
                userid = data["user"]["id"]
                tweet = { "created_at": data["created_at"], "lang": data["lang"], "text": data["text"], "entities": data["entities"], "id": data["id"], "in_reply_to_screen_name": data["in_reply_to_screen_name"], "place": data["place"] }
                
                if os.path.exists("output/profiles/" + str(userid)):
                    profile = open("output/profiles/" + str(userid) + ".json", 'rb')
                    profile_data = orjson.loads(profile.read())
                    profile.close()

                    tweets = profile_data["tweets"]

                    if len(tweets) > 1:
                        updated = { "user": { "screen_name" : data["user"]["screen_name"], "id" : userid}, "mentions": [], "tweets" : [] }

                        for t in tweets:
                            if t != tweet:
                                updated["tweets"].append(t)

                                for m in tweet["entities"]["user_mentions"]:
                                    if m not in updated["mentions"]:
                                        updated["mentions"].append(m)


                        
                        profile_add = open("output/profiles/" + str(userid) + ".json", 'wb')
                        profile_add.write(orjson.dumps(updated))
                        profile_add.close()
                            


                    else:
                        os.remove("output/profiles/" + userid)

            except:
                print("Trailing Sentance Error")

        datafile.close()
    
    os.remove("output/data/" + jsonpath)



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

    tweet = { "created_at": data["created_at"], "lang": data["lang"], "text": data["text"], "entities": data["entities"], "id": data["id"], "in_reply_to_screen_name": data["in_reply_to_screen_name"], "place": data["place"] }
    mention = data["entities"]["user_mentions"]

    if (os.path.exists("output/profiles/" + str(data["user"]["id"]) + ".json")):
        profile = open("output/profiles/" + str(data["user"]["id"]) + ".json", 'rb')
        profile_data = orjson.loads(profile.read())
        profile.close()

        tweets = profile_data["tweets"]
        tweets.append(tweet)

        mentions = profile_data["mentions"]
        for m in mention:
            if m not in mentions:
                mentions.append(m)

        
        updated = { "user": { "screen_name" : data["user"]["screen_name"], "id" : data["user"]["id"]}, "mentions": mentions, "tweets" : tweets }
        profile_add = open("output/profiles/" + str(data["user"]["id"]) + ".json", 'wb')
        profile_add.write(orjson.dumps(updated))
        profile_add.close()
        

    
    else:
        profile = open("output/profiles/" + str(data["user"]["id"]) + ".json", 'ab')
        profile.write(orjson.dumps({ "user": { "screen_name" : data["user"]["screen_name"], "id" : data["user"]["id"]}, "mentions": mention, "tweets" : [tweet] }))
        profile.close()
    

    
    
def userLocationSetter():
    #Go through user profiles and determine they're location by where most of their tweets are sent from 
    for path in os.listdir("output/profiles"):
        if os.path.isfile("output/profiles/" + path):
            profile = open("output/profiles/" + path, 'rb')
            data = orjson.loads(profile.read())
            profile.close()

            tweets = data["tweets"]
            num_tweet = math.floor((len(tweets)/2 + 1))
            place = {}
            places = {}

            for tweet in tweets:
                country_code = tweet["place"]["country_code"]
                if country_code in place:
                    place[country_code] += 1

                else:
                    place[country_code] = 1
                    places[country_code] = tweet["place"]

                
                if (place[country_code] >= num_tweet): 
                    addProfile({ "user": data["user"], "place": tweet["place"], "mentions": data["mentions"], "tweets" : tweets }, path, country_code)
                    break

            
            max_number = 0
            current_place = {}
            for country, number in place.items():
                if number > max_number:
                    max_number = number
                    current_place = places.get(country)

            if (current_place != {}):
                addProfile({ "user": data["user"], "place": current_place, "mentions": data["mentions"], "tweets" : tweets }, path, country_code)

            os.remove("output/profiles/" + path)




def addProfile(data, inp, out):
    if not os.path.isdir("output/profiles/" + out ):
        os.mkdir("output/profiles/" + out)

    profile_add = open("output/profiles/" + out + "/" + inp, 'wb')
    profile_add.write(orjson.dumps(data))
    profile_add.close()




if __name__ == '__main__':
    print("")
    inplink = input("Is this being run on the remote server? (Y/N): ")
    print("")

    if inplink.lower() == "y" or inplink.lower() == "yes":
        path = "/hywel/Tweets/geo/Europe"
    
    else:
        path = "test"

    
    inpkey = input("Are keywords being used? (Y/N): ")
    print("")

    if inpkey.lower() == "y" or inpkey.lower() == "yes":
        keywords_activated = True
    
    else:
        keywords_activated = False
    
    
    print("Started dataSorter")
    print("")


    sortFolder(path, 2019120416, 2021063023)