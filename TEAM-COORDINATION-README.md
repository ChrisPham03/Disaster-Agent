# 🚨 Disaster Rescue System - Team Coordination Guide

## ⚠️ READ THIS FIRST

This document is the **single source of truth** for our 2-person backend team. Both Person A and Person B must follow these specifications exactly to avoid integration errors.

**Copy this entire document to your Claude agent so it understands the full context.**

---

## 👥 Team Roles

| Role | Responsibility | Agents Owned |
|------|----------------|--------------|
| **Person A** | Victim intake + Resource management | Master Agent, Resource Agent |
| **Person B** | Rescue coordination + API layer | Rescue Agent, REST Gateway |

---

## 📁 Project Structure & File Ownership

```
disaster-rescue-system/
│
├── sam-project/
│   │
│   ├── configs/
│   │   ├── agents/
│   │   │   ├── master_agent.yaml      # ← PERSON A OWNS
│   │   │   ├── rescue_agent.yaml      # ← PERSON B OWNS
│   │   │   └── resource_agent.yaml    # ← PERSON A OWNS
│   │   │
│   │   ├── gateways/
│   │   │   └── rest_gateway.yaml      # ← PERSON B OWNS
│   │   │
│   │   └── shared_config.yaml         # ← SHARED (don't modify alone)
│   │
│   ├── modules/
│   │   ├── __init__.py                # ← SHARED
│   │   │
│   │   ├── master_tools/              # ← PERSON A OWNS (entire folder)
│   │   │   ├── __init__.py
│   │   │   ├── prioritizer.py
│   │   │   ├── location_utils.py
│   │   │   └── victim_chat.py
│   │   │
│   │   ├── rescue_tools/              # ← PERSON B OWNS (entire folder)
│   │   │   ├── __init__.py
│   │   │   ├── tools_calculator.py
│   │   │   ├── personnel_calc.py
│   │   │   └── navigation.py
│   │   │
│   │   └── resource_tools/            # ← PERSON A OWNS (entire folder)
│   │       ├── __init__.py
│   │       ├── inventory.py
│   │       └── allocator.py
│   │
│   ├── .env                           # ← SHARED (copy from .env.example)
│   └── requirements.txt               # ← SHARED
│
└── docker-compose.yml                 # ← SHARED (don't modify)
```

---

## 🔴 CRITICAL: Data Contracts

**Both persons MUST use these EXACT data structures. No modifications without team sync.**

### Contract 1: Victim Report

**Producer:** Master Agent (Person A)  
**Consumer:** Rescue Agent (Person B), Resource Agent (Person A)

```python
VICTIM_REPORT = {
    "victim_id": str,          # Format: "V-{timestamp}" e.g., "V-1704067200"
    "location": {
        "lat": float,          # Latitude, e.g., 13.7563
        "lng": float,          # Longitude, e.g., 100.5018
        "address": str         # Human readable, e.g., "123 Main St, Bangkok"
    },
    "severity": str,           # ENUM: "CRITICAL" | "MODERATE" | "STABLE"
    "num_people": int,         # Positive integer, minimum 1
    "has_injuries": bool,      # True/False
    "conditions": list[str],   # e.g., ["fire_hazard", "flooding", "structural_collapse"]
    "priority_score": int,     # Range: 0-100 (higher = more urgent)
    "priority_level": str,     # ENUM: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
    "reported_at": str         # ISO 8601 format: "2024-01-01T12:00:00Z"
}
```

**Example:**
```json
{
    "victim_id": "V-1704067200",
    "location": {
        "lat": 13.7563,
        "lng": 100.5018,
        "address": "45 Sukhumvit Road, Bangkok"
    },
    "severity": "CRITICAL",
    "num_people": 3,
    "has_injuries": true,
    "conditions": ["structural_collapse", "fire_hazard"],
    "priority_score": 85,
    "priority_level": "CRITICAL",
    "reported_at": "2024-01-01T12:00:00Z"
}
```

---

### Contract 2: Equipment Request

**Producer:** Rescue Agent (Person B)  
**Consumer:** Resource Agent (Person A)

