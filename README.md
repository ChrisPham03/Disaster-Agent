# 🚨 Disaster Rescue Coordination System

An AI-powered real-time disaster rescue coordination platform built with **Solace Agent Mesh (SAM)** — the open-source framework for building event-driven multi-agent AI systems.

![Architecture](docs/images/architecture-banner.png)

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Agent Configuration](#agent-configuration)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

The Disaster Rescue Coordination System leverages **Solace Agent Mesh** to orchestrate multiple AI agents that work together to:

- **Communicate with victims** and gather critical information
- **Prioritize rescue operations** based on severity and location
- **Coordinate rescue teams** with real-time assignments
- **Optimize resource allocation** (tools, personnel, vehicles)
- **Provide live situational awareness** via interactive maps

### Why Solace Agent Mesh?

| Challenge | SAM Solution |
|-----------|--------------|
| LLM "thinking time" causes timeouts | Asynchronous event-driven communication |
| Tight coupling between services | A2A Protocol for loose coupling |
| Message loss during failures | Guaranteed delivery via Solace broker |
| Complex orchestration logic | Built-in Orchestrator agent |
| Multiple interface requirements | Gateways (Web UI, REST, Slack, etc.) |

---

## Key Features

### 🎯 Master Agent (Victim Triage)
- Natural language communication with victims
- Automatic extraction of location, severity, and headcount
- Priority scoring: `CRITICAL` → `MODERATE` → `STABLE`
- Task delegation to rescue agents via A2A protocol

### 🚑 Rescue Agent
- Real-time victim assignment notifications
- Tools and equipment recommendation engine
- Personnel requirement calculations
- GPS navigation to victim locations

### 📦 Resource Agent
- Inventory tracking (tools, vehicles, medical supplies)
- Optimal resource allocation algorithms
- Low-stock alerts via built-in tools

### 🗺️ Real-time Dashboard
- Interactive map with live victim/team markers
- WebSocket-powered instant updates via SAM REST Gateway
- Multi-role interfaces (Victim, Rescue Team, Command Center)

---

## Architecture

### Solace Agent Mesh Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CLIENT INTERFACES                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   👤 Victim App        👷 Rescue Dashboard       🎖️ Command Center         │
│   (Next.js)            (Next.js)                 (SAM Web UI)               │
│                                                                             │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SAM GATEWAYS                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐           │
│   │   REST Gateway  │  │  Web UI Gateway │  │  Slack Gateway  │           │
│   │   (Custom API)  │  │   (Built-in)    │  │   (Optional)    │           │
│   └────────┬────────┘  └────────┬────────┘  └────────┬────────┘           │
│            │                    │                    │                     │
│            └────────────────────┼────────────────────┘                     │
│                                 │                                          │
│                                 ▼                                          │
│                    ┌────────────────────────┐                              │
│                    │    A2A Protocol        │                              │
│                    │  (Agent-to-Agent)      │                              │
│                    └────────────────────────┘                              │
│                                                                             │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     SOLACE PUBSUB+ EVENT BROKER                             │
│                                                                             │
│   • Guaranteed Message Delivery    • Topic-based Routing                   │
│   • Multi-AZ Replication           • A2A Protocol Transport                │
│                                                                             │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SAM AGENTS                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────┐                                                     │
│  │   ORCHESTRATOR    │  ← Built-in: Breaks down tasks & delegates          │
│  │   (Built-in)      │                                                     │
│  └─────────┬─────────┘                                                     │
│            │                                                                │
│            ▼                                                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐            │
│  │  MASTER AGENT   │  │  RESCUE AGENT   │  │ RESOURCE AGENT  │            │
│  │                 │  │                 │  │                 │            │
│  │  Tools:         │  │  Tools:         │  │  Tools:         │            │
│  │  • victim_chat  │  │  • calc_tools   │  │  • inventory    │            │
│  │  • prioritize   │  │  • calc_people  │  │  • allocate     │            │
│  │  • location_get │  │  • navigate     │  │  • alert        │            │
│  │  • builtin:*    │  │  • builtin:*    │  │  • builtin:*    │            │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### AWS Infrastructure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AWS Cloud                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────── Public Subnet (Multi-AZ) ───────────────────────┐  │
│  │                                                                        │  │
│  │   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐              │  │
│  │   │     ALB     │    │ CloudFront  │    │     NAT     │              │  │
│  │   │             │    │   (CDN)     │    │   Gateway   │              │  │
│  │   └──────┬──────┘    └──────┬──────┘    └─────────────┘              │  │
│  │          │                  │                                         │  │
│  └──────────┼──────────────────┼─────────────────────────────────────────┘  │
│             │                  │                                             │
│  ┌──────────┼──────────────────┼── Private Subnet (Multi-AZ) ────────────┐  │
│  │          ▼                  ▼                                          │  │
│  │                                                                        │  │
│  │   ┌─────────────────────────────────────────────────────────────────┐ │  │
│  │   │                    ECS FARGATE CLUSTER                           │ │  │
│  │   │                                                                  │ │  │
│  │   │  ┌───────────────────────────────────────────────────────────┐  │ │  │
│  │   │  │           SOLACE AGENT MESH (SAM)                         │  │ │  │
│  │   │  │                                                           │  │ │  │
│  │   │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │  │ │  │
│  │   │  │  │ Orchestrator│  │   Master    │  │   Rescue    │      │  │ │  │
│  │   │  │  │   Agent     │  │   Agent     │  │   Agent     │      │  │ │  │
│  │   │  │  └─────────────┘  └─────────────┘  └─────────────┘      │  │ │  │
│  │   │  │                                                           │  │ │  │
│  │   │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │  │ │  │
│  │   │  │  │  Resource   │  │ REST Gateway│  │  Web UI     │      │  │ │  │
│  │   │  │  │   Agent     │  │             │  │  Gateway    │      │  │ │  │
│  │   │  │  └─────────────┘  └─────────────┘  └─────────────┘      │  │ │  │
│  │   │  │                                                           │  │ │  │
│  │   │  └───────────────────────────────────────────────────────────┘  │ │  │
│  │   │                                                                  │ │  │
│  │   │  ┌───────────────┐                                              │ │  │
│  │   │  │   Next.js     │  ← Custom Frontend (connects to REST Gateway)│ │  │
│  │   │  │   Frontend    │                                              │ │  │
│  │   │  └───────────────┘                                              │ │  │
│  │   │                                                                  │ │  │
│  │   └──────────────────────────────────────────────────────────────────┘ │  │
│  │                                                                        │  │
│  │   ┌─────────────────────────────────────────────────────────────────┐ │  │
│  │   │              SOLACE PUBSUB+ BROKER                               │ │  │
│  │   │  (Solace Cloud Managed OR Self-hosted on Fargate)               │ │  │
│  │   └─────────────────────────────────────────────────────────────────┘ │  │
│  │                                                                        │  │
│  │   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐              │  │
│  │   │  DynamoDB   │    │ ElastiCache │    │     S3      │              │  │
│  │   │ (Sessions)  │    │  (Cache)    │    │ (Artifacts) │              │  │
│  │   └─────────────┘    └─────────────┘    └─────────────┘              │  │
│  │                                                                        │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Agent Framework** | Solace Agent Mesh (SAM) | Multi-agent orchestration |
| **Agent Runtime** | Google ADK + Solace AI Connector | Agent logic & lifecycle |
| **Event Broker** | Solace PubSub+ | Guaranteed message delivery |
| **Frontend** | Next.js 14, React 18, TypeScript | Custom real-time UI |
| **Mapping** | Leaflet / Mapbox GL | Interactive victim/team maps |
| **LLM** | OpenAI GPT-4 / Anthropic Claude | Natural language processing |
| **Container** | Docker, ECS Fargate | Serverless container hosting |
| **IaC** | Terraform | Infrastructure as Code |
| **CI/CD** | GitHub Actions | Automated deployment pipeline |

---

## Project Structure

```
disaster-rescue-system/
│
├── 📁 .github/
│   └── 📁 workflows/
│       ├── deploy.yml                 # Main deployment pipeline
│       ├── pr-check.yml               # Pull request validation
│       └── destroy.yml                # Infrastructure teardown
│
├── 📁 sam-project/                    # Solace Agent Mesh Project
│   │
│   ├── 📁 configs/                    # SAM Configuration (YAML-driven)
│   │   │
│   │   ├── 📁 agents/                 # Agent Configurations
│   │   │   ├── master_agent.yaml      # Victim communication & triage
│   │   │   ├── rescue_agent.yaml      # Rescue team coordination
│   │   │   └── resource_agent.yaml    # Resource management
│   │   │
│   │   ├── 📁 gateways/               # Gateway Configurations
│   │   │   ├── rest_gateway.yaml      # REST API for custom frontend
│   │   │   └── web_ui_gateway.yaml    # Built-in Web UI (optional)
│   │   │
│   │   ├── 📁 overrides/              # Environment-specific overrides
│   │   │   ├── dev.yaml
│   │   │   ├── staging.yaml
│   │   │   └── prod.yaml
│   │   │
│   │   └── shared_config.yaml         # Shared broker & LLM settings
│   │
│   ├── 📁 modules/                    # Custom Python Tools
│   │   │
│   │   ├── 📁 master_tools/
│   │   │   ├── __init__.py
│   │   │   ├── victim_chat.py         # Victim conversation handler
│   │   │   ├── prioritizer.py         # Severity prioritization logic
│   │   │   └── location_utils.py      # GPS/location utilities
│   │   │
│   │   ├── 📁 rescue_tools/
│   │   │   ├── __init__.py
│   │   │   ├── tools_calculator.py    # Equipment recommendation
│   │   │   ├── personnel_calc.py      # Manpower calculation
│   │   │   └── navigation.py          # Route planning
│   │   │
│   │   └── 📁 resource_tools/
│   │       ├── __init__.py
│   │       ├── inventory.py           # Inventory management
│   │       └── allocator.py           # Resource allocation
│   │
│   ├── 📁 tests/
│   │   ├── test_master_agent.py
│   │   ├── test_rescue_agent.py
│   │   └── test_resource_agent.py
│   │
│   ├── .env.example                   # Environment template
│   └── requirements.txt               # Python dependencies
│
├── 📁 frontend/                       # Next.js Custom Frontend
│   ├── 📁 src/
│   │   ├── 📁 app/
│   │   │   ├── 📁 victim/            # Victim reporting interface
│   │   │   ├── 📁 rescue/            # Rescue team dashboard
│   │   │   └── 📁 command/           # Command center overview
│   │   │
│   │   ├── 📁 components/
│   │   │   ├── 📁 Map/               # Live map components
│   │   │   ├── 📁 Chat/              # AI chat interface
│   │   │   └── 📁 Dashboard/         # Stats & metrics
│   │   │
│   │   ├── 📁 hooks/
│   │   │   └── useSamApi.ts          # SAM REST Gateway hook
│   │   │
│   │   └── 📁 lib/
│   │       └── sam-client.ts         # SAM API client
│   │
│   ├── Dockerfile
│   ├── package.json
│   └── next.config.js
│
├── 📁 terraform/                      # Infrastructure as Code
│   ├── 📁 environments/
│   │   ├── 📁 dev/
│   │   ├── 📁 staging/
│   │   └── 📁 prod/
│   │
│   └── 📁 modules/
│       ├── 📁 networking/            # VPC, Subnets, NAT
│       ├── 📁 ecs-cluster/           # ECS Cluster
│       ├── 📁 sam-deployment/        # SAM on Fargate
│       ├── 📁 solace-broker/         # Solace PubSub+ (optional)
│       └── 📁 frontend/              # Next.js deployment
│
├── 📁 docs/
│   ├── architecture.md
│   ├── agent-design.md
│   └── runbook.md
│
├── docker-compose.yml                 # Local development
├── Makefile
└── README.md
```

---

## Prerequisites

### Required Software

| Tool | Version | Purpose |
|------|---------|---------|
| **Python** | ≥ 3.10.16 | SAM runtime |
| **Node.js** | ≥ 18.x | Frontend development |
| **Docker** | ≥ 24.x | Container builds |
| **Terraform** | ≥ 1.6.x | Infrastructure deployment |
| **AWS CLI** | ≥ 2.x | AWS operations |

### Required Accounts

- **AWS Account** with appropriate IAM permissions
- **Solace Cloud Account** (free tier available) OR self-hosted Solace PubSub+
- **LLM API Key**: OpenAI, Anthropic, or Google

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/disaster-rescue-system.git
cd disaster-rescue-system
```

### 2. Set Up Solace Agent Mesh

```bash
# Navigate to SAM project
cd sam-project

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Solace Agent Mesh
pip install solace-agent-mesh

# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

### 3. Configure Environment Variables

**.env Configuration:**

```env
# ─────────────────────────────────────────────────────────
# Solace Broker Configuration
# ─────────────────────────────────────────────────────────
SOLACE_BROKER_URL=tcp://localhost:55555
SOLACE_BROKER_VPN=default
SOLACE_BROKER_USERNAME=admin
SOLACE_BROKER_PASSWORD=admin

# For Solace Cloud:
# SOLACE_BROKER_URL=tcps://your-service.messaging.solace.cloud:55443
# SOLACE_BROKER_VPN=your-vpn-name
# SOLACE_BROKER_USERNAME=solace-cloud-client
# SOLACE_BROKER_PASSWORD=your-password

# ─────────────────────────────────────────────────────────
# LLM Configuration
# ─────────────────────────────────────────────────────────
SAM_LLM_PROVIDER=openai
SAM_LLM_MODEL=gpt-4
SAM_LLM_API_KEY=sk-your-openai-key

# OR for Anthropic:
# SAM_LLM_PROVIDER=anthropic
# SAM_LLM_MODEL=claude-sonnet-4-20250514
# SAM_LLM_API_KEY=sk-ant-your-key

# ─────────────────────────────────────────────────────────
# Application Settings
# ─────────────────────────────────────────────────────────
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### 4. Initialize and Run SAM

```bash
# Initialize SAM project (if starting fresh)
sam init

# Build the project
sam build

# Run all agents and gateways
sam run

# Or run with build in one command
sam run -b
```

### 5. Access the Interfaces

| Interface | URL | Description |
|-----------|-----|-------------|
| SAM Web UI | http://localhost:8000 | Built-in chat interface |
| REST API | http://localhost:5050 | API for custom frontend |
| Config Portal | http://localhost:5002 | Agent configuration UI |

### 6. Run Custom Frontend (Optional)

```bash
# In a new terminal
cd frontend
npm install
npm run dev
```

Access at: http://localhost:3000

---

## Agent Configuration

### Master Agent Configuration

**`configs/agents/master_agent.yaml`**

```yaml
# ─────────────────────────────────────────────────────────
# Master Agent - Victim Communication & Triage
# ─────────────────────────────────────────────────────────

agent:
  name: master_agent
  description: >
    Communicates with disaster victims, extracts critical information
    (location, severity, number of people), and prioritizes rescue operations.
  
  # Agent Card (for A2A discovery)
  agent_card:
    name: "Disaster Triage Master"
    description: "Primary agent for victim communication and rescue prioritization"
    capabilities:
      - victim_communication
      - severity_assessment
      - location_extraction
      - rescue_prioritization

  # LLM Configuration
  llm:
    provider: ${SAM_LLM_PROVIDER}
    model: ${SAM_LLM_MODEL}
    api_key: ${SAM_LLM_API_KEY}
    temperature: 0.3  # Lower for more consistent triage decisions

  # System Instructions
  instructions: |
    You are the Master Disaster Rescue Agent. Your responsibilities:
    
    1. VICTIM COMMUNICATION:
       - Communicate calmly and empathetically with victims
       - Ask clear questions to gather critical information
       - Provide reassurance while extracting details
    
    2. INFORMATION EXTRACTION:
       - Location: Get GPS coordinates or detailed address
       - Severity: Assess medical urgency (CRITICAL, MODERATE, STABLE)
       - Headcount: Number of people needing rescue
       - Conditions: Injuries, hazards, accessibility
    
    3. PRIORITIZATION:
       - CRITICAL: Life-threatening, immediate danger
       - MODERATE: Injured but stable, needs attention within hours
       - STABLE: Safe but stranded, can wait for available resources
    
    4. DELEGATION:
       - Assign victims to rescue teams via Rescue Agent
       - Request resources via Resource Agent
    
    Always maintain a calm, professional tone even in crisis situations.

  # Tools Configuration
  tools:
    # Built-in SAM tools
    - group_name: artifact_management
      tool_type: builtin-group
    
    - group_name: data_analysis
      tool_type: builtin-group
    
    # Custom Python tools
    - tool_type: python
      name: extract_location
      description: "Extract and validate GPS coordinates from victim input"
      module: modules.master_tools.location_utils
      function: extract_location
    
    - tool_type: python
      name: calculate_priority
      description: "Calculate victim priority score based on severity factors"
      module: modules.master_tools.prioritizer
      function: calculate_priority
      parameters:
        - name: severity
          type: string
          description: "Severity level: CRITICAL, MODERATE, or STABLE"
          required: true
        - name: num_people
          type: integer
          description: "Number of people affected"
          required: true
        - name: has_injuries
          type: boolean
          description: "Whether there are reported injuries"
          required: true
    
    - tool_type: python
      name: create_victim_report
      description: "Create structured victim report for rescue teams"
      module: modules.master_tools.victim_chat
      function: create_victim_report

  # Lifecycle hooks (optional)
  lifecycle:
    on_start:
      module: modules.master_tools.lifecycle
      function: initialize_master_agent
    on_stop:
      module: modules.master_tools.lifecycle
      function: cleanup_master_agent
```

### Rescue Agent Configuration

**`configs/agents/rescue_agent.yaml`**

```yaml
# ─────────────────────────────────────────────────────────
# Rescue Agent - Team Coordination & Equipment
# ─────────────────────────────────────────────────────────

agent:
  name: rescue_agent
  description: >
    Receives victim assignments, calculates required tools and personnel,
    and coordinates rescue team deployments.
  
  agent_card:
    name: "Rescue Coordinator"
    description: "Coordinates rescue teams, equipment, and personnel"
    capabilities:
      - team_assignment
      - equipment_calculation
      - personnel_planning
      - navigation

  llm:
    provider: ${SAM_LLM_PROVIDER}
    model: ${SAM_LLM_MODEL}
    api_key: ${SAM_LLM_API_KEY}
    temperature: 0.2

  instructions: |
    You are the Rescue Coordination Agent. Your responsibilities:
    
    1. TEAM ASSIGNMENT:
       - Receive victim reports from Master Agent
       - Match available rescue teams to victims
       - Consider team proximity and capabilities
    
    2. EQUIPMENT CALCULATION:
       - Based on situation type (building collapse, flood, fire, etc.)
       - Calculate tools needed (stretchers, cutting equipment, etc.)
       - Request equipment from Resource Agent
    
    3. PERSONNEL PLANNING:
       - Calculate minimum personnel needed
       - Consider victim count and severity
       - Account for hazardous conditions
    
    4. NAVIGATION:
       - Provide optimal routes to victim locations
       - Consider road conditions and obstacles
    
    Always prioritize CRITICAL victims. Coordinate with Resource Agent
    for equipment availability before finalizing assignments.

  tools:
    - group_name: artifact_management
      tool_type: builtin-group
    
    - tool_type: python
      name: calculate_equipment
      description: "Calculate required equipment based on rescue scenario"
      module: modules.rescue_tools.tools_calculator
      function: calculate_equipment
    
    - tool_type: python
      name: calculate_personnel
      description: "Calculate minimum personnel for rescue operation"
      module: modules.rescue_tools.personnel_calc
      function: calculate_personnel
    
    - tool_type: python
      name: get_route
      description: "Get optimal route to victim location"
      module: modules.rescue_tools.navigation
      function: get_route
```

### Resource Agent Configuration

**`configs/agents/resource_agent.yaml`**

```yaml
# ─────────────────────────────────────────────────────────
# Resource Agent - Inventory & Allocation
# ─────────────────────────────────────────────────────────

agent:
  name: resource_agent
  description: >
    Manages inventory of rescue equipment, vehicles, and personnel.
    Handles allocation requests and alerts on low stock.
  
  agent_card:
    name: "Resource Manager"
    description: "Manages equipment inventory and resource allocation"
    capabilities:
      - inventory_management
      - resource_allocation
      - availability_check
      - low_stock_alerts

  llm:
    provider: ${SAM_LLM_PROVIDER}
    model: ${SAM_LLM_MODEL}
    api_key: ${SAM_LLM_API_KEY}
    temperature: 0.1  # Very consistent for inventory operations

  instructions: |
    You are the Resource Management Agent. Your responsibilities:
    
    1. INVENTORY MANAGEMENT:
       - Track available equipment (stretchers, tools, vehicles)
       - Monitor personnel availability
       - Update stock levels after allocations
    
    2. RESOURCE ALLOCATION:
       - Process equipment requests from Rescue Agent
       - Check availability before confirming
       - Reserve resources for confirmed missions
    
    3. ALERTS:
       - Alert when equipment falls below threshold
       - Notify when personnel availability is low
       - Escalate critical shortages to Command Center
    
    Always confirm allocation before updating inventory.
    Maintain accurate records for post-incident analysis.

  tools:
    - group_name: artifact_management
      tool_type: builtin-group
    
    - group_name: data_analysis
      tool_type: builtin-group
    
    - tool_type: python
      name: check_inventory
      description: "Check current inventory levels"
      module: modules.resource_tools.inventory
      function: check_inventory
    
    - tool_type: python
      name: allocate_resources
      description: "Allocate resources to a rescue mission"
      module: modules.resource_tools.allocator
      function: allocate_resources
    
    - tool_type: python
      name: send_alert
      description: "Send low-stock or critical alert"
      module: modules.resource_tools.inventory
      function: send_alert
```

### Shared Configuration

**`configs/shared_config.yaml`**

```yaml
# ─────────────────────────────────────────────────────────
# Shared Configuration for All Agents
# ─────────────────────────────────────────────────────────

broker:
  url: ${SOLACE_BROKER_URL}
  vpn: ${SOLACE_BROKER_VPN}
  username: ${SOLACE_BROKER_USERNAME}
  password: ${SOLACE_BROKER_PASSWORD}

llm_defaults: &llm_defaults
  provider: ${SAM_LLM_PROVIDER}
  model: ${SAM_LLM_MODEL}
  api_key: ${SAM_LLM_API_KEY}

logging:
  level: ${LOG_LEVEL:INFO}
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

---

## Custom Python Tools

### Example: Priority Calculator

**`modules/master_tools/prioritizer.py`**

```python
"""
Victim Priority Calculator for Master Agent
"""
from typing import Dict, Any
from datetime import datetime

def calculate_priority(
    severity: str,
    num_people: int,
    has_injuries: bool,
    additional_factors: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Calculate victim priority score based on multiple factors.
    
    Priority Score Range: 0-100 (higher = more urgent)
    
    Args:
        severity: CRITICAL, MODERATE, or STABLE
        num_people: Number of people affected
        has_injuries: Whether injuries are reported
        additional_factors: Optional dict with hazards, accessibility, etc.
    
    Returns:
        Dict with priority_score, priority_level, and reasoning
    """
    score = 0
    reasoning = []
    
    # Severity scoring (0-50 points)
    severity_scores = {
        "CRITICAL": 50,
        "MODERATE": 30,
        "STABLE": 10
    }
    severity_score = severity_scores.get(severity.upper(), 20)
    score += severity_score
    reasoning.append(f"Severity ({severity}): +{severity_score} points")
    
    # People count scoring (0-20 points)
    people_score = min(num_people * 4, 20)
    score += people_score
    reasoning.append(f"People count ({num_people}): +{people_score} points")
    
    # Injury scoring (0-15 points)
    if has_injuries:
        score += 15
        reasoning.append("Injuries reported: +15 points")
    
    # Additional factors (0-15 points)
    if additional_factors:
        if additional_factors.get("fire_hazard"):
            score += 5
            reasoning.append("Fire hazard: +5 points")
        if additional_factors.get("flooding"):
            score += 5
            reasoning.append("Flooding: +5 points")
        if additional_factors.get("structural_collapse"):
            score += 5
            reasoning.append("Structural collapse: +5 points")
    
    # Determine priority level
    if score >= 70:
        priority_level = "CRITICAL"
    elif score >= 40:
        priority_level = "HIGH"
    elif score >= 20:
        priority_level = "MEDIUM"
    else:
        priority_level = "LOW"
    
    return {
        "priority_score": min(score, 100),
        "priority_level": priority_level,
        "reasoning": reasoning,
        "calculated_at": datetime.utcnow().isoformat()
    }
```

### Example: Equipment Calculator

**`modules/rescue_tools/tools_calculator.py`**

```python
"""
Equipment Calculator for Rescue Agent
"""
from typing import Dict, List, Any

# Equipment database
EQUIPMENT_TEMPLATES = {
    "building_collapse": {
        "required": ["stretcher", "first_aid_kit", "flashlight", "radio"],
        "optional": ["hydraulic_cutter", "concrete_saw", "airbag_lifter"],
        "personnel_min": 4
    },
    "flood": {
        "required": ["life_jacket", "rope", "stretcher", "first_aid_kit"],
        "optional": ["inflatable_boat", "water_pump"],
        "personnel_min": 3
    },
    "fire": {
        "required": ["fire_extinguisher", "breathing_apparatus", "first_aid_kit"],
        "optional": ["thermal_camera", "ladder"],
        "personnel_min": 4
    },
    "medical": {
        "required": ["stretcher", "first_aid_kit", "defibrillator"],
        "optional": ["oxygen_tank", "splints"],
        "personnel_min": 2
    },
    "general": {
        "required": ["first_aid_kit", "flashlight", "radio", "stretcher"],
        "optional": [],
        "personnel_min": 2
    }
}

def calculate_equipment(
    scenario_type: str,
    num_victims: int,
    severity: str,
    special_conditions: List[str] = None
) -> Dict[str, Any]:
    """
    Calculate required equipment based on rescue scenario.
    
    Args:
        scenario_type: Type of disaster (building_collapse, flood, fire, medical, general)
        num_victims: Number of victims to rescue
        severity: CRITICAL, MODERATE, or STABLE
        special_conditions: List of special conditions (e.g., ["elderly", "children"])
    
    Returns:
        Dict with equipment list, quantities, and personnel requirements
    """
    template = EQUIPMENT_TEMPLATES.get(scenario_type.lower(), EQUIPMENT_TEMPLATES["general"])
    
    equipment = []
    
    # Add required equipment
    for item in template["required"]:
        quantity = 1
        if item == "stretcher":
            quantity = max(1, num_victims)
        elif item == "first_aid_kit":
            quantity = max(1, (num_victims + 2) // 3)
        
        equipment.append({
            "item": item,
            "quantity": quantity,
            "priority": "required"
        })
    
    # Add optional equipment based on severity
    if severity.upper() in ["CRITICAL", "MODERATE"]:
        for item in template["optional"]:
            equipment.append({
                "item": item,
                "quantity": 1,
                "priority": "recommended"
            })
    
    # Handle special conditions
    if special_conditions:
        if "elderly" in special_conditions or "disabled" in special_conditions:
            equipment.append({
                "item": "wheelchair_stretcher",
                "quantity": 1,
                "priority": "required"
            })
        if "children" in special_conditions:
            equipment.append({
                "item": "pediatric_kit",
                "quantity": 1,
                "priority": "required"
            })
    
    # Calculate personnel
    base_personnel = template["personnel_min"]
    if num_victims > 3:
        base_personnel += (num_victims - 3) // 2
    if severity.upper() == "CRITICAL":
        base_personnel += 2
    
    return {
        "equipment": equipment,
        "personnel_required": base_personnel,
        "scenario_type": scenario_type,
        "notes": f"Equipment calculated for {num_victims} victim(s), {severity} severity"
    }
```

---

## Deployment

### Local Development with Docker Compose

**`docker-compose.yml`**

```yaml
version: '3.8'

services:
  # ─────────────────────────────────────────────────────────
  # Solace PubSub+ Broker (Local Development)
  # ─────────────────────────────────────────────────────────
  solace:
    image: solace/solace-pubsub-standard:latest
    container_name: solace-broker
    hostname: solace
    ports:
      - "55555:55555"   # SMF
      - "8080:8080"     # SEMP / Web Admin
      - "1883:1883"     # MQTT
      - "8000:8000"     # WebSocket
    environment:
      - username_admin_globalaccesslevel=admin
      - username_admin_password=admin
    shm_size: 1g
    ulimits:
      core: -1
      nofile:
        soft: 2448
        hard: 38048
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health-check/guaranteed-active"]
      interval: 30s
      timeout: 10s
      retries: 5

  # ─────────────────────────────────────────────────────────
  # Solace Agent Mesh
  # ─────────────────────────────────────────────────────────
  sam:
    build:
      context: ./sam-project
      dockerfile: Dockerfile
    container_name: sam-agents
    depends_on:
      solace:
        condition: service_healthy
    ports:
      - "8001:8000"    # SAM Web UI
      - "5050:5050"    # REST Gateway
      - "5002:5002"    # Config Portal
    environment:
      - SOLACE_BROKER_URL=tcp://solace:55555
      - SOLACE_BROKER_VPN=default
      - SOLACE_BROKER_USERNAME=admin
      - SOLACE_BROKER_PASSWORD=admin
      - SAM_LLM_PROVIDER=${SAM_LLM_PROVIDER}
      - SAM_LLM_MODEL=${SAM_LLM_MODEL}
      - SAM_LLM_API_KEY=${SAM_LLM_API_KEY}
    volumes:
      - ./sam-project/configs:/app/configs
      - ./sam-project/modules:/app/modules
    command: sam run -b

  # ─────────────────────────────────────────────────────────
  # Next.js Frontend
  # ─────────────────────────────────────────────────────────
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: rescue-frontend
    depends_on:
      - sam
    ports:
      - "3000:3000"
    environment:
      - SAM_API_URL=http://sam:5050
      - NEXT_PUBLIC_SAM_API_URL=http://localhost:5050
    volumes:
      - ./frontend/src:/app/src

networks:
  default:
    name: disaster-rescue-network
```

### Run Locally

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f sam

# Stop services
docker-compose down
```

### Production Deployment (AWS ECS Fargate)

See `terraform/` directory for complete infrastructure code.

```bash
# Deploy to AWS
cd terraform/environments/prod
terraform init
terraform plan
terraform apply
```

---

## GitHub Actions CI/CD

**`.github/workflows/deploy.yml`**

```yaml
name: Deploy Disaster Rescue System

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  AWS_REGION: ap-southeast-1
  ECR_REGISTRY: ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.ap-southeast-1.amazonaws.com

jobs:
  # ─────────────────────────────────────────────────────────
  # Test SAM Agents
  # ─────────────────────────────────────────────────────────
  test-agents:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install Dependencies
        working-directory: sam-project
        run: |
          pip install solace-agent-mesh
          pip install -r requirements.txt
          pip install pytest
      
      - name: Run Tests
        working-directory: sam-project
        run: pytest tests/ -v

  # ─────────────────────────────────────────────────────────
  # Test Frontend
  # ─────────────────────────────────────────────────────────
  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install & Test
        working-directory: frontend
        run: |
          npm ci
          npm run test
          npm run build

  # ─────────────────────────────────────────────────────────
  # Build & Push Docker Images
  # ─────────────────────────────────────────────────────────
  build:
    needs: [test-agents, test-frontend]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      
      - name: Configure AWS
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}
      
      - name: Login to ECR
        run: |
          aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_REGISTRY
      
      - name: Build & Push SAM
        run: |
          docker build -t $ECR_REGISTRY/rescue-sam:${{ github.sha }} ./sam-project
          docker push $ECR_REGISTRY/rescue-sam:${{ github.sha }}
      
      - name: Build & Push Frontend
        run: |
          docker build -t $ECR_REGISTRY/rescue-frontend:${{ github.sha }} ./frontend
          docker push $ECR_REGISTRY/rescue-frontend:${{ github.sha }}

  # ─────────────────────────────────────────────────────────
  # Deploy Infrastructure
  # ─────────────────────────────────────────────────────────
  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
      
      - name: Terraform Apply
        working-directory: terraform/environments/prod
        run: |
          terraform init
          terraform apply -auto-approve \
            -var="sam_image_tag=${{ github.sha }}" \
            -var="frontend_image_tag=${{ github.sha }}"
