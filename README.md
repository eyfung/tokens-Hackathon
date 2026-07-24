# 🧪 Clarity — Self-Evolving Clinical Trial Design Agent

> *Built for the **tokens& Self-Evolving Agents Hackathon** (powered by DeepMind, Guild AI, Pioneer, Band, Actian, Replay)*

## The Problem

Clinical trial design is a **$50–100M bet** guided by months of manual simulation work from scarce biostatisticians. Get the sample size, eligibility criteria, or endpoint wrong and your trial fails — wasting years and hundreds of millions.

Small biotechs can't afford full-time biostatisticians. Big pharma burns weeks per iteration. Everyone agrees the process is broken.

## Our Solution

**Clarity** is a self-evolving agent that compresses clinical trial feasibility analysis from weeks to minutes:

1. **Simulate** — Runs thousands of virtual patient trials in seconds
2. **Learn** — Stores every design + outcome in a vector database (Actian)
3. **Evolve** — Gets better at predicting trial success with every iteration
4. **Collaborate** — Pulls humans in via Band when a design looks risky

## Built With

| Partner | Role |
|---|---|
| **DeepMind** (Gemini) | Complex reasoning for unusual trial designs |
| **Pioneer** | Cost-effective inference for routine simulations |
| **Actian** | Vector DB — stores trial design patterns for similarity search |
| **Band** | Human-in-the-loop escalation rooms |
| **Guild AI** | Agent lifecycle management & versioning |
| **Replay** | QA capture & replay of the demo flow |

## Project Structure

```
src/
├── simulation/      # Statistical trial simulation engine
├── agent/           # Core agent workflow & prompts
├── memory/          # Actian vector DB integration
├── communication/   # Band AI human escalation
└── inference/       # Pioneer & DeepMind API wrappers
web/                 # Streamlit demo UI
config/              # Partner API configuration
tests/               # Unit tests
guild/               # Guild AI agent definition
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the web demo
streamlit run web/app.py
```

## Team

[Clarity] — [tokens& Hackathon 2026]
