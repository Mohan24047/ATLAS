<div align="center">

# 🌐 ATLAS: Local AI Voice Assistant

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20Mac-grey?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active%20Dev-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

### "Your personal Jarvis, running entirely on your hardware."

</div>

---

**ATLAS** is a fully offline, voice-controlled AI assistant optimized for privacy and low-latency performance on standard consumer CPUs. By bridging local Speech-to-Text (STT), a quantized LLM, and OS-level automation, ATLAS offers a coding and productivity companion that never sends your data to the cloud.

## ⚡ Key Features

| 🗣️ **Voice & Interaction** | 💻 **Coding Automation** |
| :--- | :--- |
| **Offline STT:** Powered by `faster-whisper` for real-time transcription. | **File Ops:** Create, read, and edit files via voice. |
| **Wake Word:** Always-listening activation ("Atlas"). | **Contextual Explainers:** Ask Atlas to explain code in your current buffer. |
| **Local TTS:** Snappy, offline text-to-speech feedback. | **Sandbox Mode:** Safe file operations restricted to project directories. |

| 🧠 **Memory & Logic** | ⚙️ **System Control** |
| :--- | :--- |
| **RAG-Lite:** Remembers user preferences and project context. | **App Launcher:** Open IDEs, browsers, or specific folders. |
| **Privacy First:** Explicit confirmation before storing personal data. | **Workflow Scripts:** Trigger complex "Start Coding" sequences. |
| **Task Management:** SQLite-backed TODOs and reminders. | **Resource Efficient:** Low CPU footprint when idle. |

---

## 🛠️ Tech Stack

* **Core:** Python 3.10+ (Threaded Architecture)
* **LLM Backend:** [Ollama](https://ollama.ai/) (Model agnostic, `qwen2.5:1.5b` or `llama3` recommended)
* **Speech-to-Text:** Faster-Whisper (Int8 quantization)
* **Text-to-Speech:** pyttsx3 (System native)
* **Database:** SQLite (Tasks & Long-term memory)

---

## 🚀 Getting Started

### Prerequisites
* Python 3.10+
* [Ollama](https://ollama.ai/) installed and running.
* A decent CPU (Runs comfortably on 8GB+ RAM).

### Installation

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/yourusername/atlas.git](https://github.com/yourusername/atlas.git)
    cd atlas
    ```

2.  **Set up the environment**
    ```bash
    python -m venv venv
    # Windows:
    .\venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Pull the LLM**
    ```bash
    ollama pull qwen2.5:1.5b
    # Or any model you prefer (edit config.py to change)
    ```

5.  **Run Atlas**
    ```bash
    python main.py
    ```

---

## 📂 Project Structure

```text
atlas/
├── 🧠 brain/           # LLM integration & decision logic
├── 🗣️ speech/          # STT (Whisper) and TTS handlers
├── 💾 memory/          # SQLite DB & Vector stores
├── 🛠️ tools/           # File ops, system automation scripts
├── 📝 config.py        # User settings (Models, Paths, Wake words)
└── main.py             # Entry point & event loop