```python
EQUIPMENT_REQUEST = {
    "request_id": str,         # Format: "REQ-{timestamp}"
    "mission_id": str,         # Format: "M-{timestamp}"
    "victim_id": str,          # Must match victim_id from VICTIM_REPORT
    "scenario_type": str,      # ENUM: "building_collapse" | "flood" | "fire" | "medical" | "general"
    "equipment": list[dict],   # List of equipment items
    "personnel_required": int, # Minimum personnel needed
    "requested_at": str        # ISO 8601 format
}

# Equipment item structure
EQUIPMENT_ITEM = {
    "item": str,               # Equipment name (see VALID_EQUIPMENT list)
    "quantity": int,           # Positive integer
    "priority": str            # ENUM: "required" | "recommended"
}
```

**Valid Equipment Names (use EXACTLY these strings):**
```python
VALID_EQUIPMENT = [
    # Medical
    "stretcher",
    "first_aid_kit",
    "defibrillator",
    "oxygen_tank",
    "splints",
    "pediatric_kit",
    "wheelchair_stretcher",
    
    # Rescue Tools
    "hydraulic_cutter",
    "concrete_saw",
    "airbag_lifter",
    "flashlight",
    "radio",
    "rope",
    "ladder",
    
    # Fire/Flood
    "fire_extinguisher",
    "breathing_apparatus",
    "thermal_camera",
    "life_jacket",
    "inflatable_boat",
    "water_pump"
]
```

**Example:**
```json
{
    "request_id": "REQ-1704067500",
    "mission_id": "M-1704067500",
    "victim_id": "V-1704067200",
    "scenario_type": "building_collapse",
    "equipment": [
        {"item": "stretcher", "quantity": 3, "priority": "required"},
        {"item": "first_aid_kit", "quantity": 1, "priority": "required"},
        {"item": "hydraulic_cutter", "quantity": 1, "priority": "recommended"}
    ],
    "personnel_required": 6,
    "requested_at": "2024-01-01T12:05:00Z"
}
```

---

### Contract 3: Allocation Response

**Producer:** Resource Agent (Person A)  
**Consumer:** Rescue Agent (Person B)

```python
ALLOCATION_RESPONSE = {
    "request_id": str,         # Must match request_id from EQUIPMENT_REQUEST
    "mission_id": str,         # Must match mission_id from EQUIPMENT_REQUEST
    "allocated": bool,         # True if successful, False if insufficient resources
    "team_id": str,            # Format: "T-{name}" e.g., "T-Alpha"
    "equipment_assigned": list[dict],  # What was actually assigned
    "shortfall": list[dict],   # Items that couldn't be allocated (if any)
    "allocated_at": str        # ISO 8601 format
}
```

**Example (Success):**
```json
{
    "request_id": "REQ-1704067500",
    "mission_id": "M-1704067500",
    "allocated": true,
    "team_id": "T-Alpha",
    "equipment_assigned": [
        {"item": "stretcher", "quantity": 3},
        {"item": "first_aid_kit", "quantity": 1},
        {"item": "hydraulic_cutter", "quantity": 1}
    ],
    "shortfall": [],
    "allocated_at": "2024-01-01T12:06:00Z"
}
```

**Example (Partial Allocation):**
```json
{
    "request_id": "REQ-1704067500",
    "mission_id": "M-1704067500",
    "allocated": true,
    "team_id": "T-Alpha",
    "equipment_assigned": [
        {"item": "stretcher", "quantity": 2},
        {"item": "first_aid_kit", "quantity": 1}
    ],
    "shortfall": [
        {"item": "stretcher", "quantity": 1, "reason": "insufficient_stock"},
        {"item": "hydraulic_cutter", "quantity": 1, "reason": "unavailable"}
    ],
    "allocated_at": "2024-01-01T12:06:00Z"
}
```

---

### Contract 4: Inventory Status

**Producer:** Resource Agent (Person A)  
**Consumer:** Rescue Agent (Person B), Master Agent (Person A)

```python
INVENTORY_STATUS = {
    "checked_at": str,         # ISO 8601 format
    "items": dict[str, dict]   # Equipment name → status
}

# Item status structure
ITEM_STATUS = {
    "available": int,          # Currently available
    "total": int,              # Total in inventory
    "reserved": int,           # Reserved for active missions
    "threshold": int,          # Low stock alert threshold
    "status": str              # ENUM: "ok" | "low" | "critical" | "out"
}
```

