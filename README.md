# 🤖 AI-Powered Telegram Bot for Windows - Intelligent Automation

## 📌 Overview

This **AI-powered Telegram bot** is designed exclusively for **Windows**, providing advanced **automation, intelligent file searching, AI-driven code execution, voice transcription, and self-updating capabilities**.

With **natural language processing**, you can issue commands like:

- **"Find all PDF files in my Downloads folder from the past week and copy them to 'Recent PDFs' on my Desktop."**
- **"Search for an Excel report from last month and send it to me on Telegram."**
- **"Generate a Python script to fetch stock market data and email it to me."**
- **"Open Google"** (automatically launches the browser)

The bot seamlessly integrates with **Telegram** to provide **automation, efficiency, and intelligent decision-making**.

---

## 🚀 Features

### 🔹 **AI-Powered Code Generation & Execution**

- **Generates and runs Python, JavaScript, and other scripts** based on user input.
- **Detects and fixes errors automatically**.
- **Executes system commands securely**.

### 🔹 **Advanced File Search & Management**

- Finds files across multiple directories (**Desktop, Documents, Downloads, etc.**).
- Filters results based on **date, file type, size, or keyword relevance**.
- Sends **files directly to the user via Telegram**.
- Supports **batch operations** (renaming, moving, copying).

### 🔹 **Telegram Bot Integration**

- Processes **text-based and voice-based** commands.
- Uses **AI transcription** to convert speech to text.
- Responds with AI-generated replies or executes requested tasks.

### 🔹 **Self-Updating System**

- Dynamically **updates itself** by generating new versions of its code.
- Creates **automatic backups** before applying updates.
- Runs an **error-checking process** to verify update success.

### 🔹 **Voice Command Processing**

- Converts **voice messages to text** using **Cloudflare Whisper AI**.
- Understands complex, multi-step requests.

### 🔹 **Smart Error Handling & Auto-Fix**

- If an error occurs in generated code, the bot:
  1. **Identifies the issue.**
  2. **Attempts automatic correction.**
  3. **Provides an explanation if a fix isn't possible.**

---

## 🛠 Installation Guide (**Windows Only**)

### **1️⃣ Install Required Dependencies**

Ensure you have the necessary dependencies installed before running the bot.

### **🔹 Node.js & npm (For Telegram Bot)**

Download and install Node.js from [Node.js Official Site](https://nodejs.org/)

Or, if you already have Chocolatey installed, simply run this command:

```sh
choco install nodejs
```

### **🔹 Python (For Script Execution)**

Download and install Python from [Python Official Site](https://www.python.org/downloads/)

Or, if you already have Chocolatey installed, simply run this command:

```sh
choco install python
```

### **🔹 Install Required npm Packages**

```sh
npm install fs path axios child_process readline os node-telegram-bot-api
```

### **🔹 Install Required Python Modules**

```sh
pip install requests telepot python-telegram-bot fuzzywuzzy
```

---

## ⚙️ Configuration

Before running the bot, set up your **API keys** and configuration.

### **1️⃣ Download and Run the Setup Script**

1. **Download the setup script** (`setup_bot.py`) from the GitHub repository.
2. **Move the script to your desired folder** (e.g., `C:\TelegramBot`).
3. Open a **Command Prompt (cmd)** and navigate to the folder where the script is located:

```sh
cd C:\TelegramBot
```

4. **Run the script** to configure the bot:

```sh
python setup_bot.py
```

### **2️⃣ Enter Required Information**
When prompted, enter the following details:

- **Telegram Bot Token** → Get from [BotFather](https://t.me/BotFather).
- **Cloudflare Whisper API Key** → Get from [Cloudflare](https://www.cloudflare.com/).
- **Google Gemini AI API Key** → Get from [Google AI](https://ai.google.dev/).
- **Your Telegram Username** → Needed for message authentication.

The script will automatically create a configuration file (`config.json`) with your credentials.

---

## 🎯 How to Use

### ▶️ **Running the Bot**

1. Ensure all dependencies are installed.
2. Start the bot using:

```sh
node bot.js
```

3. The bot is now active and will respond to Telegram commands automatically.

---

## 📂 File Search & Management System

- Searches predefined directories.
- Filters results by **date, type, or relevance**.
- Sends files directly via Telegram.
- Supports **batch operations** like renaming and moving.

---

## 🔄 AI-Driven Self-Update System

- The bot **updates itself** automatically.
- **Creates backups** before updates.
- Verifies updates before restarting.

---

## 📌 Supported Commands

| Command Type        | Example Usage                                                 | Description                                   |
| ------------------- | ------------------------------------------------------------- | --------------------------------------------- |
| **Generate Code**   | "Open Google"                                                 | Executes an automated task.                   |
| **File Search**     | "Find a PDF file named 'HELLO WORLD' and send it to me"  | Searches for files and delivers via Telegram. |
| **Run Scripts**     | "Run the script backup.py"                                    | Executes an existing script.                  |
| **Voice Commands**  | (Send a voice note with a request)                            | Converts speech to text and processes it.     |
| **Advanced Search** | "Find Excel files created last week and move them to Reports" | Performs advanced searches and actions.       |

---

## 📝 License

This project is **open-source** and available for anyone to use and modify.

---

## 📞 Contact & Support

For **questions or support**, contact me on Telegram:\
📩 **[@HILLEL6767](https://t.me/HILLEL6767)**

🚀 Happy Coding!

