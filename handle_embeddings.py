import requests
import csv
from pymongo import MongoClient
import configparser
import sys

csv.field_size_limit(sys.maxsize)

config = configparser.ConfigParser()
config.read('config.ini')

# MongoDB 
MONGO_CONNECTION_STRING = config.get('SECRETS', 'MONGO_CONNECTION_STRING')
DB_NAME = config.get('MONGO_DB', 'DB_NAME')
COLLECTION_NAME = config.get('MONGO_DB', 'COLLECTION_NAME')
# MongoDB vector search
EMBEDDING_FIELD = config.get('VECTOR_SEARCH', 'EMBEDDING_FIELD')
INDEX = config.get('VECTOR_SEARCH', 'INDEX')
SEARCH_LIMIT = config.get('VECTOR_SEARCH', 'SEARCH_LIMIT')
CANDIDATES_NUMBER = config.get('VECTOR_SEARCH', 'CANDIDATES_NUMBER')
# Hugging Face
HF_API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
HF_TOKEN = config.get('SECRETS', 'HF_ACCESS_TOKEN')
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

def read_csv(csv_filename):
    data = []
    with open(csv_filename, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            url, title, content = row['Url'], row['Title'], row['Content']
            data.append({'url': url, 'title': title, 'content': content})

    return data

def generate_embedding(text):
    response = requests.post(
        HF_API_URL,
        headers=HEADERS,
        json={
        "inputs": text,
        "options":{"wait_for_model":True}
        }
    )

    return response.json()

def push_to_mongo(embeddings_data):
    # make connection to the database
    client = MongoClient(MONGO_CONNECTION_STRING)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    # insert data
    collection.insert_many(embeddings_data)
    client.close()

def generate_embedding_knowledgebase(csv_filename):
    """Generate embeddings for knowledgebase and push to mongodb"""
    embeddings = []
    print('Reading csv file, generating embeddings')
    file_contents = read_csv(csv_filename)
    for d in file_contents:
        content = d['content']
        embedding = generate_embedding(content)
        embeddings.append({"url": d['url'], "title": d['title'], "content": content, "embedding": embedding})

    print('Uploading to MongoDB')
    push_to_mongo(embeddings)
    print('Successfully generated embeddings and saved to mongodb collection')

def perform_vector_search(query):
    # make connection to the database
    client = MongoClient(MONGO_CONNECTION_STRING)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    print('Generating embeddings for query string, performing vector-search')
    query_embedding = generate_embedding(query)
    result = collection.aggregate([
    {"$vectorSearch": {
        "queryVector": query_embedding,
        "path": EMBEDDING_FIELD,
        "numCandidates": int(CANDIDATES_NUMBER),
        "limit": int(SEARCH_LIMIT),
        "index": INDEX,
        }}
    ])

    client.close()

    return result