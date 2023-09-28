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
openai.api_key = os.getenv('OPENAI_TOKEN')

def get_menu_from_chatgpt(menu, place):
    user_prompt = f"Today's date is {datetime.datetime.now().strftime('%A, the %d/%m/%Y')} in week {datetime.datetime.now().isocalendar().week}. The menu for today at place {place} is: ```{menu}```. What is there for lunch today? Give me just the menu, be as precise as possible, don't use adjectives. Include the name of the place in the title. Make the menu options not all capitalized, and translate to English."
    messages= [{"role": "user", "content": user_prompt}]
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        temperature=0.7,
        messages=messages,
    )
    return response.choices[0].message["content"]


# Scrape the websites
urls = ["https://www.foodandco.dk/besog-os-her/restauranter/dtu/dtu-lyngby-101/", "https://www.foodandco.dk/besog-os-her/restauranter/dtu/dtu-lyngby-202/", "https://www.foodandco.dk/besog-os-her/restauranter/dtu/dtu-lyngby-skylab/"]
for url in urls:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

# Extract the information you want to post
    title = soup.find('title').text

    mydivs = soup.find_all("div", {"class": "ContentBlock"})
    if len(mydivs) < 1:
        raise Exception()
    menu = mydivs[0].text

    print("======")
# Make a request to ChatGPT
    chat_reply = get_menu_from_chatgpt(menu, title)

    print("ChatGPT response:", chat_reply)

    # Set up the Discord webhook
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')

    # Create the payload to send in POST request
    payload = {
        "content": f"Title: {title}\nDescription: {chat_reply}",
    }

    # Make the POST request to the webhook using aiohttp
    async def post_to_webhook():
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload) as response:
                if response.status != 204:
                    print("Failed to post to webhook")

    asyncio.run(post_to_webhook())
