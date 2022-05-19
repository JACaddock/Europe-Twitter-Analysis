from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import orjson, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np


checked_profile = {} # The ID and Country Code of every profile
baseline_sentiment = {} # The Baseline Sentiments for every country
sentiment_over = {} # The Sentiment that Country A has over Country B
word_sentiment = {"brexit": {}} # The sentiment that each country has of a particular keyword


def startAnalysis(profile_path, sentiment_path, word_path, baseline_path, graph_path, do_print, target_date):
    """
    Starts the analysis

    :param profile_path: 
    :param sentiment_path:
    :param word_path:
    :param baseline_path:
    :param graph_path:
    :param do_print:

    """

    if not os.path.isdir("output/" + sentiment_path ):
        if do_print:
            print("Creating sentiment json")
        

        if do_print:
            print("")
            print("Checking Profiles")

        checkProfiles(profile_path)
        
        if do_print:
            print("Finished Checking Profiles")
            print("")
            print("Building Profiles")
            print("")

        buildProfiles(profile_path, do_print)

        if do_print:
            print("")
            print("Finished Building Profiles")
            print("")


        word_JSON = open("output/" + word_path + ".json", 'wb')
        word_JSON.write(orjson.dumps(word_sentiment))
        word_JSON.close()

        baseline_JSON = open("output/" + baseline_path + ".json", 'wb')
        baseline_JSON.write(orjson.dumps(baseline_sentiment))
        baseline_JSON.close()

        os.mkdir("output/" + sentiment_path)

        for key in sentiment_over:
            size = len(sentiment_over[key][0])
            quickSortSentimentOver(sentiment_over[key], 0, size - 1)

            sentiment_JSON = open("output/" + sentiment_path + "/" + key +".json", 'wb')
            sentiment_JSON.write(orjson.dumps(sentiment_over[key]))
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

        word_JSON = open("output/" + word_path + '.json', 'rb')
        word_sentiment_data = orjson.loads(word_JSON.read())

        for key in word_sentiment_data:
            word_sentiment[key] = word_sentiment_data[key]

        word_JSON.close()

        baseline_JSON = open("output/" + baseline_path + ".json", 'rb')
        baseline_sentiment_data = orjson.loads(baseline_JSON.read())

        for key in baseline_sentiment_data:
            baseline_sentiment[key] = baseline_sentiment_data[key]

        baseline_JSON.close()


    if not os.path.isdir("output/" + graph_path):
        os.mkdir("output/" + graph_path)
    
    if not os.path.isdir("output/" + graph_path + "/sentiment_over"):
        os.mkdir("output/" + graph_path + "/sentiment_over")
    
    if not os.path.isdir("output/" + graph_path + "/baselines"):
        os.mkdir("output/" + graph_path + "/baselines")

    if not os.path.isdir("output/" + graph_path + "/keywords"):
        os.mkdir("output/" + graph_path + "/keywords")
        
    if do_print:
        print("Plotting Graphs")

    # Keywords graphs

    for keyword in word_sentiment:
        if not os.path.isdir("output/" + graph_path + "/keywords/" + keyword):
            os.mkdir("output/" + graph_path + "/keywords/" + keyword)

        country_word_dict = calculateSentiment(word_sentiment[keyword])

        for key in country_word_dict:
            plotWordGraph(key, graph_path, keyword, [country_word_dict[key][0], country_word_dict[key][1]], country_word_dict[key][1])







    # Baseline Sentiment graphs

    country_baseline_dict = calculateSentiment(baseline_sentiment)

    for key in country_baseline_dict:
        plotBaselineGraph("Top tweeted " + key + " - " + str(len(country_baseline_dict[key][1]) + int(key) - 1), graph_path, [country_baseline_dict[key][0], country_baseline_dict[key][1]], country_baseline_dict[key][2])
    





    # Sentiment Over graphs

    for keys in sentiment_over:

        if len(sentiment_over[keys][0]) > 1:
            total_tweets = len(sentiment_over[keys][1])

            for target in target_date:
                try:
                    sentiment_over[keys] = calculateAverageSentiment(keys, target_date[target])
                    plotSentimentOverGraph(graph_path, keys, target_date[target], keys+" " + target, total_tweets)
                
                except:
                    if do_print:
                        print("Couldn't create " + target + " Graph for " + keys)




