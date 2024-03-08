import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from organization import Organization
from openai import OpenAI
import csv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json

WEBDRIVER_PATH = '/Users/cihanacar/chromedriver-mac-arm64/chromedriver'

def setup_driver():
    service = Service(WEBDRIVER_PATH)
    options = Options()
    options.add_argument("--headless")  # Run Chrome in headless mode
    options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
    options.add_argument("--window-size=1920x1080")  # Specify window size
    
    # Additional options for better performance in headless mode
    options.add_argument('--no-sandbox')  # Bypass OS security model, WARNING: only if you understand the implications
    options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
 
    driver = webdriver.Chrome(service=service, options=options)

    driver.set_page_load_timeout(60)
    return driver

def fetch_html_with_selenium(url):
    driver = setup_driver()
    try:
        driver.get(url)
        
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Adjust based on your needs
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        html = driver.page_source
    except TimeoutException:
        print(f"Page {url} could not be loaded within the timeout limit.")
        html = None
    except Exception as e:
        print(f"An error occurred: {e}")
        html = None
    finally:
        driver.quit()
    return html
def clean_html_to_text(html):
    """
    This function takes HTML content as input and returns clean text.
    It removes all HTML tags and tries to maintain readable formatting.
    """
    # Parse the HTML
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove script and style elements
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()

    # Use separator to maintain readability in text output
    # This will add double newlines before block elements (mimicking paragraphs)
    for block in soup.find_all(['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li']):
        block.insert_before("\n\n")
        block.insert_after("\n")

    # Get text from the soup and strip leading/trailing whitespaces
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    # Break multi-headlines into a line each and drop blank lines
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    return text


def get_context(text):
    client = OpenAI()
    messages = [
        {"role": "system", "content": "You are an assistant whose job is to determine context of the given text."},
        {"role": "user", "content": f"What is the context of this text: '{text}'"}
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=256
    )

    return response.choices[0].message.content

def clean_unnecessary_text(text, context): 
    client = OpenAI()
    messages = [
        {"role": "system", "content": "You are an assistant whose job is to understand and clean up texts if required depending on the context. You return JSON results with the 'tags' and 'cleaned_text' keys"},
        {"role": "assistant", "content": f"The context of the given text can be summarized as: {context}"},
        {"role": "assistant", "content": f"This is an AI Startup's website content"},  # Fixed syntax here
        {"role": "user", "content": f"I need you to do two things: First give me 5 tags for this text. And please clean up all the unnecessary paragraphs from the given text: '{text}' but keep rest of the paragraphs for a clean read"}
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages = messages,
        response_format={ "type": "json_object" }
    )

    return response.choices[0].message.content

    
    

organizations = []

with open('data/companies-2-28-2024-batch22.csv', 'r', encoding='utf-8') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        organization = Organization.from_csv_row(row)
        organizations.append(organization)
organizations_without_website = [org for org in organizations if org.website]
orgs_dicts = [org.to_dict() for org in organizations]
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
collection = db['organizations']
# [org_dict.pop('_id', None) for org_dict in orgs_dicts]
# collection.insert_many(orgs_dicts)

# exit()
# for org_dict in orgs_dicts: 
#     if collection.find_one({'website': org_dict['website']}) == None:
#         org_dict.pop('_id', None)  
#         collection.insert_one(org_dict)
# index_name = collection.create_index([('website', 1)])
query = {
    '$and': [
        {'batch': 2},
        {'website': {'$exists': True}},
        {'website': {'$ne': None}},
        {'website': {'$ne': ''}},
        {
            '$or' :[
                {'website_context': {'$exists': False}},
                {'website_context' : None},
                {'website_context' : ''}
            ]
        }
        
    ]
}
organization_list = [Organization(**doc) for doc in collection.find(query)]
print(len(organization_list))
for index, organization in enumerate(organization_list):
    document_id = organization._id[0]
    try: 
        print(f"Current Index : {index}") 
        print(f"The Website scrapping: {organization.website}")
        html_content = fetch_html_with_selenium(organization.website)
        clean_text = clean_html_to_text(html_content)
        context = get_context(clean_text)
        cleaned_up = json.loads(clean_unnecessary_text(clean_text, context))
        organization.website_context = context
        organization.website_content = cleaned_up['cleaned_text']
        organization.website_content_tags = cleaned_up['tags']
        organization_dict = organization.to_dict()
        organization_dict.pop('_id', None)  
        result = collection.replace_one(
            {"_id": document_id},
            organization_dict
        )
        print(f"Documents matched for {str(document_id)}: {result.matched_count}")
        print(f"Documents modified for {str(document_id)}: {result.modified_count}")
    except Exception as e:
        print(e)
        # collection.delete_one({"_id": document_id})
    
client.close()
# url = "http://digybite.io/"  # Replace with your target URL
# html_content = fetch_html_with_selenium(url)
# clean_text = clean_html_to_text(html_content)
# print(clean_text)
# print("---------------------------------------------------------------------------------------------")
# context = get_context(clean_text)
# print("---------------------------------------------------------------------------------------------")
# print(context)
# print("---------------------------------------------------------------------------------------------")
# cleaned_up = clean_unnecessary_text(clean_text, context)
# print(cleaned_up)
# print("---------------------------------------------------------------------------------------------")