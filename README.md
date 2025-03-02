# 🤖 AI-Powered Telegram Bot with Intelligent Automation

## 📌 Overview
This AI-powered Telegram bot is designed to automate complex tasks, including **advanced file searching, AI-driven code execution, voice transcription, and self-updating capabilities**. The bot can execute commands, locate and manage files, fix errors, and even update itself dynamically. 

It supports **natural language processing**, enabling users to issue complex commands like:
- **"Find all PDF files in my Downloads folder that were created in the last week and copy them to a new folder called 'Recent PDFs' on my Desktop."**
- **"Search for an Excel report from last month and send it to me on Telegram."**
- **"Finf and send me this file"**

The bot is built to provide **automation, efficiency, and intelligent decision-making**, fully integrated into the Telegram platform.

---

## 🚀 Features
### 🔹 **AI-Powered Code Generation & Execution**
- Generates and runs Python, JavaScript, and other scripts based on user requests.
- Detects and fixes errors automatically to ensure successful execution.
- Optimized for automation, capable of executing system commands safely.

### 🔹 **Advanced File Search & Management**
- Finds files in predefined directories (Desktop, Documents, Downloads, etc.).
- Filters results based on **date, file type, size, or keyword relevance**.
- Sends **requested files directly to the user via Telegram**.
- Supports **batch file management**, including renaming, moving, and copying files.

### 🔹 **Telegram Bot Integration**
- Processes text-based commands and voice commands in Telegram.
- Uses **AI transcription** to convert speech to text and execute tasks accordingly.
- Replies with AI-generated responses or performs requested actions immediately.

### 🔹 **Self-Updating System**
- Dynamically updates itself by generating a new version of its code.
- Creates automatic **backups** before applying updates.
- Runs an **error-checking process** to verify update success.

### 🔹 **Voice Command Processing**
- Converts **voice messages to text** using **Cloudflare Whisper AI**.
- Supports **natural language understanding**, allowing for detailed requests.

### 🔹 **Smart Error Handling & Auto-Fix**
- If an error occurs in generated code, the bot:
  1. **Detects the issue.**
  2. **Automatically corrects and reattempts execution.**
  3. **Provides an explanation if a fix isn't possible.**

---

## 🛠 Installation Guide

### **1️⃣ Install Required Dependencies**
Make sure you have the required dependencies installed before running the bot.

### **🔹 Node.js & npm (For Telegram Bot)**
Download and install Node.js from [Node.js Official Site](https://nodejs.org/)
```sh
sudo apt update
sudo apt install nodejs npm
```

### **🔹 Python (For Script Execution)**
Download and install Python from [Python Official Site](https://www.python.org/downloads/)
```sh
sudo apt install python3 python3-pip
```

### **🔹 Install Required npm Packages**
```sh
npm install fs path axios child_process readline os node-telegram-bot-api
```

### **🔹 Install Required Python Modules**
```sh
pip install requests telepot python-telegram-bot
```

---

## ⚙️ Configuration
Before running the bot, you need to set up your **API keys** for various services.

### **1️⃣ Set Up Telegram Bot API**
1. Open [BotFather](https://t.me/BotFather) on Telegram.
2. Send the command `/newbot` and follow the instructions.
3. Copy the **Telegram Bot Token** and set it in the script as `TELEGRAM_BOT_TOKEN`.

### **2️⃣ Set Up Cloudflare Whisper API (For Voice Transcription)**
1. Sign up for an account at [Cloudflare](https://www.cloudflare.com/).
2. Get an API key for **Cloudflare Whisper** transcription.
3. Set the key in the script as `CLOUDFLARE_API_TOKEN`.

### **3️⃣ Set Up Google Gemini AI API**
1. Sign up for an API key at [Google AI](https://ai.google.dev/).
2. Set the key in the script as `GEMINI_API_KEY`.

---

## 🎯 How to Use

### ▶️ **Starting the Bot**
Once everything is set up, you can start the bot by running:
```sh
node bot.js
```
The bot will begin listening for commands via Telegram.

---

## 📂 File Search & Management System
- The bot can **search for files** in predefined directories.
- Filters results based on **date, file type, and relevance**.
- Sends files directly to the user via Telegram.
- Supports **batch operations**, such as moving, renaming, and copying files.

---

## 🔄 AI-Driven Self-Update System
- The bot can **update itself** by generating a new version of its code.
- **Backups are automatically created** before applying updates.
- The bot verifies **if the update was successful** before restarting.

---

## 📌 Supported Commands
| Command Type       | Example Usage                                                   | Description                                   |
|--------------------|---------------------------------------------------------------|-----------------------------------------------|
| **Generate Code**  | "Create a Python script that opens Google"                   | Generates and executes a script.              |
| **File Search**    | "Find all PDF files from the last month and send them to me" | Searches for files and delivers them via Telegram. |
| **Run Scripts**    | "Run the script backup.py"                                   | Executes an existing Python script.          |
| **Voice Commands** | (Send a voice note with a request)                           | Converts speech to text and processes it.    |
| **Advanced Search**| "Find Excel files created last week and move them to Reports" | Performs advanced file searches and actions. |

---

## 📝 License
This project is **open-source** and available for anyone to use and modify.

---

## 📞 Contact & Support
For any **questions, issues, or feature requests**, feel free to **contact me on Telegram**:  
📩 **[@HILLEL6767](https://t.me/HILLEL6767)**

🚀 Happy Coding!
```