def checkProfiles(profile_path):
    """
    Counts every profile we have and adds them to the check_profile dictionary

    :param profile_path: String of the path that points to the folder that holds all the profiles
    """
    
    for path in os.listdir("output/" + profile_path):
        for json in os.listdir("output/" + profile_path + "/" + path):
            profile_id = json.replace(".json", "")

            checked_profile[int(profile_id)] = path



def buildProfiles(profile_path, do_print):
    """
    Scores every tweet from every profile, adds that score to the profile, baseline_sentiment, 
    word_sentiment and sentiment_over dictionaries

    :param profile_path: String of the path that points to the folder that holds all the profiles
    :param do_print: Boolean that determines whether the program should output helpful information
    """
    
    if do_print:
        max_countries = len([name for name in os.listdir("output/" + profile_path)])
        num = 1

    for profile_country in os.listdir("output/" + profile_path):
        
        for json in os.listdir("output/" + profile_path + "/" + profile_country):
            profile_file = open("output/" + profile_path + "/" + profile_country + '/' + json , 'rb')
            profile = orjson.loads(profile_file.read())
            profile_file.close()

            scored_tweets = []
        
            for tweet in profile["tweets"]:
                try:
                    score = tweet["score"]
                    
                except:
                    score = tweetAnalyser(tweet)
                    

                scored_tweets.append({ "created_at": tweet["created_at"], "lang": tweet["lang"], "text": tweet["text"], "entities": tweet["entities"], "id": tweet["id"], "place": tweet["place"], "score": score })
                zero_score = (score + 1) / 2
                

                try:
                    baseline_sentiment[profile_country].append(zero_score)

                except:
                    baseline_sentiment[profile_country] = [zero_score]

                for word in word_sentiment:
                    if word in tweet["text"].lower():
                        try:
                            word_sentiment[word][profile_country].append(zero_score)

                        except:
                            word_sentiment[word][profile_country] = [zero_score]


                mentions = tweet["entities"]["user_mentions"]
                for mention in mentions:

                    if mention["id"] in checked_profile:
                        mention_country = checked_profile[mention["id"]]

                        if profile_country != mention_country:
                    
                            datetime_object = datetime.strptime(tweet["created_at"], "%a %b %d %X %z %Y").date()
                            
                            try:
                                sentiment_over[profile_country + " of " + mention_country][0].append(datetime_object)
                                sentiment_over[profile_country + " of " + mention_country][1].append(score)

                            except:
                                sentiment_over[profile_country + " of " + mention_country] = [[datetime_object],[score]]
            
            
            

            profile_add = open("output/" + profile_path + "/" + profile_country + "/" + json, 'wb')
            profile_add.write(orjson.dumps({ "user": profile["user"], "place": profile["place"], "mentions": profile["mentions"], "tweets" : scored_tweets }))
            profile_add.close()
                        


        if do_print:
            print("Finished country: " + profile_country +" - " + str(num) + "/" + str(max_countries))
            num += 1




        

def tweetAnalyser(tweet):
    """
    Uses Vader Sentiment to analyse a tweet and returns that score

    :param tweet: A JSON converted into a python dictionary of a single tweet and it's metadata

    :return score: The score given to the text of the tweet, ranging from -1 to 1
    """
    
    analyser = SentimentIntensityAnalyzer()
    
    text = tweet["text"]
    vs = analyser.polarity_scores(text)

    return vs['compound']



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




def calculateAverageSentiment(target_key, target_date):
    """
    Calculates the average sentiment for one country to another within a given time frame
    
    :param target_key: The key for the sentiment_over dictionary
    :param target_date: A string of the desired date to be averaged over

    :return averages: A list containing the new dates and averages for the sentiment_over
    """
    
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



