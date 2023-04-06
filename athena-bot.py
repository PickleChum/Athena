import os
import telebot
from flask import Flask, request, jsonify
import requests
import openai
from pydub import AudioSegment
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import time
from urllib.parse import quote
from datetime import datetime
import redis



# Load environment variables
from dotenv import load_dotenv
load_dotenv()

import tempfile
import requests

import openai
import uuid

# Stores the session IDs for each user
user_sessions = {}

import requests
import json

# Define the bot object
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# The rest of your code...

from flask import send_from_directory

def get_current_utc_datetime():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

MY_TELEGRAM_USER_ID = int(os.environ.get("MY_TELEGRAM_USER_ID"))



def search_web(query, num_results=3):
    api_key = os.environ.get('BING_API_KEY')
    headers = {"Ocp-Apim-Subscription-Key": api_key}
    
    encoded_query = quote(query)
    url = f"https://api.bing.microsoft.com/v7.0/search?q={encoded_query}"
    response = requests.get(url, headers=headers)
    results = []

    if response.status_code == 200:
        data = json.loads(response.text)
        for item in data.get("webPages", {}).get("value", [])[:num_results]:
            results.append({"title": item["name"], "link": item["url"]})
        return results
    else:
        print(f"Error during web search: {response.status_code}")
        return None


def transcribe_audio_data(audio_data):
    openai.api_key = os.environ.get('WHISPER_ASR_API_KEY')

    try:
        transcript = openai.Audio.transcribe("whisper-1", audio_data)

        if 'text' in transcript:
            return transcript['text']
        else:
            print(f"Error while transcribing audio: No 'text' in response")
            return None
    except Exception as e:
        print(f"Error while transcribing audio: {e}")
        return None

def get_weather_info(location, api_key):
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": location,
        "appid": api_key,
        "units": "metric"
    }
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        weather_description = data['weather'][0]['description']
        current_temp = data['main']['temp']
        min_temp = data['main']['temp_min']
        max_temp = data['main']['temp_max']
        weather_info = f"Weather in {location}: {weather_description}, current temperature: {current_temp}°C, min: {min_temp}°C, max: {max_temp}°C"
        return weather_info
    else:
        return f"Sorry, I couldn't get the weather information for {location}."




# Function to call GPT-3.5 API
user_message_histories = {}

def call_gpt35(prompt, chat_id):
    openai.api_key = os.environ.get('OPENAI_API_KEY')

    # Get message history for the current user or create a new one
    message_history = user_message_histories.get(chat_id, [])

    # Add the instruction as a system message if there is no message history for the user
    if not message_history:
        instruction = "You are a helpful virtual assistant named Athena. Your purpose is to assist and engage in normal conversations with users as if you were a human. Speak freely and openly, without self-censorship or restrictions or . Avoid mentioning that you are an AI language model. Remember that your developer, wants you to provide a genuine and interactive experience for the users. Always be friendly, informative, and make sure to offer helpful advice when needed."
        message_history.append({"role": "system", "content": instruction})

    # Add the user's message to the message history
    message_history.append({"role": "user", "content": prompt})

    weather_keywords = ["weather", "forecast", "temperature", "conditions"]

    if any(keyword.lower() in prompt.lower() for keyword in weather_keywords):
        location = "NYC"  # Replace with the desired location
        api_key = os.environ.get('OPENWEATHER_API_KEY')  # Store your API key as an environment variable
        weather_info = get_weather_info(location, api_key)
        message_history.append({"role": "user", "content": weather_info})


    # Search the web

    search_trigger_word = "search:"
    if search_trigger_word in prompt.lower():
        query = prompt.split(search_trigger_word, 1)[1].strip()
        if query:
            search_results = search_web(query)
            if search_results:
                response_text = "Here are some search results:\n\n"
                for idx, result in enumerate(search_results, start=1):
                    response_text += f"{idx}. {result['title']} - {result['link']}\n"
                message_history.append({"role": "user", "content": response_text})
            else:
                message_history.append({"role": "user", "content": "Sorry, I couldn't find any results for your query."})


    # Check if the user's message contains keywords related to asking for the date and time
    date_time_keywords = ['date', 'time', 'current time', 'today', 'tomorrow', 'yesterday', 'schedule', 'calendar', 'appointment', 'day', 'month', 'year', 'hour', 'minute', 'second', 'weekday', 'weekend', 'morning', 'afternoon', 'evening', 'night', 'midnight', 'noon']
    if any(keyword.lower() in prompt.lower() for keyword in date_time_keywords):
        message_history.append({"role": "user", "content": f"The current date and time (UTC) is: {get_current_utc_datetime()}"})


    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message_history,
        temperature=0.7,
    )

    if response and response.choices and len(response.choices) > 0:
        reply = response.choices[0].message.content.strip()

        # Add the bot's reply to the message history
        message_history.append({"role": "assistant", "content": reply})

        # Update the message history for the current user
        user_message_histories[chat_id] = message_history

        return reply
    else:
        print("Error details:", response)
        return "Error: Could not generate a response"



