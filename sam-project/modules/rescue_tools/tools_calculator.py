"""
Equipment Calculator for Rescue Agent

Calculates required equipment based on rescue scenario type.
"""

import math
from typing import Dict, Any, List, Optional


# Equipment templates - MUST use these exact mappings (from TEAM-COORDINATION-README)
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
    special_conditions: Optional[List[str]] = None
) -> Dict[str, Any]:
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
    # Normalize inputs
    scenario_type = scenario_type.lower()
    severity = severity.upper()
    special_conditions = special_conditions or []
    num_victims = max(1, int(num_victims))
    
    # Get template (default to "general" if unknown)
    template = EQUIPMENT_TEMPLATES.get(scenario_type, EQUIPMENT_TEMPLATES["general"])
    
    equipment: List[Dict[str, Any]] = []
    
    # Add required equipment with calculated quantities
    for item in template["required"]:
        quantity = _calculate_quantity(item, num_victims)
        equipment.append({
            "item": item,
            "quantity": quantity,
            "priority": "required"
        })
    
    # Add optional equipment based on severity
    if severity in ["CRITICAL", "MODERATE"]:
        for item in template["optional"]:
            equipment.append({
                "item": item,
                "quantity": 1,
                "priority": "recommended"
            })
    
    # Handle special conditions
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
    personnel_required = _calculate_personnel(
        template["personnel_base"],
        num_victims,
        severity
    )
    
    # Build notes
    notes = f"Equipment calculated for {num_victims} victim(s), {severity} severity, {scenario_type} scenario"
    if special_conditions:
        notes += f". Special conditions: {', '.join(special_conditions)}"
    
    return {
        "equipment": equipment,
        "personnel_required": personnel_required,
        "scenario_type": scenario_type,
        "notes": notes
    }


def _calculate_quantity(item: str, num_victims: int) -> int:
    """Calculate quantity based on item type and victim count."""
    if item == "stretcher":
        # 1 per victim
        return num_victims
    elif item == "first_aid_kit":
        # 1 per 3 victims (round up)
        return math.ceil(num_victims / 3)
    elif item == "life_jacket":
        # 1 per victim for flood scenarios
        return num_victims
    else:
        # Default: 1 each
        return 1


def _calculate_personnel(base: int, num_victims: int, severity: str) -> int:
    """
    Calculate personnel requirements.
    
    Rules:
        - Start with personnel_base from template
        - Add 1 for every 2 victims over 3
        - Add 2 if severity is CRITICAL
    """
    personnel = base
    
    # Add for victim count over 3
    if num_victims > 3:
        personnel += (num_victims - 3) // 2
    
    # Add for severity
    if severity == "CRITICAL":
        personnel += 2
    elif severity == "MODERATE":
        personnel += 1
    
    return personnel


def get_scenario_types() -> List[str]:
    """Return list of valid scenario types."""
    return list(EQUIPMENT_TEMPLATES.keys())


