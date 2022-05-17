import csv
from os.path import exists
import sqlite3
from turtle import distance

class queryTest:
    def __init__(self):
        self.connection = sqlite3.connect("dataset.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute("SELECT KeywordMap.UserID FROM KeywordMap JOIN UserLocations UL ON KeywordMap.UserID = UL.UserID WHERE KeywordID = 8 AND SocialNetwork=1")
        self.cursor.execute("INTERSECT")
        self.cursor.execute("SELECT KeywordMap.UserID FROM KeywordMap JOIN UserLocations UL ON KeywordMap.UserID = UL.UserID WHERE KeywordID = 12 AND SocialNetwork=1")
        rows = self.cursor.fetchall()

        for row in rows:
            print(row)


def main():
    test = queryTest()

if __name__ == '__main__':
    main()