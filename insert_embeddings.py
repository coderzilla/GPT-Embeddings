import csv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json
import numpy as np

organization_dictionary_list = []
with open('data/organization_executive_summary_embeddings_2.csv', 'r', encoding='utf-8') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        organization_id = row["_id"]
        executive_summary = row["executive_summary"]
        embeddings = row["embedding"]
        embedding_str_cleaned = embeddings.strip("[]")

# Step 2: Split the string by spaces
        embedding_str_values = embedding_str_cleaned.split()

        # Step 3: Convert each string to float
        embedding_values = [float(value) for value in embedding_str_values]

        # Step 4: The result is already in array form as a list, but let's explicitly show it
        embedding_array = embedding_values

        
        organization_dictionary_list.append({'organization_id':organization_id, 'text': executive_summary, 'embedding':embedding_array})

uri = "mongodb+srv://scihanacar:taHaWzcMEymBYp5Z@cluster0.i6uzo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client['Cluster0']
collection = db['organization_embeddings_256']

collection.insert_many(organization_dictionary_list)


client.close()