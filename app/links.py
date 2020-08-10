import sqlite3
import os

#Database and methods for storing and manipulating
#URLs and thier respective counters
class LinksDB:
    #Database path and name
    APP_DIR = os.path.dirname(os.path.realpath(__file__))
    DATABASE_PATH = os.path.join(APP_DIR,"links.db")

    def __init__(self):
        #Connect to local database
        self.connection = sqlite3.connect(self.DATABASE_PATH, check_same_thread=False)
        self.cursor = self.connection.cursor()

        #Checks if the table exists and creates one if needed
        if self.cursor.execute('SELECT tbl_name FROM "main".sqlite_master;').fetchone() == None:
            self.cursor.execute('CREATE TABLE "Links" ("ID" INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,"URL" TEXT NOT NULL,"Count" INTEGER)')
            print("Created new database at '{}'.".format(self.DATABASE_PATH))

        #Commit and return
        self.connection.commit()
        print("Loaded Links database.")
        return

    #Create a new link
    def createLink(self, URL):
        if (not self.hasURL(URL)):
            self.cursor.execute("INSERT INTO Links VALUES (NULL,?,0)",(URL,))
            self.connection.commit()
        return self.getID(URL)
    
    #Get a link by its ID
    def getLink(self, ID):
        self.cursor.execute("SELECT * FROM Links WHERE ID = ?;",(ID,))
        return self.cursor.fetchone()

    #Get a ID by its URL
    def getID(self, URL):
        self.cursor.execute("SELECT * FROM Links WHERE URL = ?;",(URL,))
        return self.cursor.fetchone()

    #Update a Links URL
    def updateLink(self, ID, URL):
        self.cursor.execute("UPDATE Links SET URL = ? WHERE ID = ?", (URL,ID))
        self.connection.commit()

    #Delete a link by its ID
    def deleteLink(self, ID):
        self.cursor.execute("DELETE FROM Links WHERE ID = ?;",(ID,))
        self.connection.commit()

    #Check if the database has a URL
    def hasURL(self, URL):
        self.cursor.execute("SELECT * FROM Links WHERE URL = ?;",(URL,))
        return self.cursor.fetchone() is not None

    #Check if the database has an ID
    def hasID(self, ID):
        self.cursor.execute("SELECT * FROM Links WHERE ID = ?;",(ID,))
        return self.cursor.fetchone() is not None

    #Iterate the counter of the given ID
    def addCounter(self, ID):
        self.cursor.execute("UPDATE Links SET Count = Count + 1 WHERE ID = ?", (ID,))
        self.connection.commit()

    #Reset the counter of the given ID
    def resetCounter(self, ID):
        self.cursor.execute("UPDATE Links SET Count = 0 WHERE ID = ?", (ID,))
        self.connection.commit()

    #Return all of the data
    def dump(self):
        self.cursor.execute("SELECT * FROM Links;")
        return self.cursor.fetchall()

    #Destructor closes DB connection
    def __del__(self):
        print("Closing Links database.")
        self.connection.close()