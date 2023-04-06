## Athena - A Personal Virtual Assistant

Athena is a personal virtual assistant built using Python, GPT-3.5 Turbo, Whisper ASR, Flask, and the Telegram API. It can handle text and voice messages, provide helpful advice, search the web, and more.

### Getting Started

To set up Athena on your own machine, follow these steps:

1. Clone the repository:

```
git clone https://github.com/PickleChum/athena.git
```

2. Create a virtual environment and install the required packages:

```bash
cd athena
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Set up your API credentials for the following services:

- OpenAI (GPT-3.5 Turbo and Whisper ASR)
- Bing Web Search
- OpenWeatherMap
- Telegram

You will need to create a `.env` file in the project directory with the following content:

```
OPENAI_API_KEY=your_openai_api_key
WHISPER_ASR_API_KEY=your_whisper_asr_api_key
BING_API_KEY=your_bing_api_key
OPENWEATHER_API_KEY=your_openweathermap_api_key
BOT_TOKEN=your_telegram_bot_token
MY_TELEGRAM_USER_ID=your_telegram_user_id
```

Replace the placeholders with your actual API keys and your Telegram user ID.

4. Run the Flask application:

```bash
python app.py
```

5. Set up a webhook on your server to receive updates from the Telegram API. The webhook URL should point to the `/webhook` endpoint on your server.

### Usage

Interact with Athena by sending text or voice messages to your Telegram bot. Athena will respond with helpful information, search results, and more.

To reset the conversation history, send the `/reset` command to the bot.

Add the keyword search at the beginning of your message, and the bot will utilize the Bing API to fetch up-to-date information for your query. Additionally, if your message includes one or more trigger words related to time or weather, the bot will automatically provide relevant information.

### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