def plotSentimentOverGraph(graph_path, target_key, target_date, fig_name, total_tweets):
    """
    Creates a graph for a given countries sentiment towards another's within a given average

    :param graph_path: The path that points to where you want the graphs to be outputted
    :param target_key: The key for the sentiment_over dictionary
    :param target_date: A string of the desired date to be averaged over
    :param fig_name: A name for the figure
    :param total_tweets: The total number of tweets used for the graph
    """
    
    date = sentiment_over[target_key][0]
    sentiment = sentiment_over[target_key][1]

    plt.figure(fig_name, figsize=(10,6))

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter(target_date))
    plt.plot(date, sentiment)
    plt.gcf().autofmt_xdate()
    plt.title("Sentiment of " + target_key + " over Time - Total Tweets: " + str(total_tweets))
    plt.xlabel("Date")
    plt.ylabel("Sentiment")

    plt.savefig("output/" + graph_path + "/sentiment_over/" + fig_name)
    plt.close(fig_name)




def calculateSentiment(countries):
    """
    Calculates every countries mean sentiment and error sentiments within a dictionaries
    """
    
    errors = {}
    country_intensity = [[],[]]

    for country in countries:
        sentiments = countries[country]

        errors[country] = np.std(sentiments)
        countries[country] = np.mean(sentiments)

        country_intensity[1].append(country)
        country_intensity[0].append(len(sentiments))


    size = len(country_intensity[0])
    quickSortSentimentOver(country_intensity, 0, size - 1)
    country_intensity[0].reverse()
    country_intensity[1].reverse()


    if size < 5:
        divider = size

    else:
        divider = 5

    
    increment = divider
    countries_data = {"1" : [[],[],[],[]]}
    count = 1


    for i in range(size-1):
        countries_data[str(count)][0].append(country_intensity[1][i])
        countries_data[str(count)][1].append(countries[country_intensity[1][i]])
        countries_data[str(count)][2].append(errors[country_intensity[1][i]])
        countries_data[str(count)][3].append(country_intensity[0][i])

        if i == divider - 1:
            count = i + 2
            divider += increment

            countries_data[str(count)] = [[],[],[],[]]

        elif i >= size - 2:
            countries_data[str(count)][0].append(country_intensity[1][i+1])
            countries_data[str(count)][1].append(countries[country_intensity[1][i+1]])
            countries_data[str(count)][2].append(errors[country_intensity[1][i+1]])
            countries_data[str(count)][3].append(country_intensity[0][i+1])


    
    return countries_data



def plotBaselineGraph(fig_name, graph_path, countries, err):
    """
    Creates a bar chart of each countries baseline sentiment
    
    :param graph_path: The path that points to where you want the graphs to be outputted
    """

    fig, ax = plt.subplots()
    ax.bar(countries[0], countries[1], yerr=err, align='center', alpha=0.5, ecolor='black', capsize=10)
    ax.set_ylabel('Sentiment from 0 to 1')
    ax.set_xticks(countries[0])
    ax.yaxis.grid(True)

    plt.tight_layout()
    plt.savefig("output/" + graph_path + "/baselines/" + fig_name )

    plt.close()



def plotWordGraph(fig_name, graph_path, word_key, countries, sentiments):

    plt.bar(countries[0], countries[1], align='center', alpha=0.5, capsize=10, data=sentiments)

    plt.title("Sentiment of different countries towards the keyword Brexit")

    plt.tight_layout()
    plt.savefig("output/" + graph_path + "/keywords/" + word_key + "/" + fig_name)

    plt.close()




if __name__ == '__main__':
    # target_date - %Y is YYYY | %m is MM | %d is DD
    target_date = { "Day" : "%d/%m/%Y", "Month" : "%m/%Y" }

    

    startAnalysis("profiles", "sentiment", "words", "baseline", "graph", True, target_date)

    print("Finished Sentiment Analyser")

    #for word, countries in word_sentiment.items():
        #for country, values in countries.items():
            #print(word + " was mentioned by " + country, len(values), "times")