**Example:**
```json
{
    "checked_at": "2024-01-01T12:00:00Z",
    "items": {
        "stretcher": {
            "available": 8,
            "total": 15,
            "reserved": 7,
            "threshold": 5,
            "status": "ok"
        },
        "first_aid_kit": {
            "available": 3,
            "total": 20,
            "reserved": 17,
            "threshold": 5,
            "status": "low"
        }
    }
}
```

---

## 📋 Person A: Implementation Spec

### Files to Create

#### 1. `modules/master_tools/__init__.py`
```python
from .prioritizer import calculate_priority
from .location_utils import extract_location, validate_coordinates
from .victim_chat import create_victim_report

__all__ = [
    "calculate_priority",
    "extract_location", 
    "validate_coordinates",
    "create_victim_report"
]
```

#### 2. `modules/master_tools/prioritizer.py`

**Required Function Signature:**
```python
def calculate_priority(
    severity: str,
    num_people: int,
    has_injuries: bool,
    additional_factors: dict = None
) -> dict:
    """
    Args:
        severity: "CRITICAL" | "MODERATE" | "STABLE"
        num_people: Positive integer
        has_injuries: Boolean
        additional_factors: Optional dict with keys like "fire_hazard", "flooding", "structural_collapse"
    
    Returns:
        {
            "priority_score": int (0-100),
            "priority_level": str ("CRITICAL" | "HIGH" | "MEDIUM" | "LOW"),
            "reasoning": list[str],
            "calculated_at": str (ISO 8601)
        }
    """
    pass
```

**Scoring Rules (MUST follow):**
```
Severity:
  CRITICAL = 50 points
  MODERATE = 30 points
  STABLE = 10 points

People count:
  Each person = 4 points (max 20 points)

Injuries:
  has_injuries = True → +15 points

Additional factors (each +5 points):
  - fire_hazard
  - flooding
  - structural_collapse

Priority Level:
  score >= 70 → "CRITICAL"
  score >= 40 → "HIGH"
  score >= 20 → "MEDIUM"
  score < 20  → "LOW"
```

#### 3. `modules/master_tools/location_utils.py`

**Required Function Signatures:**
```python
def extract_location(user_input: str) -> dict:
    """
    Extract location from natural language input.
    
    Args:
        user_input: Raw text like "I'm at 123 Main St" or "near the old factory on 5th avenue"
    
    Returns:
        {
            "lat": float or None,
            "lng": float or None,
            "address": str,
            "confidence": str ("high" | "medium" | "low"),
            "raw_input": str
        }
    """
    pass

def validate_coordinates(lat: float, lng: float) -> bool:
    """
    Validate GPS coordinates are within valid range.
    
    Returns:
        True if valid (-90 <= lat <= 90 and -180 <= lng <= 180)
    """
    pass
```

#### 4. `modules/master_tools/victim_chat.py`

**Required Function Signature:**
```python
def create_victim_report(
    location: dict,
    severity: str,
    num_people: int,
    has_injuries: bool,
    conditions: list = None,
    priority_result: dict = None
) -> dict:
    """
    Create a standardized victim report following VICTIM_REPORT contract.
    
    Returns:
        Complete VICTIM_REPORT dict (see Contract 1)
    """
    pass
```

#### 5. `modules/resource_tools/__init__.py`
```python
from .inventory import check_inventory, get_item_status, send_alert
from .allocator import allocate_resources, release_resources

__all__ = [
    "check_inventory",
    "get_item_status", 
    "send_alert",
    "allocate_resources",
    "release_resources"
]
```

#### 6. `modules/resource_tools/inventory.py`

