# Test# 🚨 Disaster Rescue Coordination System

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

## 🏗️ System Architecture

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   CLIENT LAYER                           │
│             👷  Rescue Dashboard                        │
└───────────────────────┬──────────────────────────────────┘
                        │
                        │
                        │
┌───────────────────────▼──────────────────────────────────┐
│            SOLACE PUBSUB+ EVENT BROKER                   │
│  • Guaranteed Delivery  • Topic Routing  • Multi-AZ     │
└───────────────────────┬──────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼───────┐ ┌────▼────┐ ┌────────▼────────┐
│ MASTER AGENT  │ │ RESCUE  │ │ RESOURCE AGENT  │
│               │ │ AGENT   │ │                 │
│ • Triage      │ │ • Teams │ │ • Inventory     │
│ • Prioritize  │ │ • Tools │ │ • Allocation    │
└───────────────┘ └─────────┘ └─────────────────┘
```

### Agent Responsibilities

#### 🎯 Master Agent (Victim Triage)
- Communicates with victims via natural language
- Extracts location, severity, headcount, and hazard information
- Assigns priority scores (CRITICAL/MODERATE/STABLE)
- Delegates rescue tasks to Deployment Agent

#### 🚑 Deployment Agent
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

## 📁 Project Structure

```
disaster-rescue-system/
│
├── sam-project/                    # Solace Agent Mesh Configuration
│   ├── configs/
│   │   ├── agents/                 # Agent YAML configs
│   │   │   ├── master_agent.yaml
│   │   │   ├── rescue_agent.yaml
│   │   │   └── resource_agent.yaml
│   │   ├── gateways/               # Gateway configs
│   │   └── shared_config.yaml      # Shared broker settings
│   │
│   ├── modules/                    # Custom Python Tools
│   │   ├── master_tools/           # Victim communication & triage
│   │   ├── rescue_tools/           # Equipment & personnel calc
│   │   └── resource_tools/         # Inventory management
│   │
│   └── tests/                      # Unit tests
│
├── frontend/                       # Next.js Custom UI
│   ├── src/
│   │   ├── app/
│   │   │   ├── victim/            # Victim reporting interface
│   │   │   ├── rescue/            # Rescue team dashboard
│   │   │   └── command/           # Command center
│   │   ├── components/
│   │   └── lib/                    # SAM API client
│   │
├── terraform/                      # AWS Infrastructure
│   ├── environments/
│   └── modules/
│
├── .github/workflows/              # CI/CD Pipelines
│   ├── deploy.yml
│   └── pr-check.yml
│
└── docker-compose.yml              # Local development
```

---

## 🚀 Quick Start

### Prerequisites

- **Python** ≥ 3.10.16
- **Node.js** ≥ 18.x
- **Docker** ≥ 24.x
- **Terraform** ≥ 1.6.x (for AWS deployment)
- **Solace Cloud Account** or local Solace PubSub+ broker

### 1. Clone the Repository

```bash
git clone https://github.com/ChrisPham03/Disaster-Agent.git
cd Disaster-Agent
```

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

# Install SAM and dependencies
pip install solace-agent-mesh
pip install -r requirements.txt
```

### 4. Launch with Docker Compose

The easiest way to run the entire system locally:

```bash
# From project root
docker-compose up -d

# View logs
docker-compose logs -f sam
```

This will start:
- Solace PubSub+ broker (localhost:55555)
- SAM agents and gateways
- Next.js frontend (localhost:3000)

### 5. Access the Interfaces

| Interface | URL | Description |
|-----------|-----|-------------|
| **SAM Web UI** | http://localhost:8000 | Built-in agent chat interface |
| **REST API** | http://localhost:5050 | API for custom frontends |
| **Config Portal** | http://localhost:5002 | Agent configuration UI |
| **Solace Admin** | http://localhost:8080 | Broker management |
| **Custom Frontend** | http://localhost:3000 | React-based rescue dashboard |

### 6. Test the System

Try these sample interactions via the Web UI:

```
Victim: "Help! I'm trapped in a collapsed building at 123 Main St. 
There are 3 of us here and one person has a broken leg."

Expected Flow:
1. Master Agent extracts info and calculates priority (HIGH/CRITICAL)
2. Rescue Agent calculates equipment needs (stretcher, first aid, hydraulic cutters)
3. Resource Agent allocates available equipment
4. Rescue team receives assignment with route
```

---

## 🔧 Configuration

### Master Agent Configuration

The Master Agent handles victim communication and triage. Key configuration in `configs/agents/master_agent.yaml`:

```yaml
agent:
  name: master_agent
  llm:
    temperature: 0.3  # Lower for consistent triage
  
  instructions: |
    Extract critical information:
    - Location (GPS or address)
    - Severity (CRITICAL/MODERATE/STABLE)
    - Number of people
    - Injuries and hazards
  
  tools:
    - name: extract_location
      module: modules.master_tools.location_utils
    - name: calculate_priority
      module: modules.master_tools.prioritizer
```