```

---

## Cost Estimate

| Component | Service | Monthly Cost (Est.) |
|-----------|---------|---------------------|
| **SAM Container** | ECS Fargate (2-5 tasks) | $40-100 |
| **Frontend** | ECS Fargate (2 tasks) | $30-50 |
| **Solace Broker** | Solace Cloud (Free/Starter) | $0-99 |
| **Load Balancer** | ALB | $20 |
| **NAT Gateway** | NAT Gateway | $35 |
| **Storage** | S3 + DynamoDB | $10-20 |
| **Monitoring** | CloudWatch | $10-20 |
| **Total** | | **$145-344/month** |

---

## References

- [Solace Agent Mesh GitHub](https://github.com/SolaceLabs/solace-agent-mesh)
- [SAM Documentation](https://solacelabs.github.io/solace-agent-mesh/docs/documentation/getting-started/introduction/)
- [Solace Agent Mesh Codelab](https://codelabs.solace.dev/codelabs/solace-agent-mesh/)
- [SAM Docker Quickstart](https://github.com/SolaceLabs/solace-agent-mesh-docker-quickstart)
- [SAM Helm Quickstart](https://solaceproducts.github.io/solace-agent-mesh-helm-quickstart/docs/)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

Apache 2.0 - See [LICENSE](LICENSE)

---

<p align="center">
  <strong>Built with Solace Agent Mesh 🚀</strong>
</p>