# Test function
if __name__ == "__main__":
    print("=" * 60)
    print("TESTING TOOLS CALCULATOR")
    print("=" * 60)
    
    # Test 1: Building collapse scenario
    print("\nTest 1: Building collapse, 3 victims, CRITICAL")
    result = calculate_equipment(
        scenario_type="building_collapse",
        num_victims=3,
        severity="CRITICAL"
    )
    print(f"  Scenario: {result['scenario_type']}")
    print(f"  Personnel Required: {result['personnel_required']}")
    print(f"  Equipment:")
    for item in result['equipment']:
        print(f"    - {item['item']}: {item['quantity']} ({item['priority']})")
    
    # Verify: stretcher=3, first_aid_kit=1, personnel=4+0+2=6
    stretchers = next(e for e in result['equipment'] if e['item'] == 'stretcher')
    first_aid = next(e for e in result['equipment'] if e['item'] == 'first_aid_kit')
    assert stretchers['quantity'] == 3, "Test 1 FAILED: stretchers"
    assert first_aid['quantity'] == 1, "Test 1 FAILED: first_aid_kit"
    assert result['personnel_required'] == 6, f"Test 1 FAILED: personnel expected 6, got {result['personnel_required']}"
    print("  ✅ PASSED")
    
    # Test 2: Flood scenario with children
    print("\nTest 2: Flood, 5 victims, MODERATE, with children")
    result = calculate_equipment(
        scenario_type="flood",
        num_victims=5,
        severity="MODERATE",
        special_conditions=["children"]
    )
    print(f"  Personnel Required: {result['personnel_required']}")
    print(f"  Equipment count: {len(result['equipment'])}")
    
    # Check pediatric_kit was added
    has_pediatric = any(e['item'] == 'pediatric_kit' for e in result['equipment'])
    assert has_pediatric, "Test 2 FAILED: should have pediatric_kit"
    # Life jackets should equal num_victims
    life_jackets = next(e for e in result['equipment'] if e['item'] == 'life_jacket')
    assert life_jackets['quantity'] == 5, "Test 2 FAILED: life_jackets"
    # Personnel: base 3 + 1 (5 victims over 3) + 1 (MODERATE) = 5
    assert result['personnel_required'] == 5, f"Test 2 FAILED: personnel expected 5, got {result['personnel_required']}"
    print("  ✅ PASSED")
    
    # Test 3: Medical scenario
    print("\nTest 3: Medical, 2 victims, STABLE")
    result = calculate_equipment(
        scenario_type="medical",
        num_victims=2,
        severity="STABLE"
    )
    print(f"  Personnel Required: {result['personnel_required']}")
    
    # STABLE severity = no optional equipment
    optional_count = len([e for e in result['equipment'] if e['priority'] == 'recommended'])
    assert optional_count == 0, "Test 3 FAILED: should have no optional equipment for STABLE"
    # Personnel: base 2 + 0 + 0 = 2
    assert result['personnel_required'] == 2, "Test 3 FAILED: personnel"
    print("  ✅ PASSED")
    
    # Test 4: Fire scenario with elderly
    print("\nTest 4: Fire, 4 victims, CRITICAL, with elderly")
    result = calculate_equipment(
        scenario_type="fire",
        num_victims=4,
        severity="CRITICAL",
        special_conditions=["elderly"]
    )
    
    # Check wheelchair_stretcher was added
    has_wheelchair = any(e['item'] == 'wheelchair_stretcher' for e in result['equipment'])
    assert has_wheelchair, "Test 4 FAILED: should have wheelchair_stretcher"
    # Personnel: base 4 + 0 (4 victims, only 1 over 3 = 0) + 2 (CRITICAL) = 6
    # Wait: (4-3)//2 = 0, so 4+0+2=6
    assert result['personnel_required'] == 6, f"Test 4 FAILED: personnel expected 6, got {result['personnel_required']}"
    print("  ✅ PASSED")
    
    # Test 5: Unknown scenario defaults to general
    print("\nTest 5: Unknown scenario defaults to 'general'")
    result = calculate_equipment(
        scenario_type="unknown_disaster",
        num_victims=2,
        severity="MODERATE"
    )
    assert result['scenario_type'] == "unknown_disaster", "Test 5 FAILED"
    # Should have general equipment
    has_flashlight = any(e['item'] == 'flashlight' for e in result['equipment'])
    assert has_flashlight, "Test 5 FAILED: should have flashlight from general template"
    print("  ✅ PASSED")
    
    # Test 6: Large victim count
    print("\nTest 6: Building collapse, 10 victims, CRITICAL")
    result = calculate_equipment(
        scenario_type="building_collapse",
        num_victims=10,
        severity="CRITICAL"
    )
    stretchers = next(e for e in result['equipment'] if e['item'] == 'stretcher')
    first_aid = next(e for e in result['equipment'] if e['item'] == 'first_aid_kit')
    print(f"  Stretchers: {stretchers['quantity']} (expected: 10)")
    print(f"  First Aid Kits: {first_aid['quantity']} (expected: 4)")
    print(f"  Personnel: {result['personnel_required']} (expected: 9)")
    
    assert stretchers['quantity'] == 10, "Test 6 FAILED: stretchers"
    assert first_aid['quantity'] == 4, "Test 6 FAILED: first_aid_kit (ceil(10/3)=4)"
    # Personnel: base 4 + 3 ((10-3)//2=3) + 2 (CRITICAL) = 9
    assert result['personnel_required'] == 9, f"Test 6 FAILED: personnel expected 9, got {result['personnel_required']}"
    print("  ✅ PASSED")
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! ✅")
    print("=" * 60)