**Required Function Signatures:**
```python
# In-memory inventory (initialize with these values)
INITIAL_INVENTORY = {
    "stretcher": {"total": 15, "reserved": 0, "threshold": 5},
    "first_aid_kit": {"total": 30, "reserved": 0, "threshold": 10},
    "defibrillator": {"total": 5, "reserved": 0, "threshold": 2},
    "oxygen_tank": {"total": 10, "reserved": 0, "threshold": 3},
    "splints": {"total": 20, "reserved": 0, "threshold": 5},
    "pediatric_kit": {"total": 5, "reserved": 0, "threshold": 2},
    "wheelchair_stretcher": {"total": 3, "reserved": 0, "threshold": 1},
    "hydraulic_cutter": {"total": 4, "reserved": 0, "threshold": 2},
    "concrete_saw": {"total": 3, "reserved": 0, "threshold": 1},
    "airbag_lifter": {"total": 2, "reserved": 0, "threshold": 1},
    "flashlight": {"total": 50, "reserved": 0, "threshold": 15},
    "radio": {"total": 30, "reserved": 0, "threshold": 10},
    "rope": {"total": 20, "reserved": 0, "threshold": 5},
    "ladder": {"total": 8, "reserved": 0, "threshold": 3},
    "fire_extinguisher": {"total": 25, "reserved": 0, "threshold": 8},
    "breathing_apparatus": {"total": 12, "reserved": 0, "threshold": 4},
    "thermal_camera": {"total": 3, "reserved": 0, "threshold": 1},
    "life_jacket": {"total": 40, "reserved": 0, "threshold": 15},
    "inflatable_boat": {"total": 4, "reserved": 0, "threshold": 2},
    "water_pump": {"total": 6, "reserved": 0, "threshold": 2}
}

def check_inventory(item_type: str = None) -> dict:
    """
    Check inventory levels.
    
    Args:
        item_type: Specific item to check, or None for all items
    
    Returns:
        INVENTORY_STATUS dict (see Contract 4)
    """
    pass

def get_item_status(item_name: str) -> dict:
    """
    Get status of a single item.
    
    Returns:
        ITEM_STATUS dict or {"error": "Item not found"}
    """
    pass

def send_alert(item_name: str, alert_type: str, message: str) -> dict:
    """
    Send inventory alert.
    
    Args:
        item_name: Equipment name
        alert_type: "low_stock" | "critical" | "out_of_stock"
        message: Alert description
    
    Returns:
        {"alert_id": str, "sent": bool, "timestamp": str}
    """
    pass
```

#### 7. `modules/resource_tools/allocator.py`

**Required Function Signatures:**
```python
def allocate_resources(
    request_id: str,
    mission_id: str,
    equipment_list: list,
    team_id: str = None
) -> dict:
    """
    Allocate resources for a rescue mission.
    
    Args:
        request_id: From EQUIPMENT_REQUEST
        mission_id: From EQUIPMENT_REQUEST
        equipment_list: List of {"item": str, "quantity": int, "priority": str}
        team_id: Optional team assignment, auto-generate if None
    
    Returns:
        ALLOCATION_RESPONSE dict (see Contract 3)
    
    Behavior:
        - Check availability for each item
        - Allocate what's available
        - Track shortfall for unavailable items
        - Update inventory (increase reserved count)
        - Return partial allocation if some items unavailable
    """
    pass

def release_resources(mission_id: str) -> dict:
    """
    Release resources when mission completes.
    
    Returns:
        {"mission_id": str, "released": bool, "items_returned": list}
    """
    pass
```

#### 8. `configs/agents/master_agent.yaml`

