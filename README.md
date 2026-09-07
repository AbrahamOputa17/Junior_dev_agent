# Junior Dev Agent 🤖⚡

> An autonomous, secure AI Software Engineer workstation that operates safely within code repositories using Code RAG, sandboxed command execution, 2-phase authorization guardrails, and automated self-verification loops.

---

## ⚡ Key Features

- 🛡️ **2-Phase Security & HMAC Authorization**: Operates in read-only mode during investigation; requires signed authorization before executing code changes.
- 🔒 **Sandboxed Subprocess Execution**: Strict argument-vector command execution (`shell=False`) with canonical path resolution to defeat injection and path traversal.
- 🕵️ **Secret Redaction Pipeline**: Automatically redacts API keys and credentials before prompt context reaches LLMs.
- 🧠 **Code RAG & AST Symbol Indexing**: Hybrid retrieval powered by AST symbol graphs, term-frequency scoring, and SHA256 incremental hash invalidation.
- ✅ **Self-Verification & Git Rollbacks**: Auto-detects test runners (`pytest`, `jest`, `cargo test`, `go test`) and linters with atomic Git stash rollbacks on verification failure.
- 💾 **Dynamic Memory & Run Persistence**: Dynamically discovers repository tech stacks and maintains persistent task run logs in `.junior_dev/runs/`.

---

## 🛠️ Tech Stack

- **Core Engine**: Python 3.13 | FastAPI | OpenAI GPT-4o
- **Security & Sandboxing**: Subprocess Isolation | HMAC Tokens | Regex Secret Scanner
- **Verification & Tooling**: Pytest | Git | Docker

---

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/AbrahamOputa17/Junior_dev_agent.git
cd Junior_dev_agent
python -m venv .venv
.venv\Scripts\activate  # On Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment Setup
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
JUNIOR_DEV_API_KEY=your_optional_bearer_token
```

### 3. Run Application Server
```bash
uvicorn app.api.server:app --reload
```

---

## 🧪 Running Tests

Run the full unit, security, and E2E integration test suite:
```bash
pytest
```
