import os.path
import dataSorter as ds
import sentimentAnalyser as sa


if __name__ == "__main__":
    ds.keywords = {'en': ["home", "hate"]}
    ds.supported_languages = ['en']



    ds.sortFolder("zips")
    print(ds.keywords)

    sa.showProfiles()