```yaml
agent:
  name: master_agent
  description: >
    Communicates with disaster victims, extracts critical information
    (location, severity, number of people), and prioritizes rescue operations.
  
  agent_card:
    name: "Disaster Triage Master"
    description: "Primary agent for victim communication and rescue prioritization"
    capabilities:
      - victim_communication
      - severity_assessment
      - location_extraction
      - rescue_prioritization

  llm:
    provider: ${SAM_LLM_PROVIDER}
    model: ${SAM_LLM_MODEL}
    api_key: ${SAM_LLM_API_KEY}
    temperature: 0.3

  instructions: |
    You are the Master Disaster Rescue Agent. Your responsibilities:
    
    1. VICTIM COMMUNICATION:
       - Communicate calmly and empathetically with victims
       - Ask clear questions to gather: location, number of people, injuries, hazards
       - Provide reassurance while extracting details
    
    2. INFORMATION EXTRACTION:
       - Location: Get GPS coordinates or detailed address
       - Severity: Assess as CRITICAL, MODERATE, or STABLE
       - Headcount: Number of people needing rescue
       - Conditions: Injuries, fire, flood, collapse hazards
    
    3. PRIORITIZATION (use calculate_priority tool):
       - CRITICAL (70-100): Life-threatening, immediate danger
       - HIGH (40-69): Serious but not immediately life-threatening
       - MEDIUM (20-39): Needs attention but stable
       - LOW (0-19): Minor assistance needed
    
    4. HANDOFF:
       - After gathering info, create victim report
       - Delegate to Rescue Agent for team assignment
    
    Always maintain calm, professional tone in crisis situations.

  tools:
    - group_name: artifact_management
      tool_type: builtin-group
    
    - tool_type: python
      name: extract_location
      description: "Extract and validate location from victim input"
      module: modules.master_tools.location_utils
      function: extract_location
    
    - tool_type: python
      name: calculate_priority
      description: "Calculate victim priority score (0-100) based on severity factors"
      module: modules.master_tools.prioritizer
      function: calculate_priority
      parameters:
        - name: severity
          type: string
          description: "CRITICAL, MODERATE, or STABLE"
          required: true
        - name: num_people
          type: integer
          description: "Number of people affected"
          required: true
        - name: has_injuries
          type: boolean
          description: "Whether injuries are reported"
          required: true
        - name: additional_factors
          type: object
          description: "Optional: {fire_hazard: bool, flooding: bool, structural_collapse: bool}"
          required: false
    
    - tool_type: python
      name: create_victim_report
      description: "Create standardized victim report for rescue team handoff"
      module: modules.master_tools.victim_chat
      function: create_victim_report
```

#### 9. `configs/agents/resource_agent.yaml`

```yaml
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
    temperature: 0.1

  instructions: |
    You are the Resource Management Agent. Your responsibilities:
    
    1. INVENTORY MANAGEMENT:
       - Track all equipment (stretchers, tools, vehicles, medical supplies)
       - Monitor stock levels and alert when low
       - Maintain accurate counts after allocations
    
    2. RESOURCE ALLOCATION:
       - Process equipment requests from Rescue Agent
       - Check availability before confirming
       - Allocate available items, report shortfalls
       - Reserve resources for confirmed missions
    
    3. ALERTS:
       - Alert when equipment falls below threshold
       - Escalate critical shortages immediately
    
    Always confirm availability before allocation.
    Provide partial allocation if full request cannot be met.

  tools:
    - group_name: artifact_management
      tool_type: builtin-group
    
    - tool_type: python
      name: check_inventory
      description: "Check current inventory levels for all or specific equipment"
      module: modules.resource_tools.inventory
      function: check_inventory
    
    - tool_type: python
      name: allocate_resources
      description: "Allocate equipment to a rescue mission"
      module: modules.resource_tools.allocator
      function: allocate_resources
    
    - tool_type: python
      name: send_alert
      description: "Send low-stock or critical inventory alert"
      module: modules.resource_tools.inventory
      function: send_alert
    
    - tool_type: python
      name: release_resources
      description: "Release resources when mission completes"
      module: modules.resource_tools.allocator
      function: release_resources
```

---

## 📋 Person B: Implementation Spec

### Files to Create

#### 1. `modules/rescue_tools/__init__.py`
```python
from .tools_calculator import calculate_equipment
from .personnel_calc import calculate_personnel
from .navigation import get_route, estimate_arrival_time

__all__ = [
    "calculate_equipment",
    "calculate_personnel",
    "get_route",
    "estimate_arrival_time"
]
```

#### 2. `modules/rescue_tools/tools_calculator.py`

