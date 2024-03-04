import pandas as pd
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from IPython.display import display, HTML
import tiktoken
from openai import OpenAI
import ast  # for converting embeddings saved as strings back to arrays
import os # for getting API token from env variable OPENAI_API_KEY
from scipy import spatial
import numpy as np

EMBEDDING_MODEL = "text-embedding-3-small"
GPT_MODEL = "gpt-4-0125-preview"
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

df = pd.DataFrame(collection.find({}, {'text': 1, 'embedding': 1, '_id': 0}))

openai_client = OpenAI()

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

def strings_ranked_by_relatedness(
    query: str,
    df: pd.DataFrame,
    relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
    top_n: int = 100
) -> tuple[list[str], list[float]]:
    """Returns a list of strings and relatednesses, sorted from most related to least."""
    query_embedding = get_embeddings(query, EMBEDDING_MODEL)
    # query_embedding = normalize_l2(query_embedding_response.data[0].embedding[:256])
    # query_embedding_response = openai_client.embeddings.create(
    #     model=EMBEDDING_MODEL,
    #     input=query,
    # )
    # query_embedding = query_embedding_response.data[0].embedding
    strings_and_relatednesses = [
        (row["text"], relatedness_fn(query_embedding, row["embedding"]))
        for i, row in df.iterrows()
    ]
    strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
    strings, relatednesses = zip(*strings_and_relatednesses)
    return strings[:top_n], relatednesses[:top_n]

def num_tokens(text: str, model: str = GPT_MODEL) -> int:
    """Return the number of tokens in a string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def query_message(
    query: str,
    df: pd.DataFrame,
    model: str,
    token_budget: int
) -> str:
    """Return a message for GPT, with relevant source texts pulled from a dataframe."""
    strings, relatednesses = strings_ranked_by_relatedness(query, df)
    introduction = 'The information given is related with the AI startups around the world that were founded in 1 year. Use this information to answer the subsequent question. If the answer cannot be found in the informations, write "I could not find an answer."'
    question = f"\n\nQuestion: {query}"
    message = introduction
    for string in strings:
        next_article = f'\n\Company Information section:\n"""\n{string}\n"""'
        if (
            num_tokens(message + next_article + question, model=model)
            > token_budget
        ):
            break
        else:
            message += next_article
    return message + question


def ask(
    query: str,
    df: pd.DataFrame = df,
    model: str = GPT_MODEL,
    token_budget: int = 8192 - 500,
    print_message: bool = False,
    assistants = None
) -> str:
    """Answers a query using GPT and a dataframe of relevant texts and embeddings."""
    message = query_message(query, df, model=model, token_budget=token_budget)
    if print_message:
        print(message)
    
    messages = [
        {"role": "system", "content": "You are an business adviser and You answer questions about the AI Startups that were founded in last 1 year using the information given."},
        {"role" : "assistant", "content" : "Not Specified means we do not have the information."},
        {"role": "user", "content": message},
    ]
    response = openai_client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )
    response_message = response.choices[0].message.content
    return response_message

print(ask('With the information given, which industries you suggest an entrepreneur who want to implement AI into to dive in', print_message=True, model="gpt-3.5-turbo"))
# strings, relatednesses = strings_ranked_by_relatedness("Health Tech", df, top_n=5)
# for string, relatedness in zip(strings, relatednesses):
#     print(f"{relatedness=:.3f}")
#     display(string)
