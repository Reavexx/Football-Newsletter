from pymongo import MongoClient
import os

# Read environment variables from file
with open('/usr/app/src/Newsletter_Volume/envvar.txt', 'r') as file:
    for line in file:
        line = line.strip()
        if line:
            key, value = line.split('=', 1)
            os.environ[key] = value

col = MongoClient(os.getenv("GET_MONGO_CONSTRING"))["Newsletter"]["Subscribers"]

# col = MongoClient("mongodb+srv://admin:iC7ffk929AhXNKAb@footballnewsletter.unfcjpx.mongodb.net/?retryWrites=true&w=majority")["Newsletter"]["Subscribers"]


class Db:
    def rmSub(Email):  
        lower_email = Email.lower()
        # set query to value of email      
        query = { "E-Mail": lower_email }

        # remove email from db
        col.delete_one(query)
        return
    
    def addSub(Email):
        lower_email = Email.lower()
        # set module for insert
        module = { "E-Mail": Email }

        # add email to db
        col.insert_one(module)