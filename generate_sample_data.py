from openai import OpenAI
import pandas as pd
import json
import re
import asyncio
from tenacity import retry, stop_after_attempt, wait_random_exponential

# Replace with your actual API key

json_example = {
  "Report ID": "RPT1025",
  "Date Reported": "2023-02-15",
  "Accident Type": "Vehicle Collision",
  "Location": "New York",
  "Claim Amount (USD)": 5000,
  "Claim Status": "Under Review",
  "Policy Holder's Age": 30,
  "Vehicle Age": 5,
  "Incident Severity": "Medium",
  "Incident Report" :"""At approximately 3:45 PM on February 24, 2024, a collision occurred involving a 2019 Toyota Camry driven by Jane Doe and a 2017 Honda Accord driven by John Smith. The incident took place at the intersection of Main St. and 2nd Ave in Springfield. Jane Doe was traveling east on Main St. approaching the intersection with 2nd Ave. At the same time, John Smith was heading south on 2nd Ave.
                    Jane Doe reported that she had a green light as she entered the intersection. Concurrently, John Smith claimed he believed he had the right of way. The front right side of the Toyota Camry made contact with the rear left side of the Honda Accord, resulting in minor damage to both vehicles.
                    """
}

n=1
responses = []
def create_new_prompt(json):
    prompt = f"""Generate a JSON object for an insurance accident report with the following fields:
    - Report ID: A unique identifier starting with 'RPT' followed by a number.
    - Date Reported: The date when the accident was reported in 'YYYY-MM-DD' format.
    - Accident Type: One of 'Vehicle Collision', 'Property Damage', 'Personal Injury', 'Theft', 'Natural Disaster'.
    - Location: The city where the accident occurred.
    - Claim Amount (USD): The amount claimed for the accident, in USD.
    - Claim Status: One of 'Submitted', 'Under Review', 'Approved', 'Rejected'.
    - Policy Holder's Age: The age of the policyholder.
    - Vehicle Age: The age of the vehicle involved in the accident, if applicable.
    - Incident Severity: The severity of the incident, one of 'Low', 'Medium', 'High'.
    - Incident Report: A description of the incident with maximum 50 words
    Example:
    {str(json)}"""

    return prompt

def extract_json(text):
    pattern = r'\{.*?\}|\[.*?\]'
    match = re.search(pattern, text)
    if match:
        return match.group(0)
    else:
        return None

@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(2))
async def get_completion(messages): 
    client = OpenAI()
    response = client.chat.completions.create(
            model = "gpt-4-turbo-preview",
            messages=messages,  # Choose the appropriate model
            temperature=0.8,
            response_format={ "type": "json_object" }
    )
    return response

async def generate_insurance_data(messages, max=500):
    """
    Generate insurance data using OpenAI's GPT API.

    Args:
    - prompt (str): The prompt to send to the model.
    - n (int): The number of samples to generate.

    Returns:
    - DataFrame: A pandas DataFrame with the generated data.
    """
    global n
    global responses
    if n<=max: 
        try:
            response = await get_completion(messages)
            text = response.choices[0].message.content.strip()
        
            sampled_json = json.loads(text)
            n=n+1
            new_prompt = create_new_prompt(sampled_json)
            messages = [
                {"role": "system", "content": "You are a data scientist who is working on generating sample data for model training. You generate JSON."},
                {"role": "user", "content" : new_prompt}
            ]
            responses.append(sampled_json)
            print(f"Response Length {len(responses)}")
            return await generate_insurance_data(messages, max=1000)
        except Exception as e:
            print(f"Handling the exception: {e}")
            return await generate_insurance_data(messages, max=1000)
        
    else:
        return pd.DataFrame(responses)

# Define the prompt
async def main():
    prompt = create_new_prompt(json_example)
# Generate data
    messages = [
        {"role": "system", "content": "You are a data scientist who is working on generating sample data for model training. You generate JSON."},
        {"role": "user", "content" : prompt}
        ]
    df_generated = await generate_insurance_data(messages, max=1000)  # Adjust 'n' for the number of samples
    df_generated.to_csv("output/sample_insurance_data.csv")
    print(df_generated)

asyncio.run(main())