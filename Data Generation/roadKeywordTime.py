
import os
import csv
from os.path import exists
from datetime import date, timedelta
import numpy as np

dirname = os.path.dirname(__file__)

def poiTime(inputData, outputData):
    if inputData is not None and exists(inputData):
        with open(inputData, 'r') as csvfile, \
        open(outputData, 'w', newline='') as writeObj:
            
            writer = csv.writer(writeObj)

            # Header row for new data file

            low_date, high_date = date(2020, 1, 1), date(2020, 12, 31)
            dates_bet = high_date - low_date
            total_days = dates_bet.days

            csv_reader = csv.reader(csvfile)
            next(csv_reader)
            for row in csv_reader:
                ranDays = np.random.choice(total_days, 2, replace=False)
                res = [low_date + timedelta(days=int(day)) for day in ranDays]
                res.sort()
                writer.writerow([row[0],row[1],res[0],res[1]])

def main():
    # Name of the input files, has user ids
    californiaIn = os.path.join(dirname, "../Datasets/RoadNetworks/california_poi_key.csv")

    # Output filse for user attributes
    californiaOut = os.path.join(dirname, "../Datasets/RoadNetworks/california_poi_key_time.csv")


    poiTime(californiaIn, californiaOut)

    os.remove(californiaIn)

    os.rename(californiaOut, californiaIn)

if __name__ == '__main__':
    main()