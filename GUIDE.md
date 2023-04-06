# Athena Telegram Chatbot Setup Guide

This guide will walk you through the process of setting up Athena, a Telegram chatbot powered by GPT-3.5 and Whisper ASR.

## Prerequisites

- Python 3.8
- pip (Python package manager)
- A Telegram account
- An OpenAI API key for GPT-3.5 and Whisper ASR
- A Bing API key for web search
- An OpenWeatherMap API key for weather information
- A Redis server (optional, for rate limiting)
- A registered domain name connected to your server IP address

## Installation

1. Clone the project repository or download the code as a ZIP file and extract it to your local machine.

2. Ensure you have Python 3.8 installed on your system. You can check your Python version by running the following command in your terminal:

   `python --version`

   If you don't have Python 3.8, you can download it from the official Python website: https://www.python.org/downloads/

3. Create a virtual environment to isolate the project dependencies. Navigate to the project directory in your terminal and run the following command:

   `python -m venv venv`

   Activate the virtual environment by running the appropriate command for your operating system:

   - On Windows: venv\Scripts\activate
   - On macOS/Linux: source venv/bin/activate

4. Install the required packages by running the following command:

   `pip install -r requirements.txt`

5. Set up the environment variables. You can either set them directly in your system or create a .env file in the project directory with the following content:

```
   BOT_TOKEN=your_telegram_bot_token
   OPENAI_API_KEY=your_openai_api_key
   WHISPER_ASR_API_KEY=your_openai_whisper_asr_api_key
   BING_API_KEY=your_bing_api_key
   OPENWEATHER_API_KEY=your_openweathermap_api_key
   MY_TELEGRAM_USER_ID=your_telegram_user_id
   WEBHOOK_URL=your_webhook_url
   FULLCHAIN_PEM=your_fullchain_pem_file_path
   PRIVKEY_PEM=your_privkey_pem_file_path
   REDIS_URL=your_redis_url (optional)
```

6. Replace the placeholders (e.g., your_telegram_bot_token) with your actual API keys and other required information.

7. Connect your domain name to your server IP address. This process varies depending on your domain registrar and hosting provider, so please consult their documentation for instructions.

8. Run the main Python script to start the Telegram bot:

   `python athena-bot.py`

The bot should now be up and running. You can interact with it on Telegram by sending text and voice messages.
