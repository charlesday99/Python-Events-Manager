from PIL import Image
import sqlite3
import os

#Class for storing image filenames, titles and
#captions in a database.
class ImagesDB:
    #Database path and name
    APP_DIR = os.path.dirname(os.path.realpath(__file__))
    DATABASE_PATH = os.path.join(APP_DIR,"images.db")
    IMAGE_PATH = os.path.join(APP_DIR,"static","content")
    THUMBNAIL_PATH = os.path.join(APP_DIR,"static","content","thumbnails")
    THUMBNAIL_PATH_LG = os.path.join(APP_DIR,"static","content","thumbnails_lg") ## Added by Kane x 

    def __init__(self):
        #Connect to local database
        self.connection = sqlite3.connect(self.DATABASE_PATH, check_same_thread=False)
        self.cursor = self.connection.cursor()

        #Checks if the table exists and creates one if needed
        if self.cursor.execute('SELECT tbl_name FROM "main".sqlite_master;').fetchone() == None:
            self.cursor.execute('CREATE TABLE "Images" ("ID" INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,"title" TEXT NOT NULL,"caption" TEXT,"filename" TEXT NOT NULL)')
            print("Created new database at '{}'.".format(self.DATABASE_PATH))

        #Check that each folder for the images exists,
        #and create then if they do not
        if not os.path.exists(self.IMAGE_PATH):
            os.makedirs(self.IMAGE_PATH)
        if not os.path.exists(self.THUMBNAIL_PATH):
            os.makedirs(self.THUMBNAIL_PATH)
        if not os.path.exists(self.THUMBNAIL_PATH_LG):
            os.makedirs(self.THUMBNAIL_PATH_LG)

        #Commit and return
        self.connection.commit()
        print("Loaded Images database.")
        return

    #Upload a new image and create a thumbnail for it
    def addImage(self, img, filename, title, caption):
        #Check that the image isnt already uploaded
        if (not self.hasImage(filename)):
            #Convert to RGB if a PNG was uploaded
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            #Save the image
            img.save(os.path.join(self.IMAGE_PATH,filename))
            #Save image as 500x500 for tile image
            img.thumbnail((500,500))
            img.save(os.path.join(self.THUMBNAIL_PATH_LG,filename))
            #Save image as 140x140 for thumbnail image
            img.thumbnail((140,140))
            img.save(os.path.join(self.THUMBNAIL_PATH,filename))
            #Insert image into db
            self.cursor.execute("INSERT INTO Images VALUES (NULL,?,?,?)",(title,caption,filename))
            self.connection.commit()

    #Get an Image by its filename
    def getImage(self, filename):
        self.cursor.execute("SELECT * FROM Images WHERE filename = ?;",(filename,))
        return self.cursor.fetchone()

    #Update an Image title
    def updateTitle(self, filename, title):
        self.cursor.execute("UPDATE Images SET title = ? WHERE filename = ?",(title,filename))
        self.connection.commit()

    #Update an Image caption
    def updateCaption(self, filename, caption):
        self.cursor.execute("UPDATE Images SET caption = ? WHERE filename = ?",(caption,filename))
        self.connection.commit()

    #Delete an Image by its filename
    def deleteImage(self, filename):
        os.remove(os.path.join(self.IMAGE_PATH,filename))
        os.remove(os.path.join(self.THUMBNAIL_PATH,filename))
        os.remove(os.path.join(self.THUMBNAIL_PATH_LG,filename))
        self.cursor.execute("DELETE FROM Images WHERE filename = ?;",(filename,))
        self.connection.commit()

    #Check if the database has an filename
    def hasImage(self, filename):
        self.cursor.execute("SELECT * FROM Images WHERE filename = ?;",(filename,))
        return self.cursor.fetchone() is not None

    #Return all of the data
    def dump(self):
        self.cursor.execute("SELECT * FROM Images;")
        return self.cursor.fetchall()

    #Destructor closes DB connection
    def __del__(self):
        print("Closing Images database.")
        self.connection.close()
