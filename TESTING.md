# 🚨 Disaster Rescue Coordination System

An AI-powered multi-agent disaster rescue platform built with **Solace Agent Mesh (SAM)**.

---

## 👥 Team Implementation Status

| Role | Components | Status |
|------|------------|--------|
| **Person A** | Master Agent, Resource Agent | ✅ Complete |
| **Person B** | Rescue Agent, REST Gateway | 🔄 In Progress |

---

## 📁 Project Structure
```
sam-project/
├── configs/
│   └── agents/
│       ├── master_agent.yaml      # Person A ✅
│       ├── resource_agent.yaml    # Person A ✅
│       └── rescue_agent.yaml      # Person B
├── modules/
│   ├── master_tools/              # Person A ✅
│   │   ├── __init__.py
│   │   ├── prioritizer.py
│   │   ├── location_utils.py
│   │   └── victim_chat.py
│   ├── resource_tools/            # Person A ✅
│   │   ├── __init__.py
│   │   ├── inventory.py
│   │   └── allocator.py
│   └── rescue_tools/              # Person B
│       └── __init__.py
├── tests/
│   └── test_integration.py        # Person A ✅
├── .env.example
└── README.md
```

---

## 🧪 Testing Instructions

### Prerequisites
```bash
# Navigate to project
cd /Users/chrisv/Documents/Disaster-Agent/sam-project

# Activate virtual environment
source .venv/bin/activate

# Verify Python version (requires 3.10+)
python --version
```

---

### Run Individual Module Tests

Each module has built-in tests. Run from the module's directory:

#### 1. Test Priority Calculator
```bash
cd modules/master_tools
python prioritizer.py
```
**Expected:** 5 tests pass (scoring for CRITICAL, MODERATE, STABLE, HIGH, max cap)

#### 2. Test Location Utilities
```bash
cd modules/master_tools
python location_utils.py
```
**Expected:** 6 tests pass (GPS extraction, address parsing, validation)

#### 3. Test Victim Chat
```bash
cd modules/master_tools
python victim_chat.py
```
**Expected:** 5 tests pass (report creation, message parsing, ID/timestamp formats)

#### 4. Test Inventory Management
```bash
cd modules/resource_tools
python inventory.py
```
**Expected:** 9 tests pass (check inventory, reserve, release, alerts)

#### 5. Test Resource Allocator
```bash
cd modules/resource_tools
python allocator.py
```
**Expected:** 8 tests pass (allocation, partial allocation, team assignment, release)

---

### Run Full Integration Test

Tests the complete workflow from victim message to resource allocation:
```bash
cd /Users/chrisv/Documents/Disaster-Agent/sam-project
python tests/test_integration.py
```

**Expected Output:**
```
======================================================================
INTEGRATION TEST: Full Disaster Rescue Workflow
======================================================================

STEP 1: Victim Emergency Message
✅ Message parsing PASSED

STEP 2: Extract Location
✅ Location extraction PASSED

STEP 3: Calculate Priority
✅ Priority calculation PASSED

STEP 4: Create Victim Report
✅ Victim report creation PASSED

STEP 5: Check Inventory Before Allocation
✅ Inventory check PASSED

STEP 6: Allocate Resources
✅ Resource allocation PASSED

STEP 7: Verify Inventory After Allocation
✅ Inventory update PASSED

STEP 8: Release Resources (Mission Complete)
✅ Resource release PASSED

======================================================================
🎉 ALL INTEGRATION TESTS PASSED! 🎉
======================================================================
```

---

### Run All Tests (Quick Command)
```bash
cd /Users/chrisv/Documents/Disaster-Agent/sam-project

# Run all module tests
python modules/master_tools/prioritizer.py && \
python modules/master_tools/location_utils.py && \
python modules/master_tools/victim_chat.py && \
python modules/resource_tools/inventory.py && \
python modules/resource_tools/allocator.py && \
python tests/test_integration.py

echo "✅ All tests completed!"
```

---

## 📋 Data Contracts Summary

All implementations follow the contracts in `TEAM-COORDINATION-README.md`:

| Contract | Producer | Consumer | Format |
|----------|----------|----------|--------|
| VICTIM_REPORT | Master Agent | Rescue Agent | `victim_id: "V-{timestamp}"` |
| EQUIPMENT_REQUEST | Rescue Agent | Resource Agent | `request_id: "REQ-{timestamp}"` |
| ALLOCATION_RESPONSE | Resource Agent | Rescue Agent | `mission_id: "M-{timestamp}"` |
| INVENTORY_STATUS | Resource Agent | All Agents | 20 equipment types |

### Key Rules
- ✅ Enums are **UPPERCASE**: `CRITICAL`, `MODERATE`, `STABLE`
- ✅ Timestamps are **ISO 8601**: `2024-01-01T12:00:00Z`
- ✅ Equipment names are **snake_case**: `first_aid_kit`, `hydraulic_cutter`

---

## 🚀 Next Steps

1. **Person B**: Implement Rescue Agent and REST Gateway
2. **Integration**: Test full agent-to-agent communication
3. **Docker**: Set up Solace broker for local testing
4. **Deploy**: Configure for production environment

---

## 📞 Quick Commands Reference
```bash
# Activate environment
cd /Users/chrisv/Documents/Disaster-Agent/sam-project && source .venv/bin/activate

# Run SAM (after Person B completes gateway)
sam run -b

# Git workflow
git status
git add .
git commit -m "message"
git push origin main
git pull origin main
```

---

## 👤 Person A Implementation Details

**Components Implemented:**
- `prioritizer.py`: Priority scoring (0-100) based on severity, people count, injuries, hazards
- `location_utils.py`: GPS extraction, address parsing, coordinate validation
- `victim_chat.py`: Standardized victim report creation, message parsing
- `inventory.py`: 20 equipment types, availability tracking, threshold alerts
- `allocator.py`: Resource allocation, partial fulfillment, team assignment

**All tests passing as of:** January 17, 2026