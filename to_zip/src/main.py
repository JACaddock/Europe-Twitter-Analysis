import dataSorter as ds
import sentimentAnalyser as sa


if __name__ == "__main__":
    print("You have the option to do preprocessing")
    print("It may take some time depending on your machine")
    print("There are processed versions of the data already prepared to save your time")
    preprocessing = input("Would like to see preprocessing? (Y/N) : ")


    if preprocessing.lower() == "y" or preprocessing.lower() == "yes":
        ds.keywords_activated = True
        ds.startSorter("input/demo", 2020013123, 2020020300)

        profile_path = "profiles"

    else:
        profile_path = "preprocessed/profiles"


    print("Starting Sentiment Analyser")

    # target_date - %Y is YYYY | %m is MM | %d is DD
    target_date = { "Day" : "%d/%m/%Y"}

    sa.startAnalysis(profile_path, "sentiment", "words", "baseline", "graph", True, target_date)

    print("Finished Sentiment Analyser")
    print("")
    print("Look in output/graph for the graphs")
    