**Required Function Signature:**
```python
# Equipment templates - MUST use these exact mappings
EQUIPMENT_TEMPLATES = {
    "building_collapse": {
        "required": ["stretcher", "first_aid_kit", "flashlight", "radio"],
        "optional": ["hydraulic_cutter", "concrete_saw", "airbag_lifter"],
        "personnel_base": 4
    },
    "flood": {
        "required": ["life_jacket", "rope", "stretcher", "first_aid_kit"],
        "optional": ["inflatable_boat", "water_pump"],
        "personnel_base": 3
    },
    "fire": {
        "required": ["fire_extinguisher", "breathing_apparatus", "first_aid_kit"],
        "optional": ["thermal_camera", "ladder"],
        "personnel_base": 4
    },
    "medical": {
        "required": ["stretcher", "first_aid_kit", "defibrillator"],
        "optional": ["oxygen_tank", "splints"],
        "personnel_base": 2
    },
    "general": {
        "required": ["first_aid_kit", "flashlight", "radio", "stretcher"],
        "optional": [],
        "personnel_base": 2
    }
}

def calculate_equipment(
    scenario_type: str,
    num_victims: int,
    severity: str,
    special_conditions: list = None
) -> dict:
    """
    Calculate required equipment based on rescue scenario.
    
    Args:
        scenario_type: "building_collapse" | "flood" | "fire" | "medical" | "general"
        num_victims: Number of victims
        severity: "CRITICAL" | "MODERATE" | "STABLE"
        special_conditions: Optional list like ["elderly", "children", "disabled"]
    
    Returns:
        {
            "equipment": [
                {"item": str, "quantity": int, "priority": "required"|"recommended"}
            ],
            "personnel_required": int,
            "scenario_type": str,
            "notes": str
        }
    
    Quantity Rules:
        - stretcher: 1 per victim
        - first_aid_kit: 1 per 3 victims (round up)
        - other items: 1 each
        
    Personnel Rules:
        - Start with personnel_base from template
        - Add 1 for every 2 victims over 3
        - Add 2 if severity is CRITICAL
        
    Special Conditions:
        - "elderly" or "disabled": add wheelchair_stretcher
        - "children": add pediatric_kit
    """
    pass
```

#### 3. `modules/rescue_tools/personnel_calc.py`

**Required Function Signature:**
```python
def calculate_personnel(
    scenario_type: str,
    num_victims: int,
    severity: str,
    equipment_count: int = 0
) -> dict:
    """
    Calculate minimum personnel for rescue operation.
    
    Args:
        scenario_type: Type of disaster
        num_victims: Number of victims
        severity: Severity level
        equipment_count: Number of heavy equipment items
    
    Returns:
        {
            "minimum_personnel": int,
            "recommended_personnel": int,
            "breakdown": {
                "base": int,
                "victim_ratio": int,
                "severity_bonus": int,
                "equipment_operators": int
            },
            "roles": [
                {"role": str, "count": int}
            ]
        }
    
    Calculation:
        - Base: from EQUIPMENT_TEMPLATES[scenario_type]["personnel_base"]
        - Victim ratio: +1 per 2 victims over 3
        - Severity bonus: +2 if CRITICAL, +1 if MODERATE
        - Equipment operators: +1 per 2 heavy equipment items
        
    Roles (distribute personnel):
        - "team_leader": 1
        - "medic": 1 per 3 victims (min 1)
        - "rescuer": remaining personnel
    """
    pass
```

#### 4. `modules/rescue_tools/navigation.py`

**Required Function Signatures:**
```python
def get_route(
    origin: dict,
    destination: dict,
    avoid_hazards: list = None
) -> dict:
    """
    Get optimal route to victim location.
    
    Args:
        origin: {"lat": float, "lng": float} - rescue team location
        destination: {"lat": float, "lng": float} - victim location
        avoid_hazards: Optional list of hazard types to avoid routes through
    
    Returns:
        {
            "route_id": str,
            "origin": dict,
            "destination": dict,
            "distance_km": float,
            "estimated_time_minutes": int,
            "directions": [
                {"step": int, "instruction": str, "distance_m": int}
            ],
            "hazards_avoided": list,
            "calculated_at": str
        }
    
    Note: For hackathon, can use mock data / simple distance calculation.
    Real implementation would call Google Maps / OpenStreetMap API.
    """
    pass

def estimate_arrival_time(
    distance_km: float,
    traffic_level: str = "normal"
) -> dict:
    """
    Estimate arrival time based on distance and traffic.
    
    Args:
        distance_km: Distance in kilometers
        traffic_level: "light" | "normal" | "heavy"
    
    Returns:
        {
            "estimated_minutes": int,
            "traffic_level": str,
            "speed_kmh": int
        }
    
    Speed assumptions:
        - light: 60 km/h
        - normal: 40 km/h
        - heavy: 20 km/h
    """
    pass
```