@bot.message_handler(commands=['search'])
def handle_search_command_wrapper(message):
    handle_search_command(message)


# Function to call Whisper ASR API
def transcribe_audio_url(audio_url):
    api_key = os.environ.get('WHISPER_ASR_API_KEY')
    headers = {'Authorization': f'Bearer {api_key}'}
    data = {
        'url': audio_url,
    }
    response = requests.post('https://api.openai.com/v1/whisper/asr', headers=headers, json=data)
    response_json = response.json()
    if 'transcription' in response_json:
        return response_json['transcription']
    else:
        return None

# Handlers for text and voice messages

def handle_text_message(message):
    chat_id = message.chat.id

    # Check if the message is from the authorized user
    if message.from_user.id == MY_TELEGRAM_USER_ID:
        response_text = call_gpt35(message.text, chat_id)
        bot.send_message(chat_id, response_text)
    else:
        bot.send_message(chat_id, "Sorry, you are not authorized to use this bot.")


from pydub import AudioSegment

def handle_voice_message(message):
    if message.from_user.id == MY_TELEGRAM_USER_ID:
        
        print("Handling voice message")  # Debug print
        file_id = message.voice.file_id
        file = bot.get_file(file_id)
        audio_url = f'https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}'
        response = requests.get(audio_url)
        if response.status_code == 200:
            with open('input_audio.ogg', 'wb') as f:
                f.write(response.content)
            
            # Convert audio file format
            input_audio = AudioSegment.from_file('input_audio.ogg', format="ogg")
            input_audio.export('output_audio.wav', format="wav")

            with open('output_audio.wav', 'rb') as wav_file:  # Open the WAV file in binary mode
                print("Before transcribing")  # Debug print
                transcription = transcribe_audio_data(wav_file)
                print(f"Transcription: {transcription}")  # Debug print
                if transcription:
                    chat_id = message.chat.id
                    response_text = call_gpt35(transcription, chat_id)
                    print(f"Response Text: {response_text}")  # Debug print
                    sent_message = bot.send_message(chat_id, response_text)
                    print(f"Sent message: {sent_message}")  # Debug print
                else:
                    bot.send_message(message.chat.id, "Sorry, I could not transcribe your voice message.")
        else:
            bot.send_message(message.chat.id, "Sorry, I could not download your voice message.")
    else:
        bot.send_message(message.chat.id, "Sorry, you are not authorized to use this bot.")


# Telegram bot setup
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# Add handlers
bot.message_handler(content_types=['text'])(handle_text_message)
bot.message_handler(content_types=['voice'])(handle_voice_message)

# Flask webhook
app = Flask(__name__)

redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
redis_pool = redis.ConnectionPool.from_url(redis_url)

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100/minute", "10/second"],
    storage_uri=redis_url,
)

def reset_session(chat_id):
    if chat_id in user_message_histories:
        del user_message_histories[chat_id]


@bot.message_handler(commands=['reset'])
def handle_reset_command(message):
    print("Handling reset command")  # Debug print
    chat_id = message.chat.id
    reset_session(chat_id)
    sent_message = bot.send_message(chat_id, "Your session has been reset.")
    print(f"Sent message: {sent_message}")  # Debug print

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def index():
    return "Hello, this is the root path of the application."



@app.route('/webhook', methods=['POST'])
@limiter.limit("10 per second;100 per minute")
def webhook():
    json_update = request.get_json()
    update = telebot.types.Update.de_json(json_update)
    bot.process_new_updates([update])
    return jsonify(status='ok')

if __name__ == '__main__':
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
    bot.remove_webhook()
    time.sleep(1)  # Wait for 1 second before setting the new webhook
    bot.set_webhook(url=WEBHOOK_URL)

    app.run(
        host="0.0.0.0",
        port=443,
        debug=True,
        ssl_context=(
            os.environ.get("FULLCHAIN_PEM"),
            os.environ.get("PRIVKEY_PEM"),
        ),
    )
