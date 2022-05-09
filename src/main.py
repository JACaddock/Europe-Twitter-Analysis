import os.path
import dataSorter as ds
import sentimentAnalyser as sa


if __name__ == "__main__":
    print("")
    demo = input("Is this the demo? (Y/N) : ")
    print("")

    if demo.lower() == "y" or demo.lower() == "yes":

        ds.keywords = {'en': ["home", "hate"]}
        ds.supported_languages = ['en']

        ds.sortFolder("input/zips", 2019120416, 2020120416, False)
        print(ds.keywords)

        sa.startAnalysis("profiles", "sentiment", "graph", False)
    
    else:
        print("")
        demo = input("Is this the demo? (Y/N) : ")
        print("")
