import orjson, os, zipfile, shutil, re
from deep_translator import GoogleTranslator


keywords = {'en': ["united kingdom", "uk", "brexit", "england", "brits", "britain", "eu", "european union", "country"]}
supported_languages = ['en']
keywords_activated = True




def readData(link, type):
    inp = open(type+"/"+link+".json", 'rb')
    data = orjson.loads(inp.read())
    inp.close()

    return data



def sortJson(inp_link, out_link = "", do_print = True, format_link = "test", do_profiles = True, number_lines = -1):
    data_file = open("input/" + inp_link, 'rb')
    format_data = readData(format_link, "format")
    
    if (out_link != ""):
        out = open("output/" + out_link, 'wb')

    new_data = {}

    for line in data_file:
        try:
            data = orjson.loads(line)
            new_data = sortData(data, format_data, {})
            

            try:
                if (new_data["entities"]["user_mentions"] == [] or new_data["place"]["country_code"] == None):
                    new_data = {}

                elif keywords_activated:
                    lang = new_data["lang"]
                    if not (lang in supported_languages):
                        supported_languages.append(lang)
                        translateKeywords(lang)

                    new_data = contentCheck(new_data, lang)
                    
            except:
                new_data = {}


            if (out_link != "" and new_data != {}):
                out.write(orjson.dumps(new_data, option=orjson.OPT_APPEND_NEWLINE))

                if do_profiles:
                    try:
                        userProfile(new_data)

                    except:
                        if do_print:
                            print("Failed to create/update Profile of User -", new_data["user"]["id"])


            if (number_lines == 0):
                break

            if (number_lines > 0):
                number_lines -= 1
        
        except:
            if do_print:
                print("Trailing character error due to empty lines")



    if (out_link != ""):
        filesize = out.tell()
        out.close()

        if (filesize < 1):
            os.remove("output/" + out_link)



def sortData(data, format_data, new_data):
    for a in format_data:
        try:
            if type(data[a]) is dict:
                new_data[a] = sortData(data[a], format_data[a], {})


            elif type(data[a]) is list:
                for i in data[a]:
                    if a not in new_data:
                        new_data[a] = [ sortData(i, format_data[a][0], {}) ]

                    else:
                        new_data[a].append(sortData(i, format_data[a][0], {}))

            
            elif data[a] != None and type(data[a]) is not dict and type(data[a]) is not list: 

                if a == "text":
                    try:
                        new_data[a] = re.sub('@[\w]+|http\S+','',data["extended_tweet"]["full_text"])

                    except:                       
                        new_data[a] = re.sub('@[\w]+|http\S+','',data[a])
                
                    new_data[a] = new_data[a].strip()


                else:
                    if type(data[a]) == str:
                        new_data[a] = data[a].strip()
                    
                    else:
                        new_data[a] = data[a]
            
            else:
                return {}

        except:
            return {}

    return new_data



def sortFolder(dir, start, end, do_print = True, format_link = "format", line_limit = -1):
    absdir = os.path.abspath(dir)

    if not os.path.isdir("output/data"):
        os.mkdir("output/data")

    if not os.path.isdir("output/profiles"):
        os.mkdir("output/profiles")

    
    
    if do_print:
        file_number = 0
        total_files = 13139
        #total_files = len([name for name in os.listdir(absdir) if zipfile.is_zipfile(absdir + "/" + name)])

        print("Created Folders and Estimated Total files: ", total_files)
        print("")


    for path in os.listdir(absdir):

        if(zipfile.is_zipfile(absdir +"/"+ path)):
            file_date = int(re.sub('\D', '', path))

            if file_date >= start and file_date <= end:
                if do_print:
                    print(file_date)
                    file_number += 1

                zip_ref = zipfile.ZipFile(absdir +"/"+ path, 'r')
                json_path = path.replace(".zip", ".json")

                

                if os.path.exists("input/data/geoEurope/" + json_path):
                    cleanupCrash(json_path)
                

                elif os.path.exists("output/data/" + json_path):
                    if do_print:
                        print("File Completed: " + str(file_number) + "/" + str(total_files) )
                        print("")

                    continue
                    
                
                else:
                    zip_ref.extract(zip_ref.getinfo("geoEurope/"+json_path), 'input/data')

                    
                sortJson("data/geoEurope/"+json_path, "data/"+json_path, do_print, format_link,  True, line_limit)

                if do_print:
                    print("File Completed: " + str(file_number) + "/" + str(total_files) )
                    print("")
                
                if os.path.exists("input/data/geoEurope/"+json_path):
                    os.remove("input/data/geoEurope/"+json_path)

        
        elif os.path.isdir(absdir +"/"+ path):
            for inner_path in os.listdir(absdir + '/' + path):
                if(zipfile.is_zipfile(absdir + '/' + path + '/' + inner_path)):
                    file_date = int(re.sub('\D', '', inner_path))

                    if file_date >= start and file_date <= end:
                        if do_print:
                            print(file_date)
                            file_number += 1

                        
                        zip_ref = zipfile.ZipFile(absdir +"/"+ path + "/" + inner_path, 'r')
                        json_path = inner_path.replace(".zip", ".json")

                        

                        if os.path.exists("input/data/geoEurope/" + json_path):
                            cleanupCrash(json_path)

                
                        elif os.path.exists("output/data/" + json_path):

                            if do_print:
                                print("File Completed: " + str(file_number) + "/" + str(total_files) )
                                print("")

                            continue
                        
                        else:
                            zip_ref.extract(zip_ref.getinfo("geoEurope/"+json_path), 'input/data')
                            
                        
                        sortJson("data/geoEurope/"+json_path, "data/"+json_path, do_print, format_link, True, line_limit)

                        if do_print:
                            print("File Completed: " + str(file_number) + "/" + str(total_files) )
                            print("")

                        if os.path.exists("input/data/geoEurope/"+json_path):
                            os.remove("input/data/geoEurope/"+json_path)


    try:
        shutil.rmtree("input/data")

    except:
        if do_print:
            print("input/data directory has already been deleted")

    try:
        userLocationSetter()
    
    except:
        if do_print:
            print("userLocationSetter could not determine the location of a profile due to missing country code")




