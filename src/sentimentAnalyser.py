from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import orjson, os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime


checkedprofile = {}
mentioned = {}
sentimentover = {}


def startAnalysis():
    if not os.path.isdir("output/sentiment" ):
        print("Creating sentiment json")
        os.mkdir("output/sentiment")

        checkProfiles()
        buildProfiles()

        for over in sentimentover:
            size = len(sentimentover[over][0])
            quickSortSentimentOver(sentimentover[over], 0, size - 1)

            sentimentJson = open("output/sentiment/" + over +".json", 'wb')
            sentimentJson.write(orjson.dumps(sentimentover[over]))
            sentimentJson.close()

        

    else:
        print("sentiment folder already exists, delete folder if you need to recheck or build profiles")

        for json in os.listdir("output/sentiment"):

            sentimentJson = orjson.loads(open("output/sentiment/" + json, 'rb').read())

            for i in range(len(sentimentJson[0])):
                sentimentJson[0][i] = datetime.strptime(sentimentJson[0][i], "%Y-%m-%d").date()


            key = json.replace(".json", "")
            sentimentover[key] = sentimentJson



    if not os.path.isdir("output/graphs"):
        os.mkdir("output/graphs")
        
    
    for keys in sentimentover:

        if len(sentimentover[keys][0]) > 1:
            total_tweets = len(sentimentover[keys][1])


            # %Y is YYYY | %m is MM | %d is DD
            target_date = "%d/%m/%Y"
            sentimentover[keys] = workoutAverageSentiment(keys, target_date)
            plotGraph(keys, target_date, keys+" Day", total_tweets)

            target_date = "%m/%Y"
            sentimentover[keys] = workoutAverageSentiment(keys, target_date)
            plotGraph(keys, target_date, keys+" Month", total_tweets)



def checkProfiles():
    for path in os.listdir("output/profiles"):
        for json in os.listdir("output/profiles/" + path):
            file = open("output/profiles/" + path + "/" + json, 'rb')
            profile = orjson.loads(file.read())

            checkedprofile[profile["user"]["id"]] = profile["place"]["country_code"]



def buildProfiles():
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


                    else:
                        mentioned[mention["id"]] = 1



                    if mention["id"] in checkedprofile:
                        profile_country = profile["place"]["country_code"]
                        mention_country = checkedprofile[mention["id"]]

                        if profile_country != mention_country:
                            score = tweetAnalyser(tweet)
                            datetime_object = datetime.strptime(tweet["created_at"], "%a %b %d %X %z %Y").date()

                            #print(profile["user"]["id"], profile_country, mention["id"], mention_country, score, datetime_object)
                            
                            try:
                                sentimentover[profile_country + " of " + mention_country][0].append(datetime_object)
                                sentimentover[profile_country + " of " + mention_country][1].append(score)

                            except:
                                sentimentover[profile_country + " of " + mention_country] = [[datetime_object],[score]]



        

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



def quickSortSentimentOver(array, low, high):
  if low < high:

    # find pivot element such that
    # element smaller than pivot are on the left
    # element greater than pivot are on the right
    pi = partition(array, low, high)

    # recursive call on the left of pivot
    quickSortSentimentOver(array, low, pi - 1)

    # recursive call on the right of pivot
    quickSortSentimentOver(array, pi + 1, high)




def partition(array, low, high):
    # choose the rightmost element as pivot
    pivot = array[0][high]

    # pointer for greater element
    i = low - 1

    # traverse through all elements
    # compare each element with pivot
    for j in range(low, high):
        if array[0][j] <= pivot:
            # if element smaller than pivot is found
            # swap it with the greater element pointed by i
            i = i + 1

            # swapping element at i with element at j
            (array[0][i], array[0][j]) = (array[0][j], array[0][i])
            (array[1][i], array[1][j]) = (array[1][j], array[1][i])

    # swap the pivot element with the greater element specified by i
    (array[0][i + 1], array[0][high]) = (array[0][high], array[0][i + 1])
    (array[1][i + 1], array[1][high]) = (array[1][high], array[1][i + 1])

    # return the position from where partition is done
    return i + 1


def workoutAverageSentiment(target_key, target_date):
    averages = [[],[]]
    dates = sentimentover[target_key][0]
    sentiments = sentimentover[target_key][1]

    last_date = 0
    date_date = 0
    to_average = []

    for i in range(len(dates)):
        if dates[i].strftime(target_date) == last_date:
            to_average.append(sentiments[i])

        else:
            
            if len(to_average) > 0:
                averages[0].append(date_date)
                avg = sum(to_average) / len(to_average)
                averages[1].append(avg)


            last_date = dates[i].strftime(target_date) 
            to_average = [sentiments[i]]
            date_date = datetime.strptime(last_date, target_date).date()

    
    averages[0].append(date_date)
    averages[1].append(sum(to_average) / len(to_average))

    return averages



def plotGraph(target_key, target_date, fig_name, total_tweets):
    date = sentimentover[target_key][0]
    sentiment = sentimentover[target_key][1]

    plt.figure(fig_name, figsize=(10,6))

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter(target_date))
    plt.plot(date, sentiment)
    plt.gcf().autofmt_xdate()
    plt.title("Sentiment of " + target_key + " over Time - Total Tweets: " + str(total_tweets))
    plt.xlabel("Date")
    plt.ylabel("Sentiment")

    plt.savefig("output/graphs/" + fig_name)
    plt.close(fig_name)




if __name__ == '__main__':
    startAnalysis()