import csv
from os.path import exists
import sqlite3
from turtle import distance

class queryTest:
    def __init__(self):
        self.connection = sqlite3.connect("dataset.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute("SELECT * FROM UserLocations WHERE SocialNetwork = ?", (1,))
        rows = self.cursor.fetchall()

        for row in rows:
            print(row)


def main():
    test = queryTest()

if __name__ == '__main__':
    main()