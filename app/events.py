import sqlite3
import os

class EventsDB:
    DATABASE_PATH = os.path.join("databases","events.db")
    

    def __init__(self):
        #Connect to local database
        conn = sqlite3.connect(self.DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()

        #Checks if the table exists and creates one if needed
        if c.execute('SELECT tbl_name FROM "main".sqlite_master;').fetchone() == None:
            c.execute('CREATE TABLE "Strings" ("key" TEXT NOT NULL UNIQUE,"value" TEXT, PRIMARY KEY("key"));')
            print("Created new database at '{}',".format(self.DATABASE_PATH))

        #Commit, close and return
        conn.commit()
        conn.close()
        print("Loaded Database.")
        return
    
    def setValue(self, key, value): #POST, PUT
        conn = sqlite3.connect(self.DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()

        if self.hasKey(key):
            c.execute("UPDATE Strings SET value = ? WHERE key = ?", (value,key))
        else:
            c.execute("INSERT INTO Strings VALUES (?,?)",(key,value))
    
        conn.commit()
        conn.close()
        return key,value

    def getValue(self, key): #GET
        conn = sqlite3.connect(self.DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()

        c.execute("SELECT * FROM Strings WHERE key = ?;",(key,))
        result = c.fetchone()
    
        conn.commit()
        conn.close()
        return result

    def deleteKey(self, key): #DELETE
        conn = sqlite3.connect(self.DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()

        c.execute("DELETE FROM Strings WHERE key = ?;",(key,))
        result = c.fetchone()
    
        conn.commit()
        conn.close()
        return key

    def hasKey(self, key):
        conn = sqlite3.connect(self.DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()

        c.execute("SELECT * FROM Strings WHERE key = ?;",(key,))
        result = c.fetchone()
    
        conn.commit()
        conn.close()

        if result == None:
            return False
        else:
            return True
