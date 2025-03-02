```markdown
# 🤖 AI-Powered Telegram Bot with File Search, Code Execution, and Self-Update

## 📌 Overview
This is an advanced AI-powered Telegram bot that integrates cutting-edge technologies, including **AI-driven code generation, file search, error correction, and voice transcription**. The bot can automatically generate and execute code, search for files, and even update itself based on user requests.

It is designed to provide **automation, productivity enhancements, and intelligent decision-making** while offering full integration with Telegram.

---

## 🚀 Features
### 🔹 **AI-Powered Code Generation**
- Automatically generates Python, JavaScript, and other scripts based on user requests.
- Executes scripts, detects errors, and attempts to auto-correct them.

### 🔹 **File Search & Management**
- Searches for files in predefined directories (Desktop, Documents, Downloads, etc.).
- Uses AI filtering to suggest relevant files if an exact match isn't found.
- Provides file search results with pagination for easy navigation.

### 🔹 **Telegram Bot Integration**
- Receives and processes text-based commands via Telegram messages.
- Accepts **voice messages**, transcribes them, and executes corresponding actions.
- Replies with AI-generated responses or executes the requested actions.

### 🔹 **AI-Based Self-Update System**
- Updates itself dynamically by generating new versions of its code.
- Maintains automatic **backups** before any updates.
- Runs an **error-checking system** to verify successful updates.

### 🔹 **Voice Transcription & AI Understanding**
- Converts **voice messages to text** using **Cloudflare Whisper AI**.
- Understands natural language and executes commands based on voice input.

### 🔹 **Advanced Error Handling & Auto-Fix**
- If an error occurs in generated code, the bot:
  1. **Detects the error**.
  2. **Attempts to fix the code automatically**.
  3. **Retries execution until a working solution is found**.

---

## 🛠 Installation Guide
### **1️⃣ Install Required Dependencies**
Ensure you have the necessary dependencies installed before running the bot.

### **Node.js & npm (For Telegram Bot)**
Download and install Node.js from [Node.js Official Site](https://nodejs.org/)
```sh
sudo apt update
sudo apt install nodejs npm
```

### **Python (For Script Execution)**
Download and install Python from [Python Official Site](https://www.python.org/downloads/)
```sh
sudo apt install python3 python3-pip
```

### **Install Required npm Packages**
```sh
npm install fs path axios child_process readline os node-telegram-bot-api
```

### **Install Required Python Modules**
```sh
pip install requests telepot python-telegram-bot
```

---

## ⚙️ Configuration
Before running the bot, you need to set up your **API keys** for various services.

### **1. Set Up Telegram Bot API**
1. Open [BotFather](https://t.me/BotFather) on Telegram.
2. Send the command `/newbot` and follow the instructions.
3. Copy the **Telegram Bot Token** and set it in the script as `TELEGRAM_BOT_TOKEN`.

### **2. Set Up Cloudflare Whisper API (For Voice Transcription)**
1. Sign up for an account at [Cloudflare](https://www.cloudflare.com/).
2. Get an API key for **Cloudflare Whisper** transcription.
3. Set the key in the script as `CLOUDFLARE_API_TOKEN`.

### **3. Set Up Google Gemini AI API**
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

## 📂 File Search System
- The bot can **search for files** in predefined directories (Desktop, Documents, Downloads, etc.).
- If an **exact match isn't found**, the bot will suggest **similar files** sorted by relevance.
- **Pagination support** allows you to browse through results easily.

---

## 🔄 AI-Driven Self-Update System
- The bot can **update itself** by generating a new version of its code.
- **Backups are automatically created** before applying updates.
- The bot verifies **if the update was successful** before restarting.

---

## 📌 Supported Commands
| Command Type       | Example Usage                                   | Description |
|--------------------|-----------------------------------------------|-------------|
| **Generate Code** | "Create a Python script that opens Google" | Generates and executes a script. |
| **File Search**   | "Find a file named report.pdf"             | Searches for files across directories. |
| **Run Scripts**   | "Run the script backup.py"                 | Executes an existing Python script. |
| **Voice Commands**| (Send a voice note with a request)           | Converts speech to text and processes it. |

---

## 📝 License
This project is **open-source** and available for anyone to use and modify.

---

## 📞 Contact & Support
For any **questions, issues, or feature requests**, feel free to **contact me on Telegram**:  
📩 **[@HILLEL6767](https://t.me/HILLEL6767)**

🚀 Happy Coding!
```

