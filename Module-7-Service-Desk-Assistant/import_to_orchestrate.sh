#!/bin/bash

# ============================================================
# Import Tools, Connections, and Agents to Watsonx Orchestrate
# ============================================================
# Prerequisites:
# 1. Install CLI: pip install ibm-watsonx-orchestrate
# 2. Set environment variables in .env file
# 3. Run from project root: bash import_to_orchestrate.sh
# ============================================================

set -e  # Exit on error

echo ""
echo "============================================================"
echo "WATSONX ORCHESTRATE - IMPORT TOOLS & AGENTS"
echo "============================================================"
echo ""

# Load environment variables
if [ -f .env ]; then
    echo "→ Loading environment variables from .env..."
    set -a
    source .env
    set +a
    echo "   ✅ Environment variables loaded"
else
    echo "❌ Error: .env file not found!"
    exit 1
fi

# Check required environment variables
echo ""
echo "→ Checking required environment variables..."
REQUIRED_VARS=(
    "WATSONX_ORCHESTRATE_URL"
    "WXO_APIKEY"
    "ES_HOST"
    "ES_USERNAME"
    "ES_PASSWORD"
    "WATSONX_URL"
    "WATSONX_APIKEY"
    "WATSONX_PROJECT_ID"
    "SNOW_INSTANCE_URL"
    "SNOW_USERNAME"
    "SNOW_PASSWORD"
    "GITHUB_TOKEN"
    "GITHUB_REPO_OWNER"
    "GITHUB_REPO_NAME"
)

MISSING_VARS=()
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo "❌ Error: Missing required environment variables:"
    for var in "${MISSING_VARS[@]}"; do
        echo "   - $var"
    done
    exit 1
fi
echo "   ✅ All required variables are set"

# Check orchestrate CLI
echo ""
echo "→ Checking orchestrate CLI installation..."
if ! command -v orchestrate &> /dev/null; then
    echo "❌ Error: orchestrate CLI not found!"
    echo "   Install it with: pip install ibm-watsonx-orchestrate"
    exit 1
fi
echo "   ✅ orchestrate CLI is installed"

# ============================================================
echo ""
echo "============================================================"
echo "STEP 1: Configure Watsonx Orchestrate Environment"
echo "============================================================"
echo ""

ENV_NAME="servicedesk_assistant"

echo "→ Adding environment: $ENV_NAME..."
orchestrate env add \
    --name "$ENV_NAME" \
    --url "$WATSONX_ORCHESTRATE_URL" \
    --type ibm_iam \
    --activate || {
        echo "⚠️  Environment may already exist, trying to activate..."
    }

echo ""
echo "→ Activating environment with API key..."
orchestrate env activate "$ENV_NAME" --api-key "$WXO_APIKEY"
echo "   ✅ Environment activated"

echo ""
echo "→ Verifying connection..."
orchestrate tools list > /dev/null 2>&1 && echo "   ✅ Connection successful" || {
    echo "❌ Error: Could not connect to Watsonx Orchestrate"
    exit 1
}

# ============================================================
echo ""
echo "============================================================"
echo "STEP 2: Import Connections and Set Credentials"
echo "============================================================"
echo ""

# Elasticsearch connection
echo "→ Importing Elasticsearch connection..."
orchestrate connections import -f connections/elasticsearch-service-desk.yaml && \
    echo "   ✅ Connection definition imported" || \
    echo "   ⚠️  Connection may already exist, continuing..."

echo "   → Setting Elasticsearch credentials..."
for env in draft live; do
    orchestrate connections set-credentials -a elasticsearch-service-desk \
        --env "$env" \
        -e "ES_HOST=${ES_HOST}" \
        -e "ES_PORT=${ES_PORT:-9200}" \
        -e "ES_USERNAME=${ES_USERNAME}" \
        -e "ES_PASSWORD=${ES_PASSWORD}" \
        -e "ES_USE_SSL=${ES_USE_SSL:-true}" \
        -e "ES_VERIFY_CERTS=${ES_VERIFY_CERTS:-false}" \
        -e "ES_CERT_CONTENT=${ES_CERT_CONTENT:-}"
    echo "   ✅ Elasticsearch credentials set ($env)"
done

echo ""
# ServiceNow connection
echo "→ Importing ServiceNow connection..."
orchestrate connections import -f connections/servicenow-service-desk.yaml && \
    echo "   ✅ Connection definition imported" || \
    echo "   ⚠️  Connection may already exist, continuing..."

echo "   → Setting ServiceNow credentials..."
for env in draft live; do
    orchestrate connections set-credentials -a servicenow-service-desk \
        --env "$env" \
        -e "SNOW_INSTANCE_URL=${SNOW_INSTANCE_URL}" \
        -e "SNOW_USERNAME=${SNOW_USERNAME}" \
        -e "SNOW_PASSWORD=${SNOW_PASSWORD}"
    echo "   ✅ ServiceNow credentials set ($env)"
done

echo ""
# GitHub connection
echo "→ Importing GitHub connection..."
orchestrate connections import -f connections/github-service-desk.yaml && \
    echo "   ✅ Connection definition imported" || \
    echo "   ⚠️  Connection may already exist, continuing..."

