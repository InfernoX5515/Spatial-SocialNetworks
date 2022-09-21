import faker
import csv
from os.path import exists
import os
import random as r

dirname = os.path.dirname(__file__)

faker_obj = faker.Faker()

def generateUsrAttributes(inputData, outputData):
    if inputData is not None and exists(inputData):
        with open(inputData, 'r') as csvfile, \
        open(outputData, 'w', newline='') as writeObj:
            
            writer = csv.writer(writeObj)

            # Header row for new data file
            writer.writerow(['id','username','name','email','birthdate','phone'])

            csv_reader = csv.reader(csvfile)
            next(csv_reader) # skip header
            for row in csv_reader:
                # Generate phone number
                # Generate random data for each row in input
                profile = faker_obj.simple_profile()
                writer.writerow([row[0],profile["username"],profile["name"], profile["mail"],profile["birthdate"], faker_obj.phone_number()])

# Name of the input files, has user ids
gowallaIn = os.path.join(dirname, "../Datasets/SocialNetworks/Gowalla/gowalla_loc.csv")
gowallaOut = os.path.join(dirname, "../Datasets/SocialNetworks/Gowalla/gowalla_user.csv")

# Output filse for user attributes
foursquareIn = os.path.join(dirname, "../Datasets/SocialNetworks/Foursquare/foursquare_loc.csv")
foursquareOut = os.path.join(dirname, "../Datasets/SocialNetworks/Foursquare/foursquare_user.csv")


generateUsrAttributes(gowallaIn, gowallaOut)
generateUsrAttributes(foursquareIn, foursquareOut)


