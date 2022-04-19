from tabnanny import check
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import orjson, os


checkedprofile = {}
mentioned = {}
mentionedmore = {}


def checkProfiles():
    for path in os.listdir("output/profiles"):
        for json in os.listdir("output/profiles/" + path):
            file = open("output/profiles/" + path + "/" + json, 'rb')
            profile = orjson.loads(file.read())

            checkedprofile[profile["user"]["id"]] = profile["place"]["country_code"]



def showProfiles():
    for path in os.listdir("output/profiles"):
        #scores = [path]
        #print(path)
        
        for json in os.listdir("output/profiles/" + path):
            file = open("output/profiles/" + path + '/' + json , 'rb')
            profile = orjson.loads(file.read())

            #inmention = False
            checkedprofile[profile["user"]["id"]] = profile["place"]["country_code"]

            #if profile["user"]["id"] in mentioned:
                #print(profile["user"])
                #inmention = True

            
            for tweet in profile["tweets"]:
                mentions = tweet["entities"]["user_mentions"]
                for mention in mentions:

                    if mention["id"] in mentioned:
                        mentioned[mention["id"]] += 1
                        mentionedmore[mention["id"]] = mentioned[mention["id"]]


                    else:
                        mentioned[mention["id"]] = 1



                    if mention["id"] in checkedprofile:
                            if profile["place"]["country_code"] != checkedprofile[mention["id"]]:
                                score = tweetAnalyser(tweet)
                                print(profile["user"]["id"], profile["place"]["country_code"], mention["id"], checkedprofile[mention["id"]], score)




            #scores.append(json)
            #scores.append(jsonscores)

        #print(scores)

        

def tweetAnalyser(tweet):
    analyser = SentimentIntensityAnalyzer()
    
    text = tweet["text"]
    vs = analyser.polarity_scores(text)
    #print(data[i], str(vs))

    return vs['compound']




def profileAnalyser(profile):
    analyser = SentimentIntensityAnalyzer()
    tweets = profile["tweets"]

    scores = []


    for tweet in tweets:
        text = tweet["text"]
        vs = analyser.polarity_scores(text)
        #print(data[i], str(vs))
        scores.append(vs['compound'])

    return scores



if __name__ == '__main__':
    checkProfiles()
    showProfiles()


    #print(mentionedmore)