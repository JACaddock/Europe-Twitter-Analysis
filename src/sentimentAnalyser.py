from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import orjson, os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime


checked_profile = {}
mentioned = {}
sentiment_over = {}


def startAnalysis(profile_path, sentiment_path, graph_path, do_print):
    if not os.path.isdir("output/" + sentiment_path ):
        if do_print:
            print("Creating sentiment json")
        
        os.mkdir("output/" + sentiment_path)

        checkProfiles(profile_path)
        buildProfiles(profile_path)

        for over in sentiment_over:
            size = len(sentiment_over[over][0])
            quickSortSentimentOver(sentiment_over[over], 0, size - 1)

            sentiment_JSON = open("output/" + sentiment_path + "/" + over +".json", 'wb')
            sentiment_JSON.write(orjson.dumps(sentiment_over[over]))
            sentiment_JSON.close()

        

    else:
        if do_print:
            print("sentiment folder already exists, delete folder if you need to recheck or build profiles")

        for json in os.listdir("output/" + sentiment_path):

            sentiment_JSON = orjson.loads(open("output/" + sentiment_path + "/" + json, 'rb').read())

            for i in range(len(sentiment_JSON[0])):
                sentiment_JSON[0][i] = datetime.strptime(sentiment_JSON[0][i], "%Y-%m-%d").date()


            key = json.replace(".json", "")
            sentiment_over[key] = sentiment_JSON



    if not os.path.isdir("output/" + graph_path):
        os.mkdir("output/" + graph_path)
        
    
    for keys in sentiment_over:

        if len(sentiment_over[keys][0]) > 1:
            total_tweets = len(sentiment_over[keys][1])


            # %Y is YYYY | %m is MM | %d is DD
            target_date = "%d/%m/%Y"
            sentiment_over[keys] = workoutAverageSentiment(keys, target_date)
            plotGraph(keys, target_date, keys+" Day", total_tweets)

            target_date = "%m/%Y"
            sentiment_over[keys] = workoutAverageSentiment(keys, target_date)
            plotGraph(keys, target_date, keys+" Month", total_tweets)



def checkProfiles(profile_path):
    for path in os.listdir("output/" + profile_path):
        for json in os.listdir("output/" + profile_path + "/" + path):
            file = open("output/" + profile_path + "/" + path + "/" + json, 'rb')
            profile = orjson.loads(file.read())

            checked_profile[profile["user"]["id"]] = profile["place"]["country_code"]



def buildProfiles(profile_path):
    for path in os.listdir("output/" + profile_path):
        #scores = [path]
        #print(path)
        
        for json in os.listdir("output/" + profile_path + "/" + path):
            file = open("output/" + profile_path + "/" + path + '/' + json , 'rb')
            profile = orjson.loads(file.read())

            #inmention = False
            checked_profile[profile["user"]["id"]] = profile["place"]["country_code"]

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



                    if mention["id"] in checked_profile:
                        profile_country = profile["place"]["country_code"]
                        mention_country = checked_profile[mention["id"]]

                        if profile_country != mention_country:
                            score = tweetAnalyser(tweet)
                            datetime_object = datetime.strptime(tweet["created_at"], "%a %b %d %X %z %Y").date()

                            #print(profile["user"]["id"], profile_country, mention["id"], mention_country, score, datetime_object)
                            
                            try:
                                sentiment_over[profile_country + " of " + mention_country][0].append(datetime_object)
                                sentiment_over[profile_country + " of " + mention_country][1].append(score)

                            except:
                                sentiment_over[profile_country + " of " + mention_country] = [[datetime_object],[score]]



        

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
    dates = sentiment_over[target_key][0]
    sentiments = sentiment_over[target_key][1]

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



def plotGraph(graph_path, target_key, target_date, fig_name, total_tweets):
    date = sentiment_over[target_key][0]
    sentiment = sentiment_over[target_key][1]

    plt.figure(fig_name, figsize=(10,6))

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter(target_date))
    plt.plot(date, sentiment)
    plt.gcf().autofmt_xdate()
    plt.title("Sentiment of " + target_key + " over Time - Total Tweets: " + str(total_tweets))
    plt.xlabel("Date")
    plt.ylabel("Sentiment")

    plt.savefig("output/" + graph_path + "/" + fig_name)
    plt.close(fig_name)




if __name__ == '__main__':
    startAnalysis("profiles", "sentiment", "graph", False)

    print("Finished Sentiment Analyser")