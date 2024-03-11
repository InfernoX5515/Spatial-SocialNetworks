import os
import csv
from os.path import exists
from datetime import date as Date, timedelta
import numpy as np

dirname = os.path.dirname(__file__)

def keywordTime(inputData, outputData):
    if inputData is not None and exists(inputData):
        with open(inputData, 'r') as csvfile, \
        open(outputData, 'w', newline='') as writeObj:
            
            writer = csv.writer(writeObj)

            # Header row for new data file
            writer.writerow(['id','poi','time'])

            low_date, high_date = Date(2020, 1, 1), Date(2020, 12, 31)
            dates_bet = high_date - low_date
            total_days = dates_bet.days

            csv_reader = csv.reader(csvfile)
            next(csv_reader)
            for row in csv_reader:
                ranNum = np.random.randint(2, 9)
                ranDays = np.random.choice(total_days, ranNum, replace=False)
                res = [low_date + timedelta(days=int(day)) for day in ranDays]
                res.sort()
                for date in res:
                    writer.writerow([row[0],row[1],date])

def main():
    # Name of the input files, has user ids
    gowallaIn = os.path.join(dirname, "../Datasets/SocialNetworks/Gowalla/gowalla_poi.csv")
    gowallaOut = os.path.join(dirname, "../Datasets/SocialNetworks/Gowalla/gowalla_poi_time.csv")

    # Output filse for user attributes
    foursquareIn = os.path.join(dirname, "../Datasets/SocialNetworks/Foursquare/foursquare_poi.csv")
    foursquareOut = os.path.join(dirname, "../Datasets/SocialNetworks/Foursquare/foursquare_poi_time.csv")


    keywordTime(gowallaIn, gowallaOut)
    #keywordTime(foursquareIn, foursquareOut)

    #os.remove(foursquareIn)
    os.remove(gowallaIn)

    #os.rename(foursquareOut, foursquareIn)
    os.rename(gowallaOut, gowallaIn)

if __name__ == '__main__':
    main()