#### 5. `configs/agents/rescue_agent.yaml`

```yaml
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
    
    1. RECEIVE VICTIM REPORTS:
       - Accept victim reports from Master Agent
       - Parse location, severity, and victim count
    
    2. CALCULATE REQUIREMENTS:
       - Determine scenario type (building_collapse, flood, fire, medical, general)
       - Calculate equipment needed using calculate_equipment tool
       - Calculate personnel using calculate_personnel tool
    
    3. REQUEST RESOURCES:
       - Send equipment request to Resource Agent
       - Handle partial allocations gracefully
    
    4. COORDINATE DEPLOYMENT:
       - Generate route to victim location
       - Assign team and equipment
       - Provide deployment instructions
    
    Always prioritize CRITICAL victims.
    Confirm resource availability before finalizing assignments.

  tools:
    - group_name: artifact_management
      tool_type: builtin-group
    
    - tool_type: python
      name: calculate_equipment
      description: "Calculate required equipment based on rescue scenario"
      module: modules.rescue_tools.tools_calculator
      function: calculate_equipment
      parameters:
        - name: scenario_type
          type: string
          description: "building_collapse, flood, fire, medical, or general"
          required: true
        - name: num_victims
          type: integer
          description: "Number of victims"
          required: true
        - name: severity
          type: string
          description: "CRITICAL, MODERATE, or STABLE"
          required: true
        - name: special_conditions
          type: array
          description: "Optional: elderly, children, disabled"
          required: false
    
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

#### 6. `configs/gateways/rest_gateway.yaml`

```yaml
gateway:
  name: rest_gateway
  type: rest
  port: 5050
  
  cors:
    enabled: true
    origins: ["*"]
    methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    headers: ["Content-Type", "Authorization"]
  
  endpoints:
    # Victim Reporting
    - path: /api/victim/report
      method: POST
      description: "Submit a new victim report"
      agent: master_agent
    
    - path: /api/victim/{victim_id}
      method: GET
      description: "Get victim status by ID"
      agent: master_agent
    
    # Rescue Operations
    - path: /api/rescue/mission/{mission_id}
      method: GET
      description: "Get mission details"
      agent: rescue_agent
    
    - path: /api/rescue/calculate
      method: POST
      description: "Calculate equipment and personnel for scenario"
      agent: rescue_agent
    
    # Resource Management
    - path: /api/resource/inventory
      method: GET
      description: "Get current inventory status"
      agent: resource_agent
    
    - path: /api/resource/allocate
      method: POST
      description: "Allocate resources to mission"
      agent: resource_agent
    
    # Health Check
    - path: /api/health
      method: GET
      description: "System health check"
      response:
        status: "ok"
        timestamp: "${TIMESTAMP}"
```

---

## 🧪 Testing Checkpoints

### Hour 3 Checkpoint (Individual Testing)

**Person A - Test Master Agent:**
```bash
# Terminal 1: Run just master agent
cd sam-project
sam run configs/agents/master_agent.yaml

# Terminal 2: Test priority calculation
curl -X POST http://localhost:5050/api/test \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Calculate priority for 3 people, CRITICAL severity, with injuries"
  }'
```

Expected output should include `priority_score` between 70-100.

**Person B - Test Rescue Agent:**
```bash
# Terminal 1: Run just rescue agent
cd sam-project
sam run configs/agents/rescue_agent.yaml

# Terminal 2: Test equipment calculation
curl -X POST http://localhost:5050/api/test \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Calculate equipment for building collapse, 3 victims, CRITICAL"
  }'
```

Expected output should include `stretcher: 3`, `first_aid_kit: 1`.

---

### Hour 7 Checkpoint (Integration Testing)

**Run all agents together:**
```bash
docker-compose up -d
sam run -b
```

**Test full flow in Web UI (http://localhost:8000):**

```
User: "There's been a building collapse at 123 Main Street. 
       3 people are trapped, one is seriously injured. 
       There's smoke coming from the building."