### Rescue Agent Configuration

Handles team coordination and equipment calculation:

```yaml
agent:
  name: rescue_agent
  llm:
    temperature: 0.2
  
  tools:
    - name: calculate_equipment
      module: modules.rescue_tools.tools_calculator
    - name: calculate_personnel
      module: modules.rescue_tools.personnel_calc
```

### Environment-Specific Overrides

Use `configs/overrides/` for different environments:

```bash
sam run --override configs/overrides/prod.yaml
```

---

## 🧪 Testing

Run the test suite:

```bash
cd sam-project

# Run all tests
pytest tests/ -v

# Run specific agent tests
pytest tests/test_master_agent.py -v

# Run with coverage
pytest --cov=modules tests/
```

---

## 📊 Custom Tools Development

Create custom Python tools to extend agent capabilities:

```python
# modules/master_tools/prioritizer.py

def calculate_priority(
    severity: str,
    num_people: int,
    has_injuries: bool
) -> dict:
    """
    Calculate victim priority score (0-100).
    
    Returns:
        {
            "priority_score": int,
            "priority_level": str,
            "reasoning": list[str]
        }
    """
    score = 0
    reasoning = []
    
    # Severity scoring (0-50 points)
    severity_map = {"CRITICAL": 50, "MODERATE": 30, "STABLE": 10}
    score += severity_map.get(severity.upper(), 20)
    reasoning.append(f"Severity ({severity}): +{score} points")
    
    # People count (0-20 points)
    people_score = min(num_people * 4, 20)
    score += people_score
    reasoning.append(f"People: +{people_score}")
    
    # Injuries (0-15 points)
    if has_injuries:
        score += 15
        reasoning.append("Injuries: +15")
    
    priority_level = (
        "CRITICAL" if score >= 70 
        else "HIGH" if score >= 40 
        else "MEDIUM" if score >= 20 
        else "LOW"
    )
    
    return {
        "priority_score": min(score, 100),
        "priority_level": priority_level,
        "reasoning": reasoning
    }
```

Register the tool in your agent config:

```yaml
tools:
  - tool_type: python
    name: calculate_priority
    module: modules.master_tools.prioritizer
    function: calculate_priority
    parameters:
      - name: severity
        type: string
        required: true
```

---

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

### Infrastructure Created

- **VPC**: Multi-AZ with public/private subnets
- **ECS Cluster**: Fargate tasks for SAM and frontend
- **ALB**: Application Load Balancer for traffic routing
- **ECR**: Docker image repositories
- **DynamoDB**: Session storage
- **S3**: Artifact storage
- **CloudWatch**: Logging and monitoring

### Estimated AWS Costs

| Component | Monthly Cost |
|-----------|-------------|
| ECS Fargate (SAM) | $40-100 |
| ECS Fargate (Frontend) | $30-50 |
| Solace Cloud | $0-99 |
| ALB | $20 |
| NAT Gateway | $35 |
| Storage (S3/DynamoDB) | $10-20 |
| Monitoring | $10-20 |
| **Total** | **$145-344/mo** |

---

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

## 📚 Documentation

- **[Solace Agent Mesh Docs](https://solacelabs.github.io/solace-agent-mesh/)**
- **[SAM GitHub Repository](https://github.com/SolaceLabs/solace-agent-mesh)**
- **[SAM Codelab Tutorial](https://codelabs.solace.dev/codelabs/solace-agent-mesh/)**
- **[Architecture Deep Dive](./docs/architecture.md)**
- **[Agent Design Guide](./docs/agent-design.md)**
- **[Operations Runbook](./docs/runbook.md)**

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and test thoroughly
4. Commit with clear messages (`git commit -m 'Add amazing feature'`)
5. Push to your fork (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript for frontend code
- Write tests for new features
- Update documentation as needed
- Keep commits atomic and well-described

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: Agents not connecting to Solace broker
```bash
# Check broker status
docker-compose ps solace

# View broker logs
docker-compose logs solace

# Verify broker health
curl http://localhost:8080/health-check/guaranteed-active
```

**Issue**: LLM API timeout errors
```yaml
# Increase timeout in agent config
llm:
  timeout: 120  # seconds
  max_retries: 3
```

**Issue**: Frontend not connecting to SAM API
```bash
# Verify REST Gateway is running
curl http://localhost:5050/health

# Check CORS settings in gateway config
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Solace** for the Agent Mesh framework
- **Anthropic** and **OpenAI** for LLM capabilities
- **Google ADK** for agent runtime
- All contributors and disaster response professionals who provided insights

---

## 📧 Contact

For questions or support:
- **GitHub Issues**: [Create an issue](https://github.com/ChrisPham03/Disaster-Agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ChrisPham03/Disaster-Agent/discussions)

---

**Built with ❤️ using Solace Agent Mesh**

*Making disaster response faster, smarter, and more coordinated.*
