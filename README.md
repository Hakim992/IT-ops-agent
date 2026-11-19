# IT Ops Agent

A simple AI agent that helps with everyday IT checks through chat. Ask in plain language (English or Malay) and the agent decides which tools to run: checking disk space, pinging hosts, listing files and reading log files.

Built from scratch without an agent framework, to show how the agent loop works: **LLM + tools + loop**.

## Features

- **Tool calling**: the LLM decides on its own when to call a tool and which one
- **6 built-in tools**:
  | Tool | What it does |
  |---|---|
  | `get_time` | Current date and time |
  | `list_files` | List files in a folder |
  | `list_drives` | List all drives on the machine |
  | `check_disk` | Disk usage for a drive |
  | `ping_host` | Check network connectivity to a host/IP |
  | `read_file` | Read a text or log file |
- **Error handling**: tool and API errors are passed back to the AI instead of crashing the program
- **Basic safety**: tools are read-only, and host input is validated before running `ping`

## How it works

```
User question
     │
     ▼
   LLM  ──── needs data? ──► calls a tool (runs locally) ──┐
     ▲                                                     │
     └──────────────── tool result ◄───────────────────────┘
     │
     ▼
Final answer
```

The agent code and tools run locally. The LLM (Google Gemini) is called through its OpenAI-compatible API.

## Example

```
Kau: storage laptop aku tinggal berapa?
  [tool] list_drives({}) -> C:
  [tool] check_disk({'drive': 'C:'}) -> C:\ Total 251.2GB, guna 213.8GB, baki 37.4GB (85% penuh)
AI: Drive C: tinggal 37.4GB (85% penuh).
```

## Setup

**Requirements:** Python 3.10+, a free Gemini API key from [Google AI Studio](https://aistudio.google.com)

```bash
git clone https://github.com/Hakim992/it-ops-agent.git
cd it-ops-agent

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

pip install openai python-dotenv
```

Create a `.env` file in the project folder:

```
GEMINI_API_KEY=your_key_here
```

Run:

```bash
python agent.py
```

Type `keluar` or `exit` to quit.

## Tech stack

- Python
- Google Gemini (via the OpenAI Python SDK)
- python-dotenv

## Roadmap

- [ ] Web chat UI with Streamlit
- [ ] Fully local mode with Ollama (no data leaves the machine)
- [ ] More tools: CPU/RAM usage, running processes, log error analysis