```

**Expected flow:**
1. Master Agent extracts: location, 3 people, injuries, fire_hazard
2. Master Agent calculates priority: should be CRITICAL (70+)
3. Rescue Agent calculates: building_collapse scenario, ~6 personnel
4. Resource Agent allocates: stretchers, first_aid_kits, etc.

---

### Hour 10 Checkpoint (API Testing)

**Test REST endpoints:**

```bash
# 1. Submit victim report
curl -X POST http://localhost:5050/api/victim/report \
  -H "Content-Type: application/json" \
  -d '{
    "message": "5 people trapped in flooding at riverside park, 2 children"
  }'

# 2. Check inventory
curl http://localhost:5050/api/resource/inventory

# 3. Calculate rescue requirements
curl -X POST http://localhost:5050/api/rescue/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_type": "flood",
    "num_victims": 5,
    "severity": "CRITICAL",
    "special_conditions": ["children"]
  }'
```

---

## ⚠️ Common Integration Errors & How to Avoid

### Error 1: Enum Mismatch
```
❌ severity: "critical"
✅ severity: "CRITICAL"
```
**Rule:** All enums are UPPERCASE

### Error 2: Missing Required Fields
```
❌ {"victim_id": "V-001", "severity": "CRITICAL"}
✅ {"victim_id": "V-001", "severity": "CRITICAL", "num_people": 1, ...}
```
**Rule:** Always include ALL required fields from contracts

### Error 3: Wrong Equipment Names
```
❌ "first-aid-kit"
❌ "FirstAidKit"  
✅ "first_aid_kit"
```
**Rule:** Use EXACT names from VALID_EQUIPMENT list (snake_case)

### Error 4: ID Format Mismatch
```
❌ victim_id: "001"
❌ victim_id: "victim-001"
✅ victim_id: "V-1704067200"
```
**Rule:** Follow ID formats: `V-{timestamp}`, `M-{timestamp}`, `REQ-{timestamp}`, `T-{name}`

### Error 5: Timestamp Format
```
❌ "2024-01-01 12:00:00"
❌ "Jan 1, 2024"
✅ "2024-01-01T12:00:00Z"
```
**Rule:** Always use ISO 8601 format with Z suffix

---

## 🔄 Git Workflow

### Branch Strategy
```
main
├── feature/person-a-master-agent
├── feature/person-a-resource-agent
├── feature/person-b-rescue-agent
└── feature/person-b-gateway
```

### Commit Convention
```
[Person A] Add master agent priority calculator
[Person B] Add rescue equipment calculator
[SYNC] Merge integration fixes
```

### Merge Points
- **Hour 6:** First merge to main
- **Hour 9:** Second merge after testing
- **Hour 11:** Final merge for demo

---

## 🆘 Quick Fixes

### SAM Won't Start
```bash
# Check Python version
python3 --version  # Need 3.10.16+

# Reinstall SAM
pip uninstall solace-agent-mesh
pip install solace-agent-mesh
```

### Docker Issues
```bash
# Reset everything
docker-compose down -v
docker-compose up -d --build
```

### Agent Not Responding
```bash
# Check logs
docker-compose logs -f sam

# Verify agent loaded
sam list agents
```

### Import Errors
```bash
# Make sure __init__.py exists in all module folders
touch modules/__init__.py
touch modules/master_tools/__init__.py
touch modules/rescue_tools/__init__.py
touch modules/resource_tools/__init__.py
```

---

## ✅ Final Checklist Before Demo

| Item | Person A | Person B |
|------|----------|----------|
| All functions return correct contract format | ☐ | ☐ |
| All enums are UPPERCASE | ☐ | ☐ |
| All timestamps are ISO 8601 | ☐ | ☐ |
| All IDs follow format conventions | ☐ | ☐ |
| Equipment names match VALID_EQUIPMENT | ☐ | ☐ |
| Agent YAML loads without errors | ☐ | ☐ |
| Tools callable from Web UI | ☐ | ☐ |
| Full flow works end-to-end | ☐ | ☐ |

---

## 📞 Sync Points Summary

| Hour | Action |
|------|--------|
| 0 | Read this doc together, agree on any questions |
| 3 | Quick check: "My agent loads, does yours?" |
| 6 | Git merge, test each other's agents |
| 9 | Full integration test together |
| 11 | Demo prep together |

---

**Good luck! 🚀 Build fast, integrate clean.**
