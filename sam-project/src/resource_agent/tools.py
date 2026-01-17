"""
Resources Agent - Tools for estimating disaster relief resources needed.

This agent analyzes victim descriptions and estimates what supplies
and resources are needed for rescue and relief operations.
"""

from typing import Any, Dict, Optional
from google.adk.tools import ToolContext
from solace_ai_connector.common.log import log


async def estimate_resources(
    description: str,
    victim_id: str,
    num_people: int = 1,
    tool_context: Optional[ToolContext] = None,
    tool_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Estimate resource needs based on victim situation description.
    
    Analyzes the description to determine what supplies are needed:
    - Food and water
    - Medical supplies
    - Shelter/blankets
    - Emergency equipment
    
    Args:
        description: Description of the situation
        victim_id: Unique identifier for the victim/group
        num_people: Number of people affected (default: 1)
        tool_context: Tool invocation context (provided by SAM)
        tool_config: Tool configuration (from YAML)
        
    Returns:
        Dictionary with resource needs categorized by type and priority
    """
    log_identifier = "[ResourceEstimation]"
    log.info(f"{log_identifier} Estimating resources for victim {victim_id} ({num_people} people)")
    
    if not description or len(description.strip()) < 5:
        return {
            "status": "error",
            "victim_id": victim_id,
            "message": "Description too short for resource estimation"
        }
    
    try:
        lower_desc = description.lower()
        
        # Initialize resource needs
        resources = {
            "food": {"priority": "LOW", "quantity": 0},
            "water": {"priority": "LOW", "quantity": 0},
            "medical_supplies": {"priority": "LOW", "items": []},
            "blankets": {"priority": "LOW", "quantity": 0},
            "shelter": {"priority": "LOW", "type": None},
            "emergency_equipment": {"priority": "LOW", "items": []}
        }
        
        # FOOD ASSESSMENT
        food_keywords = ['hungry', 'starving', 'no food', 'haven\'t eaten', 'food shortage']
        if any(kw in lower_desc for kw in food_keywords):
            resources["food"]["priority"] = "HIGH"
            resources["food"]["quantity"] = num_people * 3  # 3 meals per person
        elif 'food' in lower_desc:
            resources["food"]["priority"] = "MEDIUM"
            resources["food"]["quantity"] = num_people * 2
        else:
            resources["food"]["priority"] = "LOW"
            resources["food"]["quantity"] = num_people
        
        # WATER ASSESSMENT
        water_keywords = ['thirsty', 'dehydrated', 'no water', 'water shortage', 'dry']
        if any(kw in lower_desc for kw in water_keywords):
            resources["water"]["priority"] = "HIGH"
            resources["water"]["quantity"] = num_people * 4  # 4 liters per person
        elif 'water' in lower_desc:
            resources["water"]["priority"] = "MEDIUM"
            resources["water"]["quantity"] = num_people * 2
        else:
            resources["water"]["priority"] = "LOW"
            resources["water"]["quantity"] = num_people
        
        # MEDICAL SUPPLIES ASSESSMENT
        medical_items = []
        
        if any(word in lower_desc for word in ['bleeding', 'blood', 'cut', 'laceration']):
            medical_items.extend(['bandages', 'gauze', 'antiseptic'])
            resources["medical_supplies"]["priority"] = "HIGH"
        
        if any(word in lower_desc for word in ['broken', 'fracture', 'sprain']):
            medical_items.extend(['splints', 'elastic bandages'])
            resources["medical_supplies"]["priority"] = "HIGH"
        
        if any(word in lower_desc for word in ['burn', 'burned', 'burning']):
            medical_items.extend(['burn dressings', 'antibiotic ointment'])
            resources["medical_supplies"]["priority"] = "HIGH"
        
        if any(word in lower_desc for word in ['pain', 'hurt', 'aching']):
            medical_items.append('pain medication')
            if resources["medical_supplies"]["priority"] == "LOW":
                resources["medical_supplies"]["priority"] = "MEDIUM"
        
        if any(word in lower_desc for word in ['unconscious', 'not breathing', 'cardiac']):
            medical_items.extend(['AED', 'oxygen', 'IV fluids'])
            resources["medical_supplies"]["priority"] = "CRITICAL"
        
        if any(word in lower_desc for word in ['diabetes', 'insulin']):
            medical_items.append('insulin')
            resources["medical_supplies"]["priority"] = "HIGH"
        
        resources["medical_supplies"]["items"] = list(set(medical_items))  # Remove duplicates
        
        # BLANKETS/WARMTH ASSESSMENT
        cold_keywords = ['cold', 'freezing', 'hypothermia', 'shivering', 'wet']
        if any(kw in lower_desc for kw in cold_keywords):
            resources["blankets"]["priority"] = "HIGH"
            resources["blankets"]["quantity"] = num_people * 2
        else:
            resources["blankets"]["priority"] = "LOW"
            resources["blankets"]["quantity"] = num_people
        
        # SHELTER ASSESSMENT
        shelter_keywords = ['homeless', 'destroyed', 'no shelter', 'collapsed', 'rubble']
        if any(kw in lower_desc for kw in shelter_keywords):
            resources["shelter"]["priority"] = "HIGH"
            resources["shelter"]["type"] = "emergency tent"
        elif any(word in lower_desc for word in ['rain', 'storm', 'wind']):
            resources["shelter"]["priority"] = "MEDIUM"
            resources["shelter"]["type"] = "temporary shelter"
        
        # EMERGENCY EQUIPMENT ASSESSMENT
        equipment_items = []
        
        if any(word in lower_desc for word in ['trapped', 'stuck', 'rubble', 'debris']):
            equipment_items.extend(['hydraulic tools', 'cutting equipment', 'search and rescue gear'])
            resources["emergency_equipment"]["priority"] = "CRITICAL"
        
        if any(word in lower_desc for word in ['fire', 'smoke', 'burning']):
            equipment_items.extend(['fire extinguisher', 'breathing apparatus'])
            resources["emergency_equipment"]["priority"] = "HIGH"
        
        if any(word in lower_desc for word in ['flood', 'water', 'drowning']):
            equipment_items.extend(['life vests', 'boats', 'water pumps'])
            resources["emergency_equipment"]["priority"] = "HIGH"
        
        if any(word in lower_desc for word in ['dark', 'night', 'can\'t see']):
            equipment_items.append('flashlights')
        
        resources["emergency_equipment"]["items"] = list(set(equipment_items))
        
        # Generate summary
        high_priority = [k for k, v in resources.items() if v.get("priority") in ["HIGH", "CRITICAL"]]
        
        summary = f"Resource needs for {num_people} person(s): "
        if high_priority:
            summary += f"High priority: {', '.join(high_priority)}"
        else:
            summary += "Basic supplies needed"
        
        result = {
            "status": "success",
            "victim_id": victim_id,
            "num_people": num_people,
            "resources": resources,
            "summary": summary,
            "high_priority_items": high_priority
        }
        
        log.info(f"{log_identifier} Estimation complete for victim {victim_id}: {len(high_priority)} high priority categories")
        return result
        
    except Exception as e:
        log.error(f"{log_identifier} Error estimating resources: {e}")
        return {
            "status": "error",
            "victim_id": victim_id,
            "message": f"Resource estimation failed: {str(e)}"
        }