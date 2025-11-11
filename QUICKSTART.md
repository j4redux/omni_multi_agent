# Quick Start (5 Minutes)

Get the Omni Multi-Agent System running in 5 minutes.

## Prerequisites

- Python 3.11+
- Anthropic API key
- OpenAI API key

## Setup

```bash
# 1. Clone and setup
git clone https://github.com/yourusername/omni_multi_agent.git
cd omni_multi_agent
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure API keys
export ANTHROPIC_API_KEY="sk-ant-your-key"
export OPENAI_API_KEY="sk-your-key"

# 3. Install and configure Letta
pip install letta
letta configure  # Follow prompts to enter API keys

# 4. Start Letta server (keep this terminal open)
letta server
```

## Create Agents (New Terminal)

```bash
# Activate venv in new terminal
cd omni_multi_agent
source venv/bin/activate

# Create agents in order
python orchestrator_agent/orchestrator_agent.py
# Copy the Agent ID from output

python tasks_agent/tasks_agent.py
python projects_agent/projects_agent.py  
python preferences_agent/preferences_agent.py
python conversational_agent/conversational_agent.py
```

## Update Agent IDs

**Important**: Update hardcoded agent IDs in the code (see [docs/SETUP.md](docs/SETUP.md#3-update-agent-id-references) for details).

## Test It

```bash
# Set your conversational agent ID
export CONVERSATIONAL_AGENT_ID="agent-abc123"

# Run examples
python examples/basic_usage.py
```

## Next Steps

- Read [README.md](README.md) for architecture overview
- See [docs/SETUP.md](docs/SETUP.md) for detailed setup
- Review [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for deep dive
- Try [examples/advanced_workflows.py](examples/advanced_workflows.py)

## Troubleshooting

**Connection refused**: Make sure `letta server` is running

**Agent not found**: Set correct `CONVERSATIONAL_AGENT_ID`

**Import errors**: Activate virtual environment

---

For complete documentation, see [docs/SETUP.md](docs/SETUP.md)
