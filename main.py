import requests
import aiohttp
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import openai
import datetime
import os
# Run the asynchronous function to post to the webhook
import asyncio
load_dotenv()  

# Set up your OpenAI API key
OPENAI_TOKEN = os.getenv('OPENAI_TOKEN')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

if OPENAI_TOKEN is None:
    raise Exception("You need to set OPENAI_TOKEN environment variable to run this script")

if DISCORD_WEBHOOK_URL is None:
    raise Exception("You need to set DISCORD_WEBHOOK_URL environment variable to run this script")

openai.api_key = OPENAI_TOKEN

def get_menu_from_chatgpt(menu):
    menu = menu.lower()
    menu = menu.replace("mandag", "monday")
    menu = menu.replace("tirsdag", "tuesday")
    menu = menu.replace("onsdag", "wednesday")
    menu = menu.replace("torsdag", "thursday")
    menu = menu.replace("fredag", "friday")

    user_prompt = f"Today is {datetime.datetime.now().strftime('%A')} in week {datetime.datetime.now().isocalendar().week}. The menu is: ```{menu}```. What is there for lunch today ({datetime.datetime.now().strftime('%A')}? Give me just the menu, be as precise as possible, don't use adjectives, I only want the menu options as bullet points and I don't want the name of the place or any extra information. Make the menu options not all capitalized, and translate to English."
    messages= [{"role": "user", "content": user_prompt}]
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        temperature=0.7,
        messages=messages,
    )
    return response.choices[0].message["content"]


# Scrape the websites
urls = ["https://www.foodandco.dk/besog-os-her/restauranter/dtu/dtu-lyngby-101/", "https://www.foodandco.dk/besog-os-her/restauranter/dtu/dtu-lyngby-202/", "https://www.foodandco.dk/besog-os-her/restauranter/dtu/dtu-lyngby-skylab/"]
responses = []
for url in urls:
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

# Extract the information you want to post
        place_name = soup.find('title').text

        mydivs = soup.find_all("div", {"class": "ContentBlock"})
        if len(mydivs) < 1:
            raise Exception()
        menu = mydivs[0].text

        print("======")
# Make a request to ChatGPT
        chat_reply = get_menu_from_chatgpt(menu)

        responses.append({
                    "title": place_name,
                    "description": chat_reply,
                    "color": 0x00ff00
                })
        print(f"Successfully processed the menu for {url}")
    except:
        print(f"An error occured processing the menu for {url}")

print("======")
# Set up the Discord webhook
webhook_url = DISCORD_WEBHOOK_URL

# Create the payload to send in POST request
payload = {
    "embeds": responses
}

DISCORD_ROLE_TO_PING = os.getenv('DISCORD_ROLE_TO_PING')
if DISCORD_ROLE_TO_PING is not None:
    payload["content"] = f"<@&{DISCORD_ROLE_TO_PING}>"

# Make the POST request to the webhook using aiohttp
async def post_to_webhook():
    async with aiohttp.ClientSession() as session:
        async with session.post(webhook_url, json=payload) as response:
            if response.status != 204:
                print("Failed to post to webhook")

asyncio.run(post_to_webhook())
