from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


uri = "mongodb+srv://scihanacar:taHaWzcMEymBYp5Z@cluster0.i6uzo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


db = client['Cluster0']
collection = db['organizations']

# Aggregate all unique values for 'fieldName'
pipeline = [
    {
        '$group': {
            '_id': None,  # Group all documents together
            'allUniqueValues': {'$addToSet': '$website_content'}  # Collect unique values of 'fieldName'
        }
    }
]

results = collection.aggregate(pipeline)

for result in results:
    print(result['allUniqueValues'])