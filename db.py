#
# module db
# contains database helper functions for pwsafe.py
#
# config is a ConfigParser object
# args is the result of argparse
# category means the selected category, expected to be !all
#
import os
import sqlite3

#
# construct db name from category and config file
#
def getDataBaseFile(config, category):
    dbBaseDir = config.get('DEFAULT', 'dbbasedir')
    dbBaseDir = os.path.expanduser(dbBaseDir)
    if not os.path.isdir(dbBaseDir):
        os.makedirs(dbBaseDir)

    dbName = dbBaseDir + '/' + config.get(category, 'db')
    return dbName



def initializeDataBase(config, category):
    dbName = getDataBaseFile(config, category)
    dbConnection = None

    if not os.path.isfile(dbName):
        try:
            dbConnection = sqlite3.connect(dbName)
            cur = dbConnection.cursor()
            cur.execute("CREATE TABLE Accounts(Id INT PRIMARY KEY, Name TEXT, Comment TEXT, Url TEXT, User Text, Length INT, Password TEXT)")

        except sqlite3.Error, e:
            print "Error %s:" % e.args[0]
            sys.exit(1)

        finally:
            if dbConnection:
                dbConnection.close()

    dbConnection = sqlite3.connect(dbName)
    return dbConnection
