# 🤖 AI Assistant

A personal AI assistant built with Python that connects to your Gmail and Google Calendar, 
helping you manage emails and daily schedule through natural language conversation.

## ✨ Features
- 📧 Read and summarize your Gmail emails
- 📅 Check today's Google Calendar events
- 🤖 AI-powered responses using Groq API & Ollama
- 💬 Talk to it naturally — no commands needed
- 🌐 Frontend interface to interact with the assistant

## 🛠️ Tech Stack
- **Python** — core language
- **Groq API** — fast AI responses using cloud LLMs
- **Ollama** — run AI models locally on your machine
- **Gmail API** — read and manage emails
- **Google Calendar API** — fetch your daily events

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/shubhansharma46-collab/ai-assistant.git
cd ai-assistant
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up your `.env` file
Create a `.env` file in the root folder and add:
```
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Set up Google APIs
- Enable **Gmail API** and **Google Calendar API** from [Google Cloud Console](https://console.cloud.google.com/)
- Download your `credentials.json` and place it in the project folder
- On first run, it will ask you to log in with Google

### 5. Install and run Ollama (for local AI)
- Download Ollama from [ollama.com](https://ollama.com)
- Pull a model: `ollama pull llama3`

### 6. Run the assistant
```bash
python main.py
```

## 📌 Important Notes
- Never share your `.env` or `user_credentials.json` files
- Groq API key is free to get at [console.groq.com](https://console.groq.com)
- Ollama lets you run AI completely offline and privately

## 🙋 Made By
Shubhan Sharma — built as a personal productivity AI assistant(HACKETHON PROJECT)