echo "   → Setting GitHub credentials..."
for env in draft live; do
    orchestrate connections set-credentials -a github-service-desk \
        --env "$env" \
        -e "GITHUB_TOKEN=${GITHUB_TOKEN}" \
        -e "GITHUB_REPO_OWNER=${GITHUB_REPO_OWNER}" \
        -e "GITHUB_REPO_NAME=${GITHUB_REPO_NAME}"
    echo "   ✅ GitHub credentials set ($env)"
done

echo ""
# WatsonX AI connection
echo "→ Importing WatsonX AI connection..."
orchestrate connections import -f connections/watsonx-ai-service-desk.yaml && \
    echo "   ✅ Connection definition imported" || \
    echo "   ⚠️  Connection may already exist, continuing..."

echo "   → Setting WatsonX AI credentials..."
for env in draft live; do
    orchestrate connections set-credentials -a watsonx-ai-service-desk \
        --env "$env" \
        -e "WATSONX_URL=${WATSONX_URL}" \
        -e "WATSONX_APIKEY=${WATSONX_APIKEY}" \
        -e "WATSONX_PROJECT_ID=${WATSONX_PROJECT_ID}"
    echo "   ✅ WatsonX AI credentials set ($env)"
done

# ============================================================
echo ""
echo "============================================================"
echo "STEP 3: Import Tools"
echo "============================================================"
echo ""

export PYTHONPATH="${PWD}:${PYTHONPATH}"

echo "→ Importing Risk tools..."
if [ -f "agents/risk_tools.py" ]; then
    orchestrate tools import \
        -k python \
        -f "agents/risk_tools.py" \
        -r "requirements_tools.txt" \
        -a elasticsearch-service-desk \
        -a watsonx-ai-service-desk && \
        echo "   ✅ Risk tools imported successfully" || \
        echo "   ⚠️  Risk tools import failed"
else
    echo "   ⚠️  risk_tools.py not found"
fi

echo ""
echo "→ Importing ServiceNow tools..."
if [ -f "agents/servicenow_tools.py" ]; then
    orchestrate tools import \
        -k python \
        -f "agents/servicenow_tools.py" \
        -r "requirements_tools.txt" \
        -a servicenow-service-desk && \
        echo "   ✅ ServiceNow tools imported successfully" || \
        echo "   ⚠️  ServiceNow tools import failed"
else
    echo "   ⚠️  servicenow_tools.py not found"
fi

echo ""
echo "→ Importing GitHub investigation tools..."
if [ -f "agents/investigation_tools.py" ]; then
    orchestrate tools import \
        -k python \
        -f "agents/investigation_tools.py" \
        -r "requirements_tools.txt" \
        -a github-service-desk && \
        echo "   ✅ GitHub investigation tools imported successfully" || \
        echo "   ⚠️  GitHub investigation tools import failed"
else
    echo "   ⚠️  investigation_tools.py not found"
fi

echo ""
echo "→ Listing imported tools..."
orchestrate tools list

# ============================================================
echo ""
echo "============================================================"
echo "STEP 4: Import Agents"
echo "============================================================"
echo ""

echo "→ Importing incident_logging_agent..."
if [ -f "agents/incident_logging_agent.yml" ]; then
    orchestrate agents import -f "agents/incident_logging_agent.yml" && \
        echo "   ✅ incident_logging_agent imported" || \
        echo "   ⚠️  incident_logging_agent import failed (may already exist)"
else
    echo "   ⚠️  incident_logging_agent.yml not found"
fi

echo ""
echo "→ Importing risk_mapping_agent..."
if [ -f "agents/risk_mapping_agent.yml" ]; then
    orchestrate agents import -f "agents/risk_mapping_agent.yml" && \
        echo "   ✅ risk_mapping_agent imported" || \
        echo "   ⚠️  risk_mapping_agent import failed (may already exist)"
else
    echo "   ⚠️  risk_mapping_agent.yml not found"
fi

echo ""
echo "→ Importing root_cause_agent..."
if [ -f "agents/root_cause_agent.yml" ]; then
    orchestrate agents import -f "agents/root_cause_agent.yml" && \
        echo "   ✅ root_cause_agent imported" || \
        echo "   ⚠️  root_cause_agent import failed (may already exist)"
else
    echo "   ⚠️  root_cause_agent.yml not found"
fi

echo ""
echo "→ Importing service_desk_assistant (main orchestrator)..."
if [ -f "agents/service_desk_assistant.yml" ]; then
    orchestrate agents import -f "agents/service_desk_assistant.yml" && \
        echo "   ✅ service_desk_assistant imported" || \
        echo "   ⚠️  service_desk_assistant import failed (may already exist)"
else
    echo "   ⚠️  service_desk_assistant.yml not found"
fi

echo ""
echo "→ Listing imported agents..."
orchestrate agents list

# ============================================================
echo ""
echo "============================================================"
echo "IMPORT COMPLETE!"
echo "============================================================"
echo ""
echo "✅ Environment:  $ENV_NAME"
echo "✅ Connections:  elasticsearch-service-desk, watsonx-ai-service-desk, servicenow-service-desk, github-service-desk"
echo "✅ Tools:        risk_tools, servicenow_tools, investigation_tools"
echo "✅ Agents:       incident_logging_agent, risk_mapping_agent, root_cause_agent, service_desk_assistant"
echo ""
echo "Next: open Watsonx Orchestrate UI and say:"
echo "   'Investigate the root cause of incident INC0010001'"
echo "============================================================"

# Made with Bob
