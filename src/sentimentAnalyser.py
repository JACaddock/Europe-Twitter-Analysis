from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import orjson


analyser = SentimentIntensityAnalyzer()

datafile = open("output/geoEurope_2019120416.json", 'rb')

for line in datafile:
    data = orjson.loads(line)

    for i in data:
        if i == "text":
            vs = analyser.polarity_scores(data[i])
            print(data[i], str(vs))

