import csv
import csv
from os.path import exists
from Config import Config
import random    

class KeywordGeneration:
    def __init__(self):
        #
        # INSTRUCTIONS:
        # Update below path names and below variable then run
        #
        self.numOfKeywords = 200
        self.chooseKeywords = 20

        print("KEYWORD GENERATOR: ")
        self.generateSocialKeywords(path="./Datasets/SocialNetworks/gowalla_loc.csv", name="./Datasets/SocialNetworks/gowalla_keywords.csv")
        print('Gowalla Done!')
        self.generateSocialKeywords(path='./Datasets/SocialNetworks/foursquare_loc.csv', name="./Datasets/SocialNetworks/foursquare_keywords.csv")
        print('Foursquare Done!')

    def generateSocialKeywords(self, path=None, name='out.csv'):
        if 1 == 1:
            with open(path, 'r') as readObj, \
                    open(name, 'w', newline='') as writeObj:
                reader = csv.reader(readObj, delimiter=',', quotechar='|')
                writer = csv.writer(writeObj)
                
                # Add header to output file
                writer.writerow(['user_id','keyword_id'])
                next(reader)
                for row in reader:
                    user_id = row[0]
                    randNums = random.sample(range(self.numOfKeywords), self.chooseKeywords+1)
                    for x in range(self.chooseKeywords):
                        writer.writerow([user_id, randNums[x]])


def main():
    test = KeywordGeneration()

if __name__ == '__main__':
    main()
