import os
import re

def configure_ai_script():
    print("Please provide the following API keys and tokens for the AI script:")

    gemini_api_key = input("Gemini API Key: ").strip()
    telegram_bot_token = input("Telegram Bot Token: ").strip()
    cloudflare_account_id = input("Cloudflare Account ID: ").strip()
    cloudflare_api_token = input("Cloudflare API Token: ").strip()
    username = input("Your Windows username (e.g., hillel1): ").strip()
    telegram_username = input("Your Telegram username (e.g., HILLEL6767): ").strip() # Added Telegram username input

    # Original ai.js code as a string (multiline) - EXACT CODE PROVIDED BY USER
    ai_js_code = r"""
const fs = require('fs');
const path = require('path');
const axios = require('axios');
const { spawn } = require('child_process');
const readline = require('readline');
const TelegramBot = require('node-telegram-bot-api');
const { networkInterfaces } = require('os');

// ================================
// Configuration
// ================================
const GEMINI_API_KEY = "AIzaSyBGuxhNZvX_HyfoQHIUdWHAsnpS36ToxTU";
const GEMINI_API_ENDPOINT = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-thinking-exp:generateContent?key=${GEMINI_API_KEY}`;
const TELEGRAM_BOT_TOKEN = "7942491688:AAGO6osIzsLXTd0VOhn01BTGm4tC8VZ-Pkw";
const BASE_CODES_FOLDER = "C:\\Users\\hillel1\\Desktop\\AI\\codes";
const BASE_BACKUPS_FOLDER = "C:\\Users\\hillel1\\Desktop\\AI\\backups";
const TEMP_UPDATE_FILE = path.join(BASE_CODES_FOLDER, "update_temp.js");
const UPDATE_PY_SCRIPT = path.join(__dirname, "update.py"); // Assumes update.py is in the same directory
const CURRENT_SYSTEM_FILE = __filename;
const SEARCH_FILE_SCRIPT = path.join(__dirname, "search_file.py"); // Path to the Python file search script

// Cloudflare Whisper API Configuration
const CLOUDFLARE_ACCOUNT_ID = "38a8437a72c997b85a542a6b64a699e2";
const CLOUDFLARE_API_TOKEN = "jCnlim7diZ_oSCKIkSUxRJGRS972sHEHfgGTmDWK";
const CLOUDFLARE_WHISPER_API_ENDPOINT = `https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/ai/run/@cf/openai/whisper-large-v3-turbo`;

// Error database to learn from previous errors

// Create necessary folders if they don't exist
if (!fs.existsSync(BASE_CODES_FOLDER)) {
  fs.mkdirSync(BASE_CODES_FOLDER, { recursive: true });
}
if (!fs.existsSync(BASE_BACKUPS_FOLDER)) {
  fs.mkdirSync(BASE_BACKUPS_FOLDER, { recursive: true });
}

// Cache: normalized request => { filePath, type }
let previousCommands = {};

// Initialize Telegram bot
let bot;
try {
    bot = new TelegramBot(TELEGRAM_BOT_TOKEN, { polling: true });
} catch (error) {
    console.error("Telegram Bot initialization failed:", error.message);
    bot = null; // Indicate bot is not available
}

// Keep track of chats currently being processed to prevent concurrent requests
const processingChats = {};


async function checkCodeActionSuccess(stdout, stderr) {
    console.log("🤔 Asking AI to verify code action success based on output...");
    const verificationPrompt =
        "Answer 'yes' or 'no' only in English. " +
        "An AI assistant ran some code to perform a user's request. " +
        "Based on the output of the code, determine if the code execution was successful in performing the requested action.\n\n" +
        "Code Output (stdout):\n" + stdout + "\n\n" +
        "Code Error Output (stderr):\n" + stderr + "\n\n" +
        "Was the code execution successful in performing the user's intended action? Answer 'yes' or 'no' ONLY.";

    const responseJson = await sendRequestToAI(verificationPrompt);
    if (!responseJson) return false; // Assume failure if no response
    const { text: aiResponseText } = processAIResponse(responseJson);
    if (aiResponseText) {
        const normalizedResponse = aiResponseText.trim().toLowerCase();
        if (normalizedResponse === 'yes') {
            console.log("👍 AI verification: Action was likely successful.");
            return true;
        } else if (normalizedResponse === 'no') {
            console.log("👎 AI verification: Action was likely NOT successful.");
            return false;
        } else {
            console.warn("⚠️ Unexpected AI verification response:", normalizedResponse);
            return false; // Treat unexpected response as failure
        }
    }
    return false; // Assume failure if response is empty or cannot be processed
}

// ================================
// Self-Update Functionality
// ================================
async function updateSystem(userRequest, source, telegramChatId = null) {
  // Backup the current system file
  const currentFile = CURRENT_SYSTEM_FILE;
  let currentCode = "";
  try {
    currentCode = fs.readFileSync(currentFile, 'utf8');
  } catch (err) {
    console.error("Error reading current system file:", err);
    if (source === "telegram" && telegramChatId && bot) {
      try { bot.sendMessage(telegramChatId, "Error reading current system file."); } catch (e) { console.error("Telegram Send Error:", e.message); }
    }
    return;
  }

  const backupFilePath = path.join(BASE_BACKUPS_FOLDER, `backup_${Date.now()}.js`);
  try {
    fs.writeFileSync(backupFilePath, currentCode, { encoding: 'utf8' });
  } catch (error) {
    const errMsg = "Error saving backup file.";
    console.error(errMsg, error);
    if (source === "terminal") {
      console.log(errMsg);
    } else if (source === "telegram" && telegramChatId && bot) {
      try { bot.sendMessage(telegramChatId, errMsg); } catch (e) { console.error("Telegram Send Error:", e.message); }
    }
    return;
  }

  // Build a prompt for system update.
  const prompt =
    "Answer only in English. You are an AI assistant responsible for maintaining a system. " +
    "When the user requests an update to the system, do not include any commentary or markdown formatting; " +
    "provide only the complete updated system code. " +
    "Do NOT include any header comments or any text outside of the javascript code itself. " + // Modified prompt - No header comment
    "Just provide the complete, valid javascript code for the entire system.\n\n" + // Explicit instruction for only JS code
    "Current System Code:\n" + currentCode + "\n\n" +
    "User Update Request:\n" + userRequest + "\n\n" +
    "Please provide the complete updated system code ONLY."; // Emphasize ONLY code


  if (source === "terminal") {
    console.log("Sending update request to the AI...");
  } else if (source === "telegram" && telegramChatId && bot) {
    try { bot.sendMessage(telegramChatId, "Processing system update request..."); } catch (e) { console.error("Telegram Send Error:", e.message); }
  }

  let responseJson = null;
  while (!responseJson) {
    if (!isInternetConnected()) {
      console.log("No internet connection, waiting for connection...");
      if (source === "telegram" && telegramChatId && bot) {
        try { bot.sendMessage(telegramChatId, "No internet connection, waiting for connection..."); } catch (e) { console.error("Telegram Send Error:", e.message); }
      }
      await new Promise(resolve => setTimeout(resolve, 15000)); // Wait 15 seconds before retrying
      continue;
    }

    responseJson = await sendRequestToAI(prompt);
    if (!responseJson) {
      const errMsg = "Failed to receive an update from the AI. Retrying...";
      console.error(errMsg);
      if (source === "terminal") {
        console.log(errMsg);
      } else if (source === "telegram" && telegramChatId && bot) {
        try { bot.sendMessage(telegramChatId, errMsg); } catch (e) { console.error("Telegram Send Error:", e.message); }
      }
      await new Promise(resolve => setTimeout(resolve, 15000)); // Wait before retrying
    }
  }


  const { text: newCode, type } = processAIResponse(responseJson);
  if (type !== "code" || !newCode) {
    const errMsg = "Invalid update response from the AI. Could not parse system code.";
    console.error(errMsg);
    if (source === "terminal") {
      console.log(errMsg);
    } else if (source === "telegram" && telegramChatId && bot) {
        try { bot.sendMessage(telegramChatId, errMsg); } catch (e) { console.error("Telegram Send Error:", e.message); }
    }
    return;
  }

  // Save the new code to a temporary update file
  try {
    fs.writeFileSync(TEMP_UPDATE_FILE, newCode, { encoding: 'utf8' });
  } catch (error) {
    const errMsg = "Error saving the updated system code to temporary file.";
    console.error(errMsg, error);
    if (source === "terminal") {
      console.log(errMsg);
    } else if (source === "telegram" && telegramChatId && bot) {
        try { bot.sendMessage(telegramChatId, errMsg); } catch (e) { console.error("Telegram Send Error:", e.message); }
    }
    return;
  }

  const replyMsg = "System update code received. Updating system now...";
  if (source === "terminal") {
    console.log(replyMsg);
  } else if (source === "telegram" && telegramChatId && bot) {
      try { bot.sendMessage(telegramChatId, replyMsg); } catch (e) { console.error("Telegram Send Error:", e.message); }
  }

  // Call the external Python updater script update.py and pass the temporary update file
  const updater = spawn("python", [UPDATE_PY_SCRIPT, TEMP_UPDATE_FILE], { // Use UPDATE_PY_SCRIPT here
    stdio: "inherit",
    shell: true
  });

  updater.on("error", (err) => {
    console.error("Failed to spawn update.py:", err);
    if (source === "telegram" && telegramChatId && bot) {
        try { bot.sendMessage(telegramChatId, "Failed to run update.py. Make sure Python is installed and update.py is in the same folder as ai.js."); } catch (e) { console.error("Telegram Send Error:", e.message); }
    }
  });

  updater.on("close", (code) => {
    // The updater script is responsible for replacing ai.js and restarting
    // and now also for rollback if restart fails.
    // No need to process exit code here in ai.js, update.py handles it.
    process.exit(0); // ai.js will exit, and if update.py succeeded in restarting, the new version will run.
  });
}

// ================================
// Helper Functions
// ================================

// --- Helper Functions ---

// Example error database – add as many known errors as you like.
const errorDB = {
    // When the stderr contains this substring, return the known fix.
    "ModuleNotFoundError": "Missing module error – please run pip install for the module",
    // You can add other error patterns here.
};

function checkKnownErrors(stderr) {
    for (let error in errorDB) {
        if (stderr.includes(error)) {
            console.log(`🔍 Known issue detected: ${errorDB[error]}`);
            return errorDB[error]; // Return the known fix string
        }
    }
    return null;
}


// Recursively get all subfolders from the given directory.
function getAllSubfoldersRecursively(dir) {
    let results = [];
    try {
        const list = fs.readdirSync(dir);
        for (const file of list) {
            const fullPath = path.join(dir, file);
            try {
                const stat = fs.statSync(fullPath);
                if (stat && stat.isDirectory()) {
                    results.push(fullPath);
                    results = results.concat(getAllSubfoldersRecursively(fullPath));
                }
            } catch (err) {
                // Ignore permission errors or operation not permitted errors
                if (err.code !== 'EACCES' && err.code !== 'EPERM') {
                    console.error("Error reading file stats for", fullPath, err);
                }
            }
        }
    } catch (err) {
        if (err.code !== 'EACCES' && err.code !== 'EPERM') {
            console.error("Error reading directory:", dir, err);
        }
    }
    return results;
}


// Search a given subfolder for files that are similar to the searchTerm.
// For demonstration, this uses a simple case-insensitive substring match.
function searchSubfolder(subfolder, searchTerm) {
    let results = [];
    try {
        const list = fs.readdirSync(subfolder);
        for (const file of list) {
            const fullPath = path.join(subfolder, file);
            try {
                const stat = fs.statSync(fullPath);
                if (stat && stat.isFile()) {
                    const baseName = path.parse(file).name.toLowerCase();
                    const term = searchTerm.toLowerCase();
                    // נניח שנעשה השוואה פשוטה ונשתמש בציון 100 אם הקובץ כולל את המחרוזת, אחרת 50
                    let score = baseName.includes(term) ? 100 : 50;
                    results.push({
                        path: fullPath,
                        score: score,
                        name: file,
                        size: stat.size // הוספת גודל הקובץ (בבתים)
                    });
                }
            } catch (err) {
                console.error("Error reading file stats for", fullPath, err);
            }
        }
    } catch (err) {
        console.error("Error reading directory:", subfolder, err);
    }
    return results;
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  let kb = bytes / 1024;
  if (kb < 1024) return kb.toFixed(1) + ' KB';
  let mb = kb / 1024;
  if (mb < 1024) return mb.toFixed(1) + ' MB';
  let gb = mb / 1024;
  return gb.toFixed(1) + ' GB';
}


// --- Updated Callback Query Handler ---
if (bot) {
    bot.on("callback_query", async (callbackQuery) => {
        const data = callbackQuery.data;
        const chatId = callbackQuery.message.chat.id;
        const messageId = callbackQuery.message.message_id; // used for editing or deleting the message

        // Handle choosing a file
        if (data.startsWith("choose_file_")) {
            const index = parseInt(data.replace("choose_file_", ""), 10);
            const context = bot._fileSearchContext;
            if (context && context.similarFilesList && context.similarFilesList[index]) {
                const filePath = context.similarFilesList[index].path;
                try {
                    await bot.sendDocument(chatId, filePath);
                } catch (error) {
                    console.error("Error sending document:", error);
                }
            }
            bot.answerCallbackQuery(callbackQuery.id);
        
        // Handle pagination (Next/Previous)
        } else if (data === "paginate_next" || data === "paginate_prev") {
            const context = bot._fileSearchContext;
            if (!context) {
                bot.answerCallbackQuery(callbackQuery.id, { text: "No context found." });
                return;
            }
            
            let newPage = context.currentPage;
            if (data === "paginate_next") {
                newPage++;
            } else if (data === "paginate_prev") {
                newPage--;
            }
            
            const totalPages = Math.ceil(context.similarFilesList.length / context.pageSize);
            if (newPage < 0) newPage = 0;
            if (newPage >= totalPages) newPage = totalPages - 1;
            context.currentPage = newPage;
            
            const startIndex = newPage * context.pageSize;
            const endIndex = Math.min(startIndex + context.pageSize, context.similarFilesList.length);
            
            const paginatedButtons = context.similarFilesList.slice(startIndex, endIndex).map((file, index) => [
                {
                    text: `${path.basename(file.path)} (${file.score.toFixed(0)}%, ${formatFileSize(file.size)})`,
                    callback_data: `choose_file_${startIndex + index}`
                }
            ]);

            let navigationButtons = [];
            if (newPage > 0) {
                navigationButtons.push({ text: "Previous", callback_data: "paginate_prev" });
            }
            if (newPage < totalPages - 1) {
                navigationButtons.push({ text: "Next", callback_data: "paginate_next" });
            }
            if (navigationButtons.length > 0) {
                paginatedButtons.push(navigationButtons);
            }
            
            try {
                await bot.editMessageReplyMarkup(
                    { inline_keyboard: paginatedButtons },
                    {
                        chat_id: chatId,
                        message_id: messageId
                    }
                );
            } catch (error) {
                console.error("Error editing message reply markup:", error);
            }
            bot.answerCallbackQuery(callbackQuery.id);
        
        // Handle "Search Entire Directory" button
        } else if (data === "search_all_yes") {
            bot.answerCallbackQuery(callbackQuery.id);
            try {
                await bot.deleteMessage(chatId, messageId);
            } catch (err) {
                console.error("Failed to delete prompt message:", err.message);
            }
            await bot.sendMessage(chatId, "Starting search in the entire user directory...");
            handleFullUserDirectorySearch(chatId);
        
        // Handle "No, stop searching" button
        } else if (data === "search_all_no") {
            bot.answerCallbackQuery(callbackQuery.id);
            try {
                await bot.deleteMessage(chatId, messageId);
            } catch (err) {
                console.error("Failed to delete prompt message:", err.message);
            }
            await bot.sendMessage(chatId, "Search canceled.");
        }
    });
}

async function processRequest(userRequest, source, telegramChatId = null) {
    try {
        const parsedRequest = JSON.parse(userRequest);
        if (parsedRequest.is_search_file === true) {
            const folder = parsedRequest.folder || "Desktop";
            const searchResults = await handleFileSearch(parsedRequest.file_name, folder, source, telegramChatId);
            
            if (searchResults && searchResults.exact_match) {
                await bot.sendDocument(telegramChatId, searchResults.exact_match.path);
                return;
            }
        }
    } catch (e) {
        console.error("Error processing JSON search response:", e);
    }
}


// --- Full Directory Search Functions ---

// This function performs a full user directory search without AI filtering.
// It edits a single status message to show the current subfolder being searched.
async function handleFullUserDirectorySearch(chatId) {
    // Create a context object for full search
    bot._fullSearchContext = {
        stopped: false,
        partialResults: [],
        currentMessageId: null
    };

    const userDir = path.join("C:\\Users\\hillel1"); // Adjust as needed
    // Get all subfolders recursively
    const subfolders = getAllSubfoldersRecursively(userDir);

    // Send an initial status message with a "Stop" button
    const initialMessage = await bot.sendMessage(chatId, "Searching entire user directory...\n(Current directory will be shown here)", {
        reply_markup: {
            inline_keyboard: [[
                { text: "Stop", callback_data: "stop_full_search" }
            ]]
        }
    });
    bot._fullSearchContext.currentMessageId = initialMessage.message_id;

    // Iterate through each subfolder, editing the status message to show the current folder
    for (let i = 0; i < subfolders.length; i++) {
        if (bot._fullSearchContext.stopped) break;

        const subfolder = subfolders[i];
        try {
            await bot.editMessageText(
                `Searching entire user directory...\nNow searching in: ${path.basename(subfolder)}`,
                {
                    chat_id: chatId,
                    message_id: bot._fullSearchContext.currentMessageId,
                    reply_markup: {
                        inline_keyboard: [[
                            { text: "Stop", callback_data: "stop_full_search" }
                        ]]
                    }
                }
            );
        } catch (err) {
            console.error("Failed to edit searching message:", err.message);
        }

        // Search the current subfolder for files (without AI filtering)
        const foundFiles = searchSubfolder(subfolder, ""); // Pass an empty search term or adjust as needed
        bot._fullSearchContext.partialResults.push(...foundFiles);
    }

    // When finished or stopped, show the results
    if (!bot._fullSearchContext.stopped) {
        await showFullSearchResults(chatId, bot._fullSearchContext.partialResults);
    }
    bot._fullSearchContext = null;
}

// This function displays the final or partial search results without AI filtering.
async function showFullSearchResults(chatId, allFiles) {
    if (allFiles.length === 0) {
        await bot.sendMessage(chatId, "No files found in the entire user directory.");
        return;
    }
    // Sort results in descending order by score
    allFiles.sort((a, b) => b.score - a.score);

    // Paginate results (8 per page)
    const pageSize = 8;
    const totalPages = Math.ceil(allFiles.length / pageSize);
    const initialResults = allFiles.slice(0, pageSize);
    const paginatedButtons = initialResults.map((file, index) => [{
        text: `${path.basename(file.path)} (${file.score.toFixed(0)}%)`,
        callback_data: `choose_file_full_${index}`
    }]);
    let navigationButtons = [];
    if (totalPages > 1) {
        navigationButtons.push({ text: "Next", callback_data: "full_search_next" });
    }
    if (navigationButtons.length > 0) {
        paginatedButtons.push(navigationButtons);
    }
    const resultsMessage = "Results from entire user directory:";
    await bot.sendMessage(chatId, resultsMessage, {
        reply_markup: { inline_keyboard: paginatedButtons }
    });
}


function getSubfolder(ext) {
  ext = ext.toLowerCase();
  switch (ext) {
    case '.py':   return 'Python';
    case '.html': return 'HTML';
    case '.js':   return 'JavaScript';
    case '.css':  return 'Style';
    case '.txt':  return 'Text';
    case '.json':  return 'JSON';
    case '.xml':  return 'XML';
    case '.java':  return 'Java';
    case '.c':  return 'C';
    case '.cpp':  return 'C++';
    case '.cs':  return 'CSharp';
    case '.php':  return 'PHP';
    case '.rb':  return 'Ruby';
    case '.swift':  return 'Swift';
    case '.go':  return 'Go';
    case '.sh':  return 'Shell';
    case '.bat':  return 'Batch';
    default:      return 'Others';
  }
}

async function sendRequestToAI(prompt) {
   await new Promise(resolve => setTimeout(resolve, 500)); // Introduce a delay
  try {
    const response = await axios.post(
      GEMINI_API_ENDPOINT,
      { contents: [{ role: "user", parts: [{ text: prompt }] }] },
      { headers: { "Content-Type": "application/json" } }
    );
    return response.data;
  } catch (error) {
    console.error("Error communicating with the AI API:", error);
    return null;
  }
}

async function transcribeAudio(audioBase64) {
    try {
        const requestBody = {
            audio: audioBase64,
            task: "transcribe"
            // No language specified for auto-detection
        };

        const transcriptionResponse = await axios.post(CLOUDFLARE_WHISPER_API_ENDPOINT, requestBody, {
            headers: {
                "Authorization": `Bearer ${CLOUDFLARE_API_TOKEN}`,
                "Content-Type": "application/json"
            },
            responseType: 'json'
        });

        if (transcriptionResponse.data.result && transcriptionResponse.data.result.text) {
            return transcriptionResponse.data.result.text;
        } else {
            console.error("Transcription result not found in response:", transcriptionResponse.data);
            return null;
        }
    } catch (error) {
        console.error("Error during audio transcription:", error);
        return null;
    }
}


function processAIResponse(responseJson) {
  try {
    let aiText = responseJson.candidates[0].content.parts[0].text;
    if (aiText.startsWith("```")) {
      const lines = aiText.split("\n");
      if (lines[0].startsWith("```")) lines.shift();
      if (lines.length && lines[lines.length - 1].startsWith("```")) lines.pop();
      aiText = lines.join("\n");
    }
    const codeKeywords = ["import ", "def ", "os.", "subprocess", "sys", "if __name__", "print(", "//", "function", "var ", "const ", "<script", "<style", "<html", "<body", "<?php", "class ", "public static void main", "using System;", "package "]; // Extended code keywords
    const isCode = codeKeywords.some(keyword => aiText.includes(keyword));
    return { text: aiText, type: isCode ? "code" : "message" };
  } catch (error) {
    return { text: null, type: "error" };
  }
}

function extractFilename(codeStr) {
  const lines = codeStr.split("\n");
  for (const line of lines) {
    if (line.trim().startsWith("# File:")) {
      let filename = line.split(":", 2)[1].trim();
      return filename; // Extension is now part of the filename from AI
    }
  }
  return null;
}

function saveCodeToFile(codeStr, filePath) { // Modified to accept filePath
  try {
    fs.writeFileSync(filePath, codeStr, { encoding: "utf-8" }); // Use provided filePath
    return filePath;
  } catch (error) {
    console.error("Error saving file:", error);
    return null;
  }
}

function runPythonCode(filePath) {
  return new Promise((resolve) => {
    const proc = spawn("python", [filePath], { shell: true });
    let stdout = "";
    let stderr = "";
    proc.stdout.on("data", data => { stdout += data.toString(); });
    proc.stderr.on("data", data => { stderr += data.toString(); });
    proc.on("close", (code) => {
      resolve({ code, stdout, stderr });
    });
  });
}

async function runCode(filePath) {
    const ext = path.extname(filePath).toLowerCase();
    if (ext === ".py") {
        const result = await runPythonCode(filePath);
        if (result.code === 0) {
            console.log("Code ran successfully (initial execution).");
            const actionSuccess = await checkCodeActionSuccess(result.stdout, result.stderr); // Call verification function
            if (actionSuccess) {
                return { code: 0, stdout: result.stdout, stderr: result.stderr, actionSuccess: true }; // Indicate action success
            } else {
                return { code: 1, stdout: result.stdout, stderr: result.stderr, actionSuccess: false }; // Treat as code failure if action not successful
            }
        } else {
            console.error("Code execution error:", result.stderr);
            return { code: result.code, stdout: result.stdout, stderr: result.stderr, actionSuccess: false };
        }
    } else {
        return { code: 0, stdout: "", stderr: "", actionSuccess: true }; // Non-Python code assumed successful execution for now
    }
}

async function tryFixCode(errorMessage, stdout, originalCode) {
    // Check if errorMessage indicates a missing module
    if (/ModuleNotFoundError: No module named ['"]([^'"]+)['"]/.test(errorMessage)) {
        const match = errorMessage.match(/No module named ['"]([^'"]+)['"]/);
        if (match && match[1]) {
            const moduleName = match[1];
            console.log(`Missing module detected: ${moduleName}. Installing...`);
            try {
                const pipInstall = spawn("pip", ["install", moduleName], { shell: true });
                pipInstall.stdout.on("data", data => console.log(data.toString()));
                pipInstall.stderr.on("data", data => console.error(data.toString()));
                await new Promise(resolve => pipInstall.on("close", resolve));
                console.log(`Module ${moduleName} installed successfully.`);
            } catch (installError) {
                console.error("Failed to install module:", installError);
            }
        }
    }

    // Build prompt for AI fix (with additional instruction for missing module errors)
    const prompt =
        "Answer only in English. You are an AI assistant that generates code to perform actions on a computer. " +
        "When generating code, do not include markdown formatting or additional commentary. " +
        "If you see an error indicating that a module is not found (e.g., 'ModuleNotFoundError: No module named ...'), " +
        "assume that the missing module has been installed via 'pip install <module>' and output the updated, fixed code only. " +
        "Provide ONLY the corrected code, including a header comment with the filename in the format '# File: descriptive_name.ext'.\n\n" +
        "Original Code:\n" + originalCode + "\n\n" +
        "Code Output (stdout):\n" + stdout + "\n\n" +
        "Error Message (stderr):\n" + errorMessage + "\n\n" +
        "Please provide the updated, fixed code only.";

    const responseJson = await sendRequestToAI(prompt);
    if (!responseJson) return null;
    const { text, type } = processAIResponse(responseJson);
    return type === "code" ? text : null;
}


async function emergencyCodeFallback(originalCode, userRequest) {
    console.log("⚠️ All fixes failed! Generating alternative solution...");
    const emergencyPrompt = `Rewrite this code in a completely different way that does the same thing, based on the user request: ${userRequest}. Original code (for context, do not reuse directly):\n${originalCode}`;
    const responseJson = await sendRequestToAI(emergencyPrompt);
    if (!responseJson) return null;
    const { text: emergencyCode, type } = processAIResponse(responseJson);
    if (type === "code") {
        console.log("🚀 Alternative code generated. Trying again...");
        return emergencyCode;
    }
    console.log("❌ Failed to generate emergency code.");
    return null;
}

async function explainError(errorMessage, source, telegramChatId) {
    console.log("🧐 Asking AI to explain the error...");
    const explanationPrompt = `Explain this error message in simple terms: ${errorMessage}`;
    const responseJson = await sendRequestToAI(explanationPrompt);
    if (!responseJson) return null;
    const { text: explanation, type } = processAIResponse(responseJson);
    if (explanation) {
        console.log(`📢 AI Explanation: ${explanation}`);
        if (source === "telegram" && telegramChatId && bot) {
            try { bot.sendMessage(telegramChatId, `AI Explanation: ${explanation}`); } catch (e) { console.error("Telegram Send Error:", e.message); }
        }
    }
}

function isCodeSafe(codeText) {
    const dangerousCommands = ["rm -rf", "shutdown", "del /f", "format C:", "sudo", "chmod", ":(){:|:&};:", "%0|%0"]; // Added more dangerous commands
    const lowerCode = codeText.toLowerCase();
    return !dangerousCommands.some(cmd => lowerCode.includes(cmd));
}


async function fixCodeLoop(codeText, filePath, source, telegramChatId, userRequest) {
    let attempt = 0;
    let lastResult = null;
    while (attempt < 15) {
        attempt++;
        if (attempt > 1) {
            const msg = `Attempt ${attempt}: Fixing the code and retrying...`;
            console.log(msg);
            if (source === "telegram" && telegramChatId && bot) {
                bot.sendMessage(telegramChatId, msg);
            }
        }
        if (!isCodeSafe(codeText)) {
            const unsafeMsg = "Unsafe code detected! Execution stopped.";
            console.error(unsafeMsg);
            if (source === "telegram" && telegramChatId && bot) {
                bot.sendMessage(telegramChatId, unsafeMsg);
            }
            return { filePath, success: false, result: { code: -1, stderr: "Unsafe code detected", stdout: "" } };
        }
        let knownFix = checkKnownErrors(lastResult ? lastResult.stderr : "");
        if (knownFix) {
            console.log("Applying known fix automatically...");
            codeText = knownFix;
        }
        saveCodeToFile(codeText, filePath);
        const result = await runCode(filePath); // Run the code
        lastResult = result;

        // Check BOTH result.code AND result.actionSuccess
        if (result.code === 0 && result.actionSuccess === true) {
            const successMsg = `Code fixed successfully after ${attempt} attempt(s)!`;
            console.log(successMsg);
            if (source === "telegram" && telegramChatId && bot) {
                bot.sendMessage(telegramChatId, successMsg);
            }
            return { filePath, success: true, result };
        } else {
            // Call fixCodeLoopInner with the original codeText as the context
            const fixedCode = await fixCodeLoopInner(codeText, lastResult, source, telegramChatId);
            if (!fixedCode) {
                if (attempt < 15) {
                    const emergencyCode = await emergencyCodeFallback(codeText, userRequest);
                    if (emergencyCode) {
                        codeText = emergencyCode;
                        console.log("Trying emergency fallback code...");
                        if (source === "telegram" && telegramChatId && bot) {
                            bot.sendMessage(telegramChatId, "Trying emergency fallback code...");
                        }
                    } else {
                        console.error("Emergency code generation failed. Stopping retries.");
                        if (source === "telegram" && telegramChatId && bot) {
                            bot.sendMessage(telegramChatId, "Emergency code generation failed. Stopping retries.");
                        }
                        break;
                    }
                } else {
                    console.error("AI failed to generate a fix. Stopping...");
                    if (source === "telegram" && telegramChatId && bot) {
                        bot.sendMessage(telegramChatId, "AI failed to generate a fix. Stopping...");
                    }
                    break;
                }
            } else {
                codeText = fixedCode;
            }
        }
    }
    if (lastResult && lastResult.code !== 0) {
        const failMsg = `Failed to fix the code after ${attempt} attempts.`;
        console.error(failMsg);
        if (source === "terminal") {
            console.log(failMsg);
            await explainError(lastResult.stderr, source, telegramChatId);
        } else if (source === "telegram" && telegramChatId && bot) {
            bot.sendMessage(telegramChatId, failMsg);
            await explainError(lastResult.stderr, source, telegramChatId);
        }
        // Store the error and the attempted code in errorDB for future reference
        errorDB[lastResult.stderr] = codeText;
    }
    return { filePath, success: false, result: lastResult };
}

// Inner fix loop to prevent recursion issues
async function fixCodeLoopInner(codeText, result, source, telegramChatId) {
    // Corrected call to tryFixCode: Pass 'codeText' as originalCode, and result.stdout/stderr
    const fixedCode = await tryFixCode(result.stderr, result.stdout, codeText);
    if (!fixedCode) {
        console.error("Code fixing by AI failed.");
        if (source === "telegram" && telegramChatId && bot) {
            bot.sendMessage(telegramChatId, "Code fixing by AI failed.");
        }
        return null;
    }
    console.log("AI provided a fix. Trying the fixed code...");
    if (source === "telegram" && telegramChatId && bot) {
        bot.sendMessage(telegramChatId, "AI provided a fix. Trying the fixed code...");
    }
    return fixedCode;
}

function getExistingPythonFiles() {
  const pythonFolderPath = path.join(BASE_CODES_FOLDER, 'Python');
  try {
    if (!fs.existsSync(pythonFolderPath)) {
      return []; // Return empty array if folder doesn't exist
    }
    const files = fs.readdirSync(pythonFolderPath);
    return files.filter(file => path.extname(file).toLowerCase() === '.py'); // Filter for .py files
  } catch (error) {
    console.error("Error reading Python code folder:", error);
    return []; // Return empty array in case of error
  }
}

function isInternetConnected() {
    const interfaces = networkInterfaces();
    for (const name of Object.keys(interfaces)) {
        const iface = interfaces[name];
            if (!iface) continue; // Skip if interface is null or undefined
        for (const alias of iface) {
            if (alias.family === 'IPv4' && alias.address !== '127.0.0.1' && !alias.internal) {
                return true; // Found a non-loopback IPv4 address, likely connected to internet
            }
        }
    }
    return false; // No external IPv4 address found, likely no internet
}


async function generateGame(gameDescription, source, telegramChatId) {
    console.log("🎮 Generating a game: " + gameDescription);
    if (source === "telegram" && telegramChatId && bot) {
        try { bot.sendMessage(telegramChatId, "🎮 Generating a game: " + gameDescription); } catch (e) { console.error("Telegram Send Error:", e.message); }
    }

    const gamePrompt = `Write a simple game in Python based on this description: ${gameDescription}. Include comments to explain the code.`;
    const responseJson = await sendRequestToAI(gamePrompt);
    if (!responseJson) return { success: false };
    const { text: gameCode, type } = processAIResponse(responseJson);

    if (type === "code" && gameCode) {
        const filePath = generateCodeFilePath(gameCode);
        const savedFilePath = saveCodeToFile(gameCode, filePath);
        console.log(`🎮 Game created: ${savedFilePath}`);
        if (source === "telegram" && telegramChatId && bot) {
            try { bot.sendMessage(telegramChatId, `🎮 Game created: ${path.basename(savedFilePath)}`); } catch (e) { console.error("Telegram Send Error:", e.message); }
        }
        return { success: true, filePath: savedFilePath };
    } else {
        console.log("❌ Failed to generate game code.");
        if (source === "telegram" && telegramChatId && bot) {
            try { bot.sendMessage(telegramChatId, "❌ Failed to generate game code."); } catch (e) { console.error("Telegram Send Error:", e.message); }
        }
        return { success: false };
    }
}

function generateCodeFilePath(codeStr) {
    let filename = extractFilename(codeStr);
    if (!filename) {
        filename = `action_${Date.now()}.py`; // Default to .py if filename extraction fails - but filename should now include extension
    }
    const ext = path.extname(filename).toLowerCase() || '.py'; // Ensure there's always an extension
    const subfolder = getSubfolder(ext);
    const folderPath = path.join(BASE_CODES_FOLDER, subfolder);
    if (!fs.existsSync(folderPath)) {
        fs.mkdirSync(folderPath, { recursive: true });
    }
    return path.join(folderPath, filename);
}


async function filterAndSortFilesWithAI(userRequest, files) {
    const prompt = `You are an AI assistant. The user requested: "${userRequest}". 
Here is a list of file objects in JSON format (each object has "path" and "score"):
${JSON.stringify(files)}
Please filter out any files that are not relevant to the user's request and sort the remaining files in descending order of relevance. Return only the filtered and sorted list in valid JSON format without any additional commentary.`;
    
    const responseJson = await sendRequestToAI(prompt);
    if (!responseJson) {
        console.error("AI did not return a response for file filtering.");
        return files; // אם אין תגובה, נחזיר את הרשימה המקורית
    }
    const aiResponse = processAIResponse(responseJson);
    if (!aiResponse.text) {
        console.error("Empty AI response for file filtering.");
        return files;
    }
    try {
        const filteredFiles = JSON.parse(aiResponse.text);
        return filteredFiles;
    } catch (e) {
        console.error("Error parsing AI response for file filtering:", e);
        return files;
    }
}

// ================================
// New File Search Functionality
// ================================
/**
 * Handles file search requests by spawning a Python script that searches
 * for the specified file and returns its location.
 */
async function handleFileSearch(fileName, folder, source, telegramChatId) {
    const predefinedFolders = [
        path.join("C:\\Users\\hillel1", "Desktop"),
        path.join("C:\\Users\\hillel1", "Documents"),
        path.join("C:\\Users\\hillel1", "Downloads"),
        path.join("C:\\Users\\hillel1", "Music"),
        path.join("C:\\Users\\hillel1", "Pictures"),
        path.join("C:\\Users\\hillel1", "Videos")
    ];
    let bestMatch = null;
    let similarFilesList = [];

    // מערך לאיסוף ה-message_id של הודעות "🔍 Searching in X"
    const searchMessagesIds = [];

    async function executeFileSearch(searchFolder) {
        console.log(`🔍 Searching for "${fileName}" in folder "${searchFolder}"...`);

        // שולחים הודעה "🔍 Searching in X" ושומרים את ה-message_id למחיקה מאוחר יותר
        let searchingMsgId = null;
        if (source === "telegram" && telegramChatId && bot) {
            try {
                const sentMsg = await bot.sendMessage(telegramChatId, `🔍 Searching in "${path.basename(searchFolder)}"...`);
                searchingMsgId = sentMsg.message_id;
                searchMessagesIds.push(searchingMsgId);
            } catch (e) {
                console.error("Telegram Send Error (searching message):", e.message);
            }
        }

        console.log(`Debug: Calling search_file.py with fileName: "${fileName}", folder: "${searchFolder}"`);
        const searchProcess = spawn("python", [SEARCH_FILE_SCRIPT, fileName, searchFolder]);
        let stdout = "";
        let stderr = "";
        searchProcess.stdout.on("data", data => { stdout += data.toString(); });
        searchProcess.stderr.on("data", data => { stderr += data.toString(); });
        return new Promise((resolve) => {
            searchProcess.on("close", (code) => {
                if (code === 0) {
                    try {
                        const searchResults = JSON.parse(stdout);
                        console.log("Debug: search_file.py JSON output:", searchResults);
                        resolve(searchResults);
                    } catch (parseError) {
                        console.error("❌ Error parsing JSON response from search_file.py:", parseError);
                        console.error("Stdout from search_file.py:", stdout);
                        resolve({ error: "File search failed due to an error processing the search results." });
                    }
                } else {
                    let errorMsg = stderr.trim() || stdout.trim() || "Unknown error";
                    console.error("❌ File search script error:", errorMsg);
                    console.error(`Debug: search_file.py exited with code ${code}, stderr: "${stderr.trim()}", stdout: "${stdout.trim()}"`);
                    resolve({ error: "File search failed: " + errorMsg });
                }
            });
        });
    }

    // רשימת תיקיות לחיפוש – קודם התיקייה שהמשתמש בחר ואז התיקיות המוגדרות מראש.
    let foldersToSearch = [folder];
    for (const predefinedFolder of predefinedFolders) {
        if (path.resolve(predefinedFolder) !== path.resolve(folder)) {
            foldersToSearch.push(predefinedFolder);
        }
    }

    // מעבר על כל תיקיות החיפוש ואיסוף תוצאות.
    for (const searchFolder of foldersToSearch) {
        let searchResult = await executeFileSearch(searchFolder);
        if (searchResult.error) {
            continue; // במידה ויש שגיאה, ממשיכים לתיקייה הבאה
        }
        // בדיקה אם נמצא exact_match – והשוואה מדויקת של שם הקובץ (ללא סיומת)
        if (searchResult.exact_match) {
            const foundBaseName = path.parse(path.basename(searchResult.exact_match)).name;
            if (foundBaseName === fileName) {
                bestMatch = { location: searchResult.exact_match };
                break; // מצאנו התאמה מדויקת, אין צורך להמשיך
            } else {
                similarFilesList.push({
                    path: searchResult.exact_match,
                    score: 100
                });
            }
        }
        if (searchResult.similar_files && Array.isArray(searchResult.similar_files)) {
            similarFilesList = similarFilesList.concat(searchResult.similar_files);
        }
    }

    // אם נמצא קובץ במדויק – שולחים אותו ומחזירים
    if (bestMatch) {
        // לא ביקשת למחוק במקרה של exact match, אך אם תרצה – אפשר למחוק גם כאן
        const msg = `✅ File search complete. Found exact match: ${path.basename(bestMatch.location)}`;
        console.log(msg);
        if (source === "telegram" && telegramChatId && bot) {
            bot.sendMessage(telegramChatId, msg)
        }
        return { exact_match: bestMatch.location }; // Return the exact match location
    }

    // כאן אנחנו יודעים שאין exact match => מציגים את רשימת הקבצים הדומים
    // לפני כן – מוחקים את הודעות "🔍 Searching in X"
    if (source === "telegram" && telegramChatId && bot) {
        for (const msgId of searchMessagesIds) {
            try {
                await bot.deleteMessage(telegramChatId, msgId);
            } catch (err) {
                console.error("Failed to delete search message:", err.message);
            }
        }
    }

    // הסרת כפילויות לפי הנתיב
    const seenPaths = new Set();
    similarFilesList = similarFilesList.filter(file => {
        if (seenPaths.has(file.path)) return false;
        seenPaths.add(file.path);
        return true;
    });

    // מיון הקבצים מהגבוה לנמוך
    similarFilesList.sort((a, b) => b.score - a.score);

    // העברת הרשימה ל-AI לסינון ומיון לפי רלוונטיות
    const filteredSortedFiles = await filterAndSortFilesWithAI(fileName, similarFilesList);

    // אם לא נותרו קבצים לאחר הסינון – שואלים אם לחפש בתיקיית המשתמש המלאה
    if (filteredSortedFiles.length === 0) {
        const noMatchMsg = `❌ File not found in predefined folders.\nDo you want to search in the entire user directory (${path.dirname(predefinedFolders[0])})?`;
        console.log(noMatchMsg);
        if (source === "telegram" && telegramChatId && bot) {
            bot.sendMessage(telegramChatId, noMatchMsg, {
                reply_markup: {
                    inline_keyboard: [[
                        { text: 'Yes, search entire user directory', callback_data: 'search_all_yes' },
                        { text: 'No, stop searching', callback_data: 'search_all_no' }
                    ]]
                }
            });
        } else if (source === "terminal") {
            console.log("File not found.");
        }
        return { no_match: true }; // Indicate no match found
    }

    // אם כן נותרו קבצים => מציגים אותם עם כפתורי ניווט
    const pageSize = 8;
    const currentPage = 0;
    const totalPages = Math.ceil(filteredSortedFiles.length / pageSize);
    const paginatedButtons = filteredSortedFiles.slice(currentPage * pageSize, (currentPage + 1) * pageSize).map((file, index) => [{
        text: `${path.basename(file.path)} (${file.score.toFixed(0)}%)`,
        callback_data: `choose_file_${currentPage * pageSize + index}`
    }]);

    let navigationButtons = [];
    if (currentPage > 0) {
        navigationButtons.push({ text: "Previous", callback_data: "paginate_prev" });
    }
    if (currentPage < totalPages - 1) {
        navigationButtons.push({ text: "Next", callback_data: "paginate_next" });
    }

    const messageText = `⚠️ Exact file not found. Found similar files (filtered and sorted):\nChoose a file from the list below:`;
    console.log(messageText);
    if (source === "telegram" && telegramChatId && bot) {
        await bot.sendMessage(telegramChatId, messageText, {
            reply_markup: {
                inline_keyboard: [...paginatedButtons, navigationButtons.length > 0 ? navigationButtons : []]
            }
        });

        // שליחה בהודעה נפרדת לכפתור "Search Entire Directory"
        await bot.sendMessage(telegramChatId, "If none of these files match your needs, you can search in the entire user directory.", {
            reply_markup: {
                inline_keyboard: [[
                    { text: 'Search Entire Directory', callback_data: 'search_all_yes' },
                    { text: 'No, stop searching', callback_data: 'search_all_no' }
                ]]
            }
        });

        // שמירת הקשר לטיפול בבחירת הקבצים ובניווט
        bot._fileSearchContext = {
            similarFilesList: filteredSortedFiles,
            telegramChatId: telegramChatId,
            currentPage: currentPage,
            pageSize: pageSize
        };
    } else if (source === "terminal") {
        console.log(messageText);
    }
    return { similar_files: filteredSortedFiles }; // Return similar files if no exact match
}

async function handleFullUserSearchConfirmation(callbackQuery, fileName, telegramChatId) {
    const answer = callbackQuery.data;
    bot.answerCallbackQuery(callbackQuery.id);

    if (answer === 'search_all_yes') {
        await searchFullUserDirectory(fileName, telegramChatId);
    } else if (answer === 'search_all_no') {
        if (bot) {
            try { bot.sendMessage(telegramChatId, "File search cancelled by user."); } catch (e) { console.error("Telegram Send Error:", e.message); }
        } else if (source === "terminal") {
            console.log("File search cancelled.");
        }
    }
}


async function searchFullUserDirectory(fileName, telegramChatId) {
    const similarityThreshold = 80;
    const userDirectory = path.dirname(path.join("C:\\Users\\hillel1", "Desktop")); // C:\Users\hillel1

    if (bot) {
        try { bot.sendMessage(telegramChatId, `🔍 Searching in entire user directory (${userDirectory})...`); } catch (e) { console.error("Telegram Send Error:", e.message); }
    } else if (source === "terminal") {
        console.log(`Searching in entire user directory (${userDirectory})...`);
    }

    const searchResult = await executeFileSearch(userDirectory); // Reuse executeFileSearch

    if (searchResult.exact_match) {
        const msg = `✅ File search complete. Found exact match in user directory: ${path.basename(searchResult.exact_match)}`;
        console.log(msg);
        if (bot) {
            try { bot.sendMessage(telegramChatId, msg); } catch (e) { console.error("Telegram Send Error:", e.message); }
            bot.sendDocument(telegramChatId, searchResult.exact_match).catch(error => console.error("Error sending document:", error));
        }
    } else if (searchResult.similar_files) {
        const bestSimilarFile = searchResult.similar_files.find(file => file.score >= similarityThreshold);
        if (bestSimilarFile) {
            const msg = `⚠️ Exact file not found, but found similar file in user directory: ${path.basename(bestSimilarFile.path)} (Similarity: ${bestSimilarFile.score.toFixed(0)}%).`;
            console.log(msg);
            if (bot) {
                try { bot.sendMessage(telegramChatId, msg); } catch (e) { console.error("Telegram Send Error:", e.message); }
                bot.sendDocument(telegramChatId, bestSimilarFile.path).catch(error => console.error("Error sending document:", error));
            }
        } else {
            const noMatchMsg = `❌ File not found with required similarity (> ${similarityThreshold}%) even in the entire user directory.`;
            console.log(noMatchMsg);
            if (bot) {
                try { bot.sendMessage(telegramChatId, noMatchMsg); } catch (e) { console.error("Telegram Send Error:", e.message); }
            }
        }
    } else if (searchResult.no_match || searchResult.error) {
        const noMatchMsg = searchResult.error || `❌ File not found in user directory.`;
        console.log(noMatchMsg);
        if (bot) {
            try { bot.sendMessage(telegramChatId, noMatchMsg); } catch (e) { console.error("Telegram Send Error:", e.message); }
        }
    }
}




// ================================
// Main Request Processing
// ================================

async function processRequest(userRequest, source, telegramChatId = null, telegramUsername = null) {
    // Check if the user provided a JSON file search command directly
    try {
        const parsedRequest = JSON.parse(userRequest);
        if (parsedRequest.is_search_file === true) {
            const folder = parsedRequest.folder || "Desktop";
            const searchResults = await handleFileSearch(parsedRequest.file_name, folder, source, telegramChatId);

            if (searchResults && searchResults.exact_match) {
                await bot.sendDocument(telegramChatId, searchResults.exact_match);
                return;
            } else if (searchResults && searchResults.similar_files) { // Handle similar files if no exact match
                const paginatedButtons = searchResults.similar_files.slice(0, 8).map((file, index) => [{
                    text: `${path.basename(file.path)} (${file.score.toFixed(0)}%)`,
                    callback_data: `choose_file_${index}`
                }]);
            } else {
                // Handle case where no files are found (either exact or similar)
                const noMatchMsg = `❌ File not found in predefined folders.`;
                console.log(noMatchMsg);
                if (source === "telegram" && telegramChatId && bot) {
                    bot.sendMessage(telegramChatId, noMatchMsg);
                }
                return;
            }
        }
    } catch (e) {
        // Not a JSON file search command; proceed with regular processing.
    }


  // Check for Hebrew or English phrases meaning "update the system"
  if (/update the system|עדכן את המערכת|תעדכן את המערכת/i.test(userRequest)) {
    await updateSystem(userRequest, source, telegramChatId);
    return;
  }

  if (/^(create a game|generate a game|כתוב משחק|תיצור משחק)\s+(.+)$/i.test(userRequest)) { // Game request detection
      const gameMatch = userRequest.match(/^(create a game|generate a game|כתוב משחק|תיצור משחק)\s+(.+)$/i);
      const gameDescription = gameMatch ? gameMatch[2] : null;
      if (gameDescription) {
          await generateGame(gameDescription, source, telegramChatId);
          return;
      }
  }


  // For Telegram, allow only the authorized user (@HILLEL6767).
  if (source === "telegram" && telegramUsername !== "HILLEL6767") {
      if (bot) {
        try { bot.sendMessage(telegramChatId, "You are not authorized to use this bot."); } catch (e) { console.error("Telegram Send Error:", e.message); }
      }
    return;
  }

  const normalizedRequest = userRequest.toLowerCase();

  // Check if the command was previously generated, reuse it only if the file exists.
if (previousCommands[normalizedRequest]) {
  const cached = previousCommands[normalizedRequest];
  // Check if the cached file still exists on disk.
  if (!fs.existsSync(cached.filePath)) {
    // File does not exist: remove it from cache.
    delete previousCommands[normalizedRequest];
  } else {
    const replyMsg = "Reusing existing command: " + path.basename(cached.filePath);
    if (source === "terminal") {
      console.log(replyMsg);
    } else if (bot) {
      try {
        bot.sendMessage(telegramChatId, replyMsg);
      } catch (e) {
        console.error("Telegram Send Error:", e.message);
      }
    }
    const result = await runCode(cached.filePath);
    if (result.code !== 0 && cached.type === "python") {
      let errorMsg = "An error occurred with cached command " + path.basename(cached.filePath) + ". Please try again or generate a new command.";
      if (source === "terminal") {
        console.log(errorMsg);
      } else if (bot) {
        try {
          bot.sendMessage(telegramChatId, errorMsg);
        } catch (e) {
          console.error("Telegram Send Error:", e.message);
        }
      }
      return;
    } else {
      let successMsg = path.basename(cached.filePath) + " executed successfully.";
      if (source === "terminal") {
        console.log(successMsg);
      } else if (bot) {
        try {
          bot.sendMessage(telegramChatId, successMsg);
        } catch (e) {
          console.error("Telegram Send Error:", e.message);
        }
      }
      return;
    }
  }
}

  // Get list of existing Python files
  const existingPythonFiles = getExistingPythonFiles();
  const pythonFileListString = existingPythonFiles.length > 0 ? existingPythonFiles.join(", ") : "No Python files exist.";

  // Build the prompt with instructions, including file reuse instructions
  const prompt =
      "Answer only in English. You are an AI assistant that generates code, text documents, or file search commands based on the user's request. " +
      "When generating code, do not include markdown formatting. " +
      "Include a header comment in the format '# File: descriptive_name.ext', making sure to use the correct file extension for the file type.\n" +
      "IMPORTANT:\n" +
      "1. **Greetings and Simple Questions:** If the user says 'hi', 'hello', or asks 'how are you?', respond with a *short, simple TEXT MESSAGE* like 'Hello!' or 'I'm doing well, how can I help you?'. Do NOT generate code or files for greetings.\n" +
      "2. **File Search Requests:** If the user's request is to *SEARCH FOR A FILE*, output a JSON object in this format:  {\"is_search_file\": true, \"file_name\": \"<file name>\", \"folder\": \"<folder>\"}. (If the user provides a file name in any language other than English, search for it as is. However, if the user provides a folder name in a language other than English, search for it in English—unless the user explicitly states that they want to search for it in the original language.) If the folder is not specified, use 'Desktop'. Output *ONLY* the JSON, no other text.\n" +
      "3. **File Creation Requests:** If the user asks to *CREATE A FILE* (and specifies a file type, e.g., 'javascript file', 'html file', 'css file', 'java file', etc.), then generate the content for that file type.  Make sure to include the correct file extension in the '# File:' header comment. Respond with ONLY the file content (code or text), starting with the '# File:' header comment, and NO other commentary or explanation.\n" +
      "4. **Existing Python File Check:** **Before generating new Python code for action requests, check if there's an existing Python file in your 'Python code library' that could perform the requested action.** \n" +
      `**List of existing Python files in 'Python code library': ${pythonFileListString}**\n` + // Added file list to prompt
      "**If a filename from this list seems highly relevant (e.g., > 85% relevance) to the user's request,** **respond with a JSON object ONLY in the format: {\"reuse_file\": true, \"filename\": \"<relevant_filename.py>\"}. Do not provide any commentary or explanation in this JSON response.**\n" + // Instructions for JSON response to reuse file
      "**If no existing Python file is relevant enough, or if the user request is not an action requiring Python code, proceed to generate new code or respond as instructed in points 1, 2, or 3 above.**\n" + // Instruction to generate new code if no relevant file
      "5. **Action Requests (Default):** For *ALL OTHER* requests that imply performing an *ACTION* on the computer (that are not file creation or search, e.g., 'open YouTube in browser', 'create a folder named notes', 'write a note about groceries'), **YOU MUST GENERATE PYTHON CODE** to perform that action. Python is the default language for action commands.  \n" +
      "**Ensure that the generated Python code includes comprehensive and detailed logging using print() statements to track each step of the action, including start, end, success, and errors. This logging is essential for verifying the correct execution of the action.**\n" + // Added stronger logging instruction
      "For action requests, assume the user wants to EXECUTE a command, and therefore you MUST GENERATE PYTHON CODE to perform the requested action.\n\n" + // Re-emphasized Python code generation
      "User Request: " + userRequest;

  if (source === "terminal") {
    console.log("Sending your request to the AI...");
  } else {
      if (bot) {
          try { bot.sendMessage(telegramChatId, "Processing your request..."); } catch (e) { console.error("Telegram Send Error:", e.message); }
      }
  }

  let responseJson = null;
  while (!responseJson) {
    if (!isInternetConnected()) {
      console.log("No internet connection, waiting for connection...");
      if (source === "telegram" && telegramChatId && bot) {
          try { bot.sendMessage(telegramChatId, "No internet connection, waiting for connection..."); } catch (e) { console.error("Telegram Send Error:", e.message); }
      }
      await new Promise(resolve => setTimeout(resolve, 15000)); // Wait 15 seconds
      continue;
    }

    responseJson = await sendRequestToAI(prompt);

    if (!responseJson) {
      const errMsg = "Failed to receive a response from the AI. Retrying...";
      console.error(errMsg);
      if (source === "terminal") {
        console.log(errMsg);
      } else {
          if (bot) {
              try { bot.sendMessage(telegramChatId, errMsg); } catch (e) { console.error("Telegram Send Error:", e.message); }
          }
      }
      await new Promise(resolve => setTimeout(resolve, 15000)); // Wait before retrying
    }
  }


  const { text: aiText, type } = processAIResponse(responseJson);
  if (!aiText) {
    const errMsg = "Received an invalid response from the AI.";
    console.error(errMsg);
    if (source === "terminal") {
      console.log(errMsg);
    } else {
        if (bot) {
            try { bot.sendMessage(telegramChatId, errMsg); } catch (e) { console.error("Telegram Send Error:", e.message); }
        }
    }
    return;
  }

  // If the AI response is a file search command (JSON), process it accordingly.
if (type === "message") {
    try {
        const parsedResponse = JSON.parse(aiText);
        if (parsedResponse.is_search_file === true) {
            const folder = parsedResponse.folder || "Desktop";
            const searchResults = await handleFileSearch(parsedResponse.file_name, folder, source, telegramChatId);

            // אם נמצא קובץ מדויק, שלח אותו
            if (searchResults && searchResults.exact_match) {
                await bot.sendDocument(telegramChatId, searchResults.exact_match);
                return;
            }

            // אם אין התאמה מדויקת, הצג רשימת קבצים דומים
            if (searchResults && searchResults.similar_files) {
                const paginatedButtons = searchResults.similar_files.slice(0, 8).map((file, index) => [{
                    text: `${path.basename(file.path)} (${file.score.toFixed(0)}%)`,
                    callback_data: `choose_file_${index}`
                }]);
            }
            return;
        }

    // NEW ELSE IF BLOCK for reusing file:
    else if (parsedResponse.reuse_file === true) {
      const reusedFilename = parsedResponse.filename;
      if (!reusedFilename) {
        const errMsg = "Invalid reuse_file response: Filename missing.";
        console.error(errMsg);
        if (source === "terminal") {
          console.log(errMsg);
        } else if (bot) {
          try {
            bot.sendMessage(telegramChatId, errMsg);
          } catch (e) {
            console.error("Telegram Send Error:", e.message);
          }
        }
        return;
      }
      const filePath = path.join(BASE_CODES_FOLDER, 'Python', reusedFilename); // Construct file path
      if (!fs.existsSync(filePath)) {
        const errMsg = `Reused file not found: ${filePath}`;
        console.error(errMsg);
        if (source === "terminal") {
          console.log(errMsg);
        } else if (bot) {
          try {
            bot.sendMessage(telegramChatId, errMsg);
          } catch (e) {
            console.error("Telegram Send Error:", e.message);
          }
        }
        return;
      }

      const replyMsg = "Reusing existing Python file: " + path.basename(filePath);
      if (source === "terminal") {
        console.log(replyMsg);
      } else if (bot) {
        try {
          bot.sendMessage(telegramChatId, replyMsg);
        } catch (e) {
          console.error("Telegram Send Error:", e.message);
        }
      }

      const result = await runCode(filePath); // Execute the reused code

      // Trigger fix loop if needed
      if (result.code !== 0 || result.actionSuccess !== true) {
        console.log("Reused code execution failed or action was not successful. Entering fix loop.");
        const fixResult = await fixCodeLoop(fs.readFileSync(filePath, 'utf8'), filePath, source, telegramChatId, userRequest);
        const finalFilePath = fixResult.filePath;
        const finalResult = fixResult.result;

        if (fixResult.success) {
          let successMsg = "Command executed successfully after fix (reused file).";
          if (source === "terminal") {
            console.log(successMsg);
          } else if (bot) {
            try {
              bot.sendMessage(telegramChatId, successMsg);
            } catch (e) {
              console.error("Telegram Send Error:", e.message);
            }
          }
        } else {
          const finalErrMsg = `Final attempt failed to fix reused command. Please try again later.`;
          console.error(finalErrMsg);
          if (source === "terminal") {
            console.log(finalErrMsg);
            await explainError(finalResult.stderr, source, telegramChatId);
          } else if (source === "telegram" && telegramChatId && bot) {
            bot.sendMessage(telegramChatId, finalErrMsg);
            await explainError(finalResult.stderr, source, telegramChatId);
          }
        }
      } else { // Success
        let successMsg = "Command executed successfully (reused file).";
        if (source === "terminal") {
          console.log(successMsg);
        } else if (bot) {
          try {
            bot.sendMessage(telegramChatId, successMsg);
          } catch (e) {
            console.error("Telegram Send Error:", e.message);
          }
        }
      }
      return; // Exit processRequest after reusing file
    }
  } catch (e) {
    // Not a JSON file search command; continue below
  }
  // If not JSON, output as regular AI message:
  if (source === "terminal") {
    console.log("AI Response:");
    console.log(aiText);
  } else if (bot) {
    try {
      bot.sendMessage(telegramChatId, aiText);
    } catch (e) {
      console.error("Telegram Send Error:", e.message);
    }
  }
  return;
}
  if (type === "code") {
    // Determine file type from header - now extension should be in the filename
    let filename = extractFilename(aiText);
    let ext = path.extname(filename).toLowerCase() || '.txt'; // Default to .txt if no extension found
    let commandType = "unknown";

    if (ext === ".py") commandType = "python";
    else if (ext === ".txt") commandType = "text";
    else if (ext === ".html") commandType = "html";
    else if (ext === ".js") commandType = "javascript";
    else if (ext === ".css") commandType = "css";
    else if (ext === ".json") commandType = "json";
    else if (ext === ".xml") commandType = "xml";
    else if (ext === ".java") commandType = "java";
    else if (ext === ".c") commandType = "c";
    else if (ext === ".cpp") commandType = "cpp";
    else if (ext === ".cs") commandType = "csharp";
    else if (ext === ".php") commandType = "php";
    else if (ext === ".rb") commandType = "ruby";
    else if (ext === ".swift") commandType = "swift";
    else if (ext === ".go") commandType = "go";
    else if (ext === ".sh") commandType = "shell";
    else if (ext === ".bat") commandType = "batch";
    else commandType = "other";


    const fileTypeMsg = (commandType === "python")
      ? "executed"
      : "created";

    if (source === "terminal") {
      console.log(`AI generated a ${commandType} file action. Saving file...`);
    }

    const filePath = generateCodeFilePath(aiText); // Filename now includes extension
    const savedFilePath = saveCodeToFile(aiText, filePath);
    if (!savedFilePath) {
      const errMsg = "Error: Could not save the generated code.";
      console.error(errMsg);
      if (source === "terminal") {
        console.log(errMsg);
      } else {
          if (bot) {
              try { bot.sendMessage(telegramChatId, "Error: Could not save the generated code."); } catch (e) { console.error("Telegram Send Error:", e.message); }
          }
      }
      return;
    }

    // Cache the command
    previousCommands[normalizedRequest] = { filePath: savedFilePath, type: commandType };

    if (commandType === "python") { // Only run Python files for now
        const fixResult = await fixCodeLoop(aiText, savedFilePath, source, telegramChatId, userRequest); // Pass userRequest
        const finalFilePath = fixResult.filePath;
        const result = fixResult.result;

        if (fixResult.success) {
            const successMsg = path.basename(finalFilePath) + " " + fileTypeMsg + " successfully.";
            if (source === "terminal") {
                console.log(successMsg);
            } else {
                if (bot) {
                    try { bot.sendMessage(telegramChatId, successMsg); } catch (e) { console.error("Telegram Send Error:", e.message); }
                }
            }
        } else {
            const finalErrMsg = `Final attempt failed after multiple retries. Please try again later.`;
            console.error(finalErrMsg);
            if (source === "terminal") {
                console.log(finalErrMsg);
                await explainError(result.stderr, source, telegramChatId); // Explain error on final failure
            } else {
                if (bot) {
                    try { bot.sendMessage(telegramChatId, finalErrMsg); } catch (e) { console.error("Telegram Send Error:", e.message); }
                }
                 await explainError(result.stderr, source, telegramChatId); // Explain error on final failure
            }
        }
    } else { // For non-python files, just report creation success
        const successMsg = path.basename(savedFilePath) + " " + fileTypeMsg + " successfully.";
        if (source === "terminal") {
            console.log(successMsg);
        } else {
            if (bot) {
                try { bot.sendMessage(telegramChatId, successMsg); } catch (e) { console.error("Telegram Send Error:", e.message); }
            }
        }
    }


  } else {
    // Regular AI message
    if (source === "terminal") {
      console.log("AI Response:");
      console.log(aiText);
    } else {
        if (bot) {
            try { bot.sendMessage(telegramChatId, aiText); } catch (e) { console.error("Telegram Send Error:", e.message); }
        }
    }
  }
}

// ================================
// Voice message handler using Cloudflare Whisper ASR model with conversion and conversation response
// ================================
bot.on("voice", async (msg) => {
  const chatId = msg.chat.id;

  if (processingChats[chatId]) return;
  processingChats[chatId] = true;

  try {
    console.log(`Voice message received from chat ${chatId}`);

    // Display typing animation
    await bot.sendChatAction(chatId, 'typing');

    // Step 1: Get file details from Telegram
    const fileId = msg.voice.file_id;
    const file = await bot.getFile(fileId);
    const fileUrl = `https://api.telegram.org/file/bot${TELEGRAM_BOT_TOKEN}/${file.file_path}`;
    console.log("File URL:", fileUrl);

    // Step 2: Download the file in OGG format
    const oggResponse = await axios.get(fileUrl, { responseType: 'arraybuffer' });
    const oggFilePath = `temp_voice_${chatId}.ogg`;
    const wavFilePath = `temp_voice_${chatId}.wav`;
    fs.writeFileSync(oggFilePath, oggResponse.data);
    console.log("OGG file saved.");

    // Step 3: Convert the file from OGG to WAV using ffmpeg
    const ffmpegPath = "C:\\Users\\hillel1\\Downloads\\ffmpeg-master-latest-win64-gpl-shared\\ffmpeg-master-latest-win64-gpl-shared\\bin\\ffmpeg.exe";
    await new Promise((resolve, reject) => {
      const ffmpegProcess = spawn(ffmpegPath, ['-y', '-i', oggFilePath, '-ar', '16000', '-ac', '1', wavFilePath]);
      ffmpegProcess.stdout.on('data', (data) => {
        console.log(`ffmpeg stdout: ${data}`);
      });
      ffmpegProcess.stderr.on('data', (data) => {
        console.error(`ffmpeg stderr: ${data}`);
      });
      ffmpegProcess.on('close', (code) => {
        if (code === 0) {
          console.log("ffmpeg conversion completed successfully.");
          resolve();
        } else {
          reject(new Error(`ffmpeg exited with code ${code}`));
        }
      });
    });

    // Continue typing animation
    await bot.sendChatAction(chatId, 'typing');

    // Step 4: Read the WAV file and convert it to Base64
    const wavData = fs.readFileSync(wavFilePath);
    const audioBase64 = wavData.toString('base64');
    // Cleanup temporary files
    fs.unlinkSync(oggFilePath);
    fs.unlinkSync(wavFilePath);

    // Step 5: Transcribe audio using Cloudflare Whisper
    console.log("Sending transcription request...");
    const transcriptionText = await transcribeAudio(audioBase64);
    console.log("Transcription result:", transcriptionText);
    if (!transcriptionText) {
      throw new Error("No transcription available.");
    }

    // Step 6: Process the transcription text as a normal request.
    await processRequest(transcriptionText, "telegram", chatId, msg.from.username);
  } catch (error) {
    console.error("Error processing voice message:", error);
    bot.sendMessage(msg.chat.id, `Error: ${error.message}`, { reply_to_message_id: msg.message_id });
  } finally {
    processingChats[msg.chat.id] = false;
  }
});

function mergeFileSizes(filteredFiles, originalFiles) {
  // נניח ש-originalFiles הוא המערך המקורי שמכיל גם את size
  return filteredFiles.map(file => {
    // חיפוש לפי נתיב
    const original = originalFiles.find(orig => orig.path === file.path);
    if (original && original.size) {
      file.size = original.size;
    }
    return file;
  });
}



// ================================
// Input Handlers (No changes needed below this point for this feature)
// ================================

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});
rl.on("line", async (input) => {
  await processRequest(input, "terminal");
});

// Telegram bot message handler
if (bot) { // Only set up Telegram message handler if bot was initialized successfully
    bot.on("message", async (msg) => {
      const username = msg.from.username;
      const chatId = msg.chat.id;
      if (!username || username !== "HILLEL6767") {
          try { bot.sendMessage(chatId, "You are not authorized to use this bot."); } catch (e) { console.error("Telegram Send Error:", e.message); }
        return;
      }
      if (msg.text) {
        await processRequest(msg.text, "telegram", chatId, username);
      }
    });
} else {
    console.log("Telegram bot is not initialized. Telegram input will be disabled.");
}


    """

    # Replace placeholders with user inputs
    configured_code = ai_js_code.replace("GEMINI-API", gemini_api_key)
    configured_code = configured_code.replace("telegram_bot_token", telegram_bot_token)
    configured_code = configured_code.replace("cloudflare_account_id", cloudflare_account_id)
    configured_code = configured_code.replace("cloudflare_api_token", cloudflare_api_token)
    configured_code = configured_code.replace('BASE_CODES_FOLDER = "C:\\\\Users\\\\hillel1\\\\Desktop\\\\AI\\\\codes"', f'BASE_CODES_FOLDER = "C:\\\\Users\\\\{username}\\\\Desktop\\\\AI\\\\codes"')
    configured_code = configured_code.replace('BASE_BACKUPS_FOLDER = "C:\\\\Users\\\\hillel1\\\\Desktop\\\\AI\\\\backups"', f'BASE_BACKUPS_FOLDER = "C:\\\\Users\\\\{username}\\\\Desktop\\\\AI\\\\backups"')
    configured_code = configured_code.replace('const ffmpegPath = "C:\\\\Users\\\\hillel1\\\\Downloads\\\\ffmpeg-master-latest-win64-gpl-shared\\\\ffmpeg-master-latest-win64-gpl-shared\\\\bin\\\\ffmpeg.exe";', f'const ffmpegPath = "C:\\\\Users\\\\{username}\\\\Downloads\\\\ffmpeg-master-latest-win64-gpl-shared\\\\ffmpeg-master-latest-win64-gpl-shared\\\\bin\\\\ffmpeg.exe";')
    configured_code = configured_code.replace('path.join("C:\\\\Users\\\\hillel1", "Desktop")', f'path.join("C:\\\\Users\\\\{username}", "Desktop")')
    configured_code = configured_code.replace('const userDir = path.join("C:\\\\Users\\\\hillel1");', f'const userDir = path.join("C:\\\\Users\\\\{username}");')
    configured_code = configured_code.replace('path.join("C:\\\\Users\\\\hillel1", "Desktop")', f'path.join("C:\\\\Users\\\\{username}", "Desktop")')
    configured_code = configured_code.replace('path.join("C:\\\\Users\\\\hillel1", "Documents")', f'path.join("C:\\\\Users\\\\{username}", "Documents")')
    configured_code = configured_code.replace('path.join("C:\\\\Users\\\\hillel1", "Downloads")', f'path.join("C:\\\\Users\\\\{username}", "Downloads")')
    configured_code = configured_code.replace('path.join("C:\\\\Users\\\\hillel1", "Music")', f'path.join("C:\\\\Users\\\\{username}", "Music")')
    configured_code = configured_code.replace('path.join("C:\\\\Users\\\\hillel1", "Pictures")', f'path.join("C:\\\\Users\\\\{username}", "Pictures")')
    configured_code = configured_code.replace('path.join("C:\\\\Users\\\\hillel1", "Videos")', f'path.join("C:\\\\Users\\\\{username}", "Videos")')
    configured_code = configured_code.replace('"HILLEL6767"', f'"{telegram_username}"') # Replace Telegram username

    # Define output directory in Desktop\AI
    output_directory = os.path.join(os.path.expanduser("~"), "Desktop", "AI")
    output_file_path = os.path.join(output_directory, "configured_ai.js")

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Save the configured code to the new directory
    try:
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(configured_code)
        print(f"\nConfiguration for ai.js complete!")
        print(f"The configured ai.js file has been saved to: {output_file_path}")
    except Exception as e:
        print(f"Error saving the configured ai.js file: {e}")

    # Define output directory in Desktop\AI - same as configured_ai.js
    output_directory = os.path.join(os.path.expanduser("~"), "Desktop", "AI")

    # Python script for search_file.py
    search_file_py_code = """import sys
import os
import json
from fuzzywuzzy import fuzz

# Ensure stdout uses UTF-8 encoding (Python 3.7+)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

def get_desktop_path():
    home = os.path.expanduser("~")
    return os.path.join(home, "Desktop")

def search_file(file_fragment, folder):
    exact_matches = []
    all_files_in_folder = []

    for root, dirs, files in os.walk(folder):
        for file in files:
            file_path = os.path.join(root, file)
            all_files_in_folder.append((file, file_path)) # Store file name and path
            if file_fragment.lower() in file.lower():
                exact_matches.append(file_path)

    if exact_matches:
        return {"exact_match": exact_matches[0]} # Return the first exact match found

    # If no exact match, search for similar file names
    similar_files = []
    for file_name, file_path in all_files_in_folder:
        similarity_score = fuzz.partial_ratio(file_fragment.lower(), file_name.lower())
        if similarity_score > 60: # Adjust threshold as needed (0-100, higher means more strict)
            similar_files.append({"path": file_path, "score": similarity_score, "name": file_name})

    if similar_files:
        similar_files.sort(key=lambda x: x["score"], reverse=True) # Sort by similarity score
        return {"similar_files": similar_files} # Return list of similar files

    return {"no_match": True} # Indicate no match found at all


def main():
    if len(sys.argv) < 2:
        print("Usage: python search_file.py <file_name_fragment> [folder]")
        sys.exit(1)
    file_fragment = sys.argv[1]
    folder = sys.argv[2] if len(sys.argv) >= 3 else get_desktop_path()
    folder = os.path.abspath(folder)  # Convert to absolute path

    if not os.path.exists(folder):
        print(json.dumps({"error": f"Folder '{folder}' does not exist."})) # Output error as JSON
        sys.exit(1)

    results = search_file(file_fragment, folder)

    print(json.dumps(results, ensure_ascii=False)) # Output results as JSON


if __name__ == "__main__":
    main()
"""

    # Define the full path for search_file.py in the output directory
    search_file_path = os.path.join(output_directory, "search_file.py") # Changed here

    # Create the output directory if it doesn't exist (already done for configured_ai.js, but safe to keep)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    try:
        with open(search_file_path, "w", encoding="utf-8") as f: # Changed here
            f.write(search_file_py_code)
        print(f"\nPython script search_file.py created successfully!")
        print(f"It has been saved to: {os.path.abspath(search_file_path)}")
    except Exception as e:
        print(f"Error saving search_file.py: {e}")


if __name__ == "__main__":
    configure_ai_script()