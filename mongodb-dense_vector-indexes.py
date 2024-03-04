from embedding_utils import (
    get_embedding,
    distances_from_embeddings,
    tsne_components_from_embeddings,
    chart_from_components,
    chart_from_components_3D,
    indices_of_nearest_neighbors_from_distances,
)
import pandas as pd
import pickle
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
import redis
import json
import numpy as np
from sklearn.model_selection import train_test_split

r = redis.Redis(host="localhost", port=6379, db=0)
EMBEDDING_MODEL = "text-embedding-3-small"
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
org_collection = db["organizations"]
collection = db['organization_embeddings_256']
documents = collection.find({}, {'organization_id': 1, 'embedding': 1, '_id': 0})
# embeddings = [doc['embedding'] for doc in documents if 'embedding' in doc]
org_embedding_dict = r.get('organization:embedding')
if org_embedding_dict is None:
    org_embedding_dict = []
    for doc in documents: 
        embedding = doc['embedding']
        organization_id = ObjectId(doc['organization_id'])
        organization = org_collection.find_one({'_id': organization_id}, {'organization_name':1, "_id": 0})
        org_embedding_dict.append({'organization': organization['organization_name'], 'embedding':embedding})
    r.set('organization:embedding', json.dumps(org_embedding_dict))
else:
    org_embedding_dict = json.loads(org_embedding_dict)


organizations = [d["organization"] for d in org_embedding_dict if "organization" in d]
embeddings = [d["embedding"] for d in org_embedding_dict if "embedding" in d]
tra
def normalize_l2(x):
    x = np.array(x)
    if x.ndim == 1:
        norm = np.linalg.norm(x)
        if norm == 0:
            return x
        return x / norm
    else:
        norm = np.linalg.norm(x, 2, axis=1, keepdims=True)
        return np.where(norm == 0, x, x / norm)

def print_recommendations_from_strings(
    strings: list[str],
    index_of_source_string: int,
    k_nearest_neighbors: int = 1,
    model=EMBEDDING_MODEL,
) -> list[int]:
    """Print out the k nearest neighbors of a given string."""
    # get embeddings for all strings
    # embeddings = [embedding_from_string(string, model=model) for string in strings]

    # get the embedding of the source string
    query_embedding = embeddings[index_of_source_string]
    # query_embedding = get_embedding("Saas startups using AI")[:256]
    # query_embedding = normalize_l2(query_embedding).tolist()

    pipeline = [
    {
            "$vectorSearch": {
                "index": "vector_index",
                "path" : "embedding",  # Replace with the name of your dynamic index
                "queryVector" : query_embedding,
                "limit": 10,
                "numCandidates" : 10
            }
        },
    ]

    results = collection.aggregate(pipeline)

    for result in results:
        
        organization_id = ObjectId(result['organization_id'])
        organization = org_collection.find_one({'_id': organization_id}, {'organization_name':1,"website_context":1, "_id": 0})
        print(f"Organization: {organization["organization_name"]} \nBusiness Context: {organization["website_context"]}")

    # get distances between the source embedding and other embeddings (function from utils.embeddings_utils.py)
    distances = distances_from_embeddings(query_embedding, embeddings, distance_metric="cosine")
    
    # get indices of nearest neighbors (function from utils.utils.embeddings_utils.py)
    indices_of_nearest_neighbors = indices_of_nearest_neighbors_from_distances(distances)

    # print out source string
    query_string = organizations[index_of_source_string]
    print(f"Source string: {query_string}")
    # print out its k nearest neighbors
    k_counter = 0
    for i in indices_of_nearest_neighbors:
        # skip any strings that are identical matches to the starting string
        if query_string == strings[i]:
            continue
        # stop after printing out k articles
        if k_counter >= k_nearest_neighbors:
            break
        k_counter += 1

        # print out the similar strings and their distances
        print(
            f"""
        --- Recommendation #{k_counter} (nearest neighbor {k_counter} of {k_nearest_neighbors}) ---
        String: {strings[i]}
        Distance: {distances[i]:0.3f}"""
        )
    print(k_counter)
    return indices_of_nearest_neighbors


tony_blair_articles = print_recommendations_from_strings(
    strings=organizations,  # let's base similarity off of the article description
    index_of_source_string=77,  # articles similar to the first one about Tony Blair
    k_nearest_neighbors=15,  # 5 most similar articles
)

tsne_components = tsne_components_from_embeddings(embeddings, n_components=3)
# get the article labels for coloring the chart


chart_from_components_3D(
    components=tsne_components,
    labels=organizations,
    strings=organizations,
    width=1200,
    height=1000,
    title="t-SNE components of article descriptions",
)