import csv
from os.path import exists
import os
import random

dirname = os.path.dirname(__file__)

def generateUsrPois(inputData, outputData):
    if inputData is not None and exists(inputData):
        with open(inputData, 'r') as csvfile, \
        open(outputData, 'w', newline='') as writeObj:
            
            writer = csv.writer(writeObj)

            # Header row for new data file
            writer.writerow(['user','poi'])

            csv_reader = csv.reader(csvfile)
            next(csv_reader) # skip header
            for row in csv_reader:
                for i in range(random.randint(10, 25)):
                    # Random Number between 1 - 105725
                    writer.writerow([row[0], random.randint(1, 105725)])

def main():
    # Name of the input files, has user ids
    gowallaIn = os.path.join(dirname, "../Datasets/SocialNetworks/Gowalla/gowalla_loc.csv")
    gowallaOut = os.path.join(dirname, "../Datasets/SocialNetworks/Gowalla/gowalla_poi.csv")

    # Output filse for user attributes
    foursquareIn = os.path.join(dirname, "../Datasets/SocialNetworks/Foursquare/foursquare_loc.csv")
    foursquareOut = os.path.join(dirname, "../Datasets/SocialNetworks/Foursquare/foursquare_poi.csv")


    generateUsrPois(gowallaIn, gowallaOut)
    generateUsrPois(foursquareIn, foursquareOut)

if __name__ == '__main__':
    main()