def cleanupCrash(json_path):
    if os.path.exists("output/data/" + json_path):
        data_file = open("output/data/" + json_path, 'rb')

        for line in data_file:
            try:
                data = orjson.loads(line)
                user_id = data["user"]["id"]
                tweet = { "created_at": data["created_at"], "lang": data["lang"], "text": data["text"], "entities": data["entities"], "id": data["id"], "place": data["place"] }
                
                if os.path.exists("output/profiles/" + str(user_id)):
                    profile = open("output/profiles/" + str(user_id) + ".json", 'rb')
                    profile_data = orjson.loads(profile.read())
                    profile.close()

                    tweets = profile_data["tweets"]

                    if len(tweets) > 1:
                        updated_profile = { "user": { "screen_name" : data["user"]["screen_name"], "id" : user_id}, "mentions": [], "tweets" : [] }

                        for t in tweets:
                            if t != tweet:
                                updated_profile["tweets"].append(t)

                                for m in tweet["entities"]["user_mentions"]:
                                    if m not in updated_profile["mentions"]:
                                        updated_profile["mentions"].append(m)


                        
                        profile_add = open("output/profiles/" + str(user_id) + ".json", 'wb')
                        profile_add.write(orjson.dumps(updated_profile))
                        profile_add.close()
                            


                    else:
                        os.remove("output/profiles/" + user_id)

            except:
                print("Trailing Sentence Error")

        data_file.close()
    
    os.remove("output/data/" + json_path)



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

    tweet = { "created_at": data["created_at"], "lang": data["lang"], "text": data["text"], "entities": data["entities"], "id": data["id"], "place": data["place"] }
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

        
        updated_profile = { "user": { "screen_name" : data["user"]["screen_name"], "id" : data["user"]["id"]}, "mentions": mentions, "tweets" : tweets }
        profile_add = open("output/profiles/" + str(data["user"]["id"]) + ".json", 'wb')
        profile_add.write(orjson.dumps(updated_profile))
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
            place = {}
            places = {}
            tid = []
            duplicates = []

            for tweet in tweets:
                if tweet["id"] in tid:
                    duplicates.append(tweet)
                    continue
                
                else:
                    tid.append(tweet["id"])

                country_code = tweet["place"]["country_code"]
                if country_code in place:
                    place[country_code] += 1

                else:
                    place[country_code] = 1
                    places[country_code] = tweet["place"]


            for dup in duplicates:
                tweets.remove(dup)

            
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
    inp_link = input("Is this being run on the remote server? (Y/N): ")
    print("")

    if inp_link.lower() == "y" or inp_link.lower() == "yes":
        path = "/hywel/Tweets/geo/Europe"
    
    else:
        path = "zips"

    
    inp_key = input("Are keywords being used? (Y/N): ")
    print("")

    if inp_key.lower() == "y" or inp_key.lower() == "yes":
        keywords_activated = True
    
    else:
        keywords_activated = False


    inp_print = input("Should every step be outputted? (Y/N): ")
    print("")

    if inp_print.lower() == "y" or inp_print.lower() == "yes":
        do_print = True
    
    else:
        do_print = False
    
    
    print("Started dataSorter")
    print("")


    sortFolder(path, 2019120416, 2020120416, do_print)

    print("")
    print("Finished Data Sorter")