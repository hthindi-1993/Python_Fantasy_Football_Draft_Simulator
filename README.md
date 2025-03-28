# Fantasy Football Draft Order Simulator

# 🏈 Python Fantasy Football Draft Simulator

A Python desktop application that brings drama and suspense to your fantasy football league’s draft order reveal. Featuring a sleek Tkinter GUI, countdown animations, intro music, and ElevenLabs AI-generated voice announcements for each pick.

---

## 🎯 Features

- 🖼️ User-friendly GUI built with Tkinter
- 🎤 Draft pick announcements using ElevenLabs AI
- 🔊 Intro music before each pick
- ⏳ Countdown animation between reveals
- 🧼 Auto-cleans generated audio each session
- ⚙️ Easy to customize and run with Python


## 🔧 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/hthindi-1993/Python_Fantasy_Football_Draft_Simulator.git


2. Install Dependencies
This project uses Poetry for dependency management.

poetry install

Environment Configuration
This app uses ElevenLabs for AI-generated voice announcements.

Create a .env file with your credentials:

ELEVEN_API_KEY=your_api_key_here
VOICE_ID=your_voice_id_here


Once dependencies are installed and .env is set up, launch the app with:

poetry run python draft_order.py


.
├── draft_order.py
├── .env.example
├── audio/
│   └── intro/
│       └── intro.mp3
├── pyproject.toml
└── README.md


Acknowledgments
ElevenLabs for lifelike voice synthesis
Poetry for clean dependency management
Python’s tkinter for GUI components

