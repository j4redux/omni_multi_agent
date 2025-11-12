#!/bin/bash

# Export agent IDs from config to environment variables

CONFIG_FILE="/app/config/agent_ids.json"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Config file not found: $CONFIG_FILE"
    exit 1
fi

# Parse JSON and export variables
export ORCHESTRATOR_AGENT_ID=$(jq -r '.orchestrator' "$CONFIG_FILE")
export TASKS_AGENT_ID=$(jq -r '.tasks' "$CONFIG_FILE")
export PROJECTS_AGENT_ID=$(jq -r '.projects' "$CONFIG_FILE")
export PREFERENCES_AGENT_ID=$(jq -r '.preferences' "$CONFIG_FILE")
export CONVERSATIONAL_AGENT_ID=$(jq -r '.conversational' "$CONFIG_FILE")

echo "✅ Agent IDs exported to environment"
echo "ORCHESTRATOR_AGENT_ID=$ORCHESTRATOR_AGENT_ID"
echo "CONVERSATIONAL_AGENT_ID=$CONVERSATIONAL_AGENT_ID"
