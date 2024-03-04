import pandas as pd
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from IPython.display import display, HTML
import tiktoken
from openai import OpenAI
import json
import numpy as np

uri = "mongodb+srv://scihanacar:taHaWzcMEymBYp5Z@cluster0.i6uzo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
embedding_encoding = "cl100k_base"
embedding_model = "text-embedding-3-small"
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
openai_client = OpenAI()

def count_tokens(text):
    try:
        return len(encoding.encode(text))
    except Exception as e: 
        return

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


def get_embeddings(text, model):
    response = openai_client.embeddings.create(
        input = text,
        model = model
    )
    cut_dim = response.data[0].embedding[:256]
    return normalize_l2(cut_dim)


try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client['Cluster0']
organization_collection = db['organizations']
org_embedding_collection = db['organization_embeddings_2']

query = {
    '$and': [
        {'website': {'$exists': True}},
        {'website': {'$ne': None}},
        {'website_context': {'$exists': True}},
        {'website_context': {'$ne': None}}
    ]
}

display(organization_collection.count_documents(query))

df = pd.DataFrame(organization_collection.find(query))
df = df[["_id", "organization_name", "last_funding_date","founded_date","headquarters_location","total_funding_amount_currency_in_usd","top_5_investors", "description", "last_funding_type","last_funding_date","estimated_revenue_range","number_of_founders", "website_context", "website_content", 'website_content_tags']]
df.dropna()
df["executive_summary"] = (
    "Company Name: "+ df.organization_name.str.strip() + "\n" +
    "; Founded Date: " + df.founded_date.fillna("Not Specified").str.strip() + "\n"  +
    "; Headquarters Located In: " + df.headquarters_location.fillna("Not Specified").str.strip()+ "\n"  +
    "; Description: " + df.description.fillna("Not Specified").str.strip() +
    "; Total Funding: " + df.total_funding_amount_currency_in_usd.fillna("Not Specified").str.strip() + "\n" +
    "; Last Funding Type: " + df.last_funding_type.fillna("Not Specified").str.strip() + "\n" +
    "; Top 5 Investors: " + df.top_5_investors.fillna("Not Specified").str.strip() + "\n" +
    "; Business Context from the Website: " + df.website_context.str.strip() + "\n" + 
    "; Website Content: " + df.website_content.str.strip()
)

filtered_df = df.dropna(subset=['executive_summary'])

encoding = tiktoken.get_encoding(embedding_encoding)

# omit reviews that are too long to embed
df["n_tokens"] = df.executive_summary.apply(lambda x: count_tokens(x))
df = df.dropna(subset=['n_tokens'])
df["embedding"] = df.executive_summary.apply(lambda x: get_embeddings(x, model=embedding_model))
subset = df[['_id', "executive_summary", 'embedding']]
subset.to_csv('data/organization_executive_summary_embeddings_2.csv')
display(subset)

organization_embeddings = subset.to_dict()
# pretty_organization_embeddings = [{'id' : e['id'], 'executive_summary': e['executive_summary'], 'embedding': json.loads(e['embedding'])} for e in organization_embeddings]
org_embedding_collection.insert_many(organization_embeddings)
client.close()
print(df["embedding"])
# print(len(df))
# display(df)
