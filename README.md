AI-Powered Telegram Bot with File Search and Self-Update

Overview

This is an advanced AI-powered bot that integrates with Telegram, allowing users to generate code, search for files, and even update itself. The bot supports Python script execution, AI-driven code correction, voice transcription, and a file search system using an external Python script.

Features

AI-Powered Code Generation: Automatically generates Python, JavaScript, and other scripts based on user requests.

File Search: Searches for files in predefined directories and suggests similar matches.

Telegram Integration: Receives and processes commands via Telegram messages and voice notes.

AI-Based Self-Updates: Updates itself using an AI-generated script while maintaining backups.

Voice Transcription: Converts voice messages into text commands using Cloudflare Whisper.

Error Handling & Auto-Fix: Detects errors in generated code and attempts to fix them automatically.

Installation

1. Install Required Dependencies

Ensure you have the required dependencies installed.

Node.js & npm (for Telegram bot)

Download and install Node.js from nodejs.org

sudo apt update
sudo apt install nodejs npm

Python (for script execution)

Download and install Python from python.org

sudo apt install python3 python3-pip

Install Required npm Packages

npm install fs path axios child_process readline os node-telegram-bot-api

Install Required Python Modules

pip install requests telepot python-telegram-bot

Configuration

1. Set Up Telegram Bot API

Go to BotFather on Telegram.

Send /newbot and follow the instructions.

Copy the bot token and set it in the script as TELEGRAM_BOT_TOKEN.

2. Set Up Cloudflare Whisper API

Create a Cloudflare account at cloudflare.com.

Get an API key for Whisper transcription.

Set it in the script as CLOUDFLARE_API_TOKEN.

3. Set Up Google Gemini AI API

Sign up for an API key at Google AI.

Set the key in the script as GEMINI_API_KEY.

Usage

Running the Bot

To start the bot, simply run:

node bot.js

File Search System

The bot can search for files in predefined folders (Desktop, Documents, Downloads, etc.). If the exact file isn't found, it suggests similar files using an AI filter.

Update System

The bot can update itself by generating a new version of its code and applying the update automatically.

License

This project is open-source and available for use with modifications.

