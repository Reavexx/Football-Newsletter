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
    def getSubs():
        # Get all emails
        Subs = col.find({})

        # Add emails to list
        SubsList = []
        for e in Subs:
            SubsList.append(e['E-Mail'])
        return SubsList