# 🚨 Disaster Rescue Coordination System

> An AI-powered real-time disaster rescue coordination platform built with **Solace Agent Mesh (SAM)** — an open-source framework for building event-driven multi-agent AI systems.

## 📖 Overview

The Disaster Rescue Coordination System is an event-driven multi-agent platform designed to optimize disaster response operations. By leveraging Solace Agent Mesh's asynchronous architecture, the system coordinates AI agents to handle victim communication, rescue team deployment, and resource allocation in real-time.

### 🎯 Key Capabilities

- **🗣️ Natural Language Victim Communication** - AI-powered chat interface for gathering critical incident details
- **📊 Intelligent Triage & Prioritization** - Automatic severity assessment and priority scoring
- **📦 Resource Management** - Automated inventory tracking and equipment allocation
- **🗺️ Live Situational Awareness** - Interactive maps with real-time victim and team locations
- **🔄 Event-Driven Architecture** - Guaranteed message delivery and loose coupling via Solace PubSub+

---

## Agent Responsibilities

### 🎯 Orchestrattion Agent
- Communicates with victims via natural language
- Extracts location, severity, headcount, and hazard information
- Assigns priority scores (CRITICAL/MODERATE/STABLE)
- Delegates rescue tasks to Deployment Agent and Severity Agent
  

### 🚑 Deployment Agent
- Receives victim assignments from Orchestrator
- Calculates required equipment based on scenario type
- Determines personnel requirements
- Provides GPS navigation and route optimization


---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Agent Framework** | Solace Agent Mesh | Multi-agent orchestration |
| **Agent Runtime** | Google ADK + Solace AI Connector | Agent execution environment |
| **Event Broker** | Solace PubSub+ | Message routing & delivery |
| **Frontend** | Next.js 14, React 18, TypeScript | Real-time UI |
| **Mapping** | Leaflet / Mapbox GL | Interactive geospatial visualization |
| **LLM** | OpenAI GPT-4 / Anthropic Claude | Natural language processing |
| **Containers** | Docker, AWS ECS Fargate | Serverless deployment |
| **IaC** | Terraform | Infrastructure automation |
| **CI/CD** | GitHub Actions | Automated pipelines |

---

### 2. Configure Environment

```bash
cd sam-project
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
# Solace Broker (local development)
SOLACE_BROKER_URL=tcp://localhost:55555
SOLACE_BROKER_VPN=default
SOLACE_BROKER_USERNAME=admin
SOLACE_BROKER_PASSWORD=admin

# LLM Configuration
SAM_LLM_PROVIDER=openai
SAM_LLM_MODEL=gpt-4
SAM_LLM_API_KEY=sk-your-openai-key

# Or use Anthropic Claude
# SAM_LLM_PROVIDER=anthropic
# SAM_LLM_MODEL=claude-sonnet-4-20250514
# SAM_LLM_API_KEY=sk-ant-your-key
```

### 3. Install Dependencies

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install solace-agent-mesh
```

## ☁️ AWS Deployment

Deploy to AWS ECS Fargate using Terraform:

```bash
cd terraform/environments/prod

# Initialize Terraform
terraform init

# Review changes
terraform plan

# Deploy infrastructure
terraform apply
```

## 🔄 CI/CD Pipeline

GitHub Actions automatically:

1. **Tests** - Runs unit tests on every PR
2. **Builds** - Creates Docker images for SAM and frontend
3. **Pushes** - Uploads images to AWS ECR
4. **Deploys** - Updates ECS services with new images

Trigger deployment:

```bash
git push origin main
```

---

## 🙏 Acknowledgments

- **Solace** for the Agent Mesh framework
- **OpenAI** for LLM capabilities
- **Google ADK** for agent runtime

---

**Built with ❤️ using Solace Agent Mesh**

*Making disaster response faster, smarter, and more coordinated.*
