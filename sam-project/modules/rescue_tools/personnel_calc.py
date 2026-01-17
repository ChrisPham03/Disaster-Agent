"""
Personnel Calculator for Rescue Agent

Calculates minimum personnel requirements and role distribution.
"""

import math
from typing import Dict, Any, List, Optional

# Reference to equipment templates for base personnel
PERSONNEL_BASE = {
    "building_collapse": 4,
    "flood": 3,
    "fire": 4,
    "medical": 2,
    "general": 2
}


def calculate_personnel(
    scenario_type: str,
    num_victims: int,
    severity: str,
    equipment_count: int = 0
) -> Dict[str, Any]:
    """
    Calculate minimum personnel for rescue operation.
    
    Args:
        scenario_type: Type of disaster
        num_victims: Number of victims
        severity: Severity level (CRITICAL, MODERATE, STABLE)
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
        - Base: from PERSONNEL_BASE[scenario_type]
        - Victim ratio: +1 per 2 victims over 3
        - Severity bonus: +2 if CRITICAL, +1 if MODERATE
        - Equipment operators: +1 per 2 heavy equipment items
        
    Roles (distribute personnel):
        - "team_leader": 1
        - "medic": 1 per 3 victims (min 1)
        - "rescuer": remaining personnel
    """
    # Normalize inputs
    scenario_type = scenario_type.lower()
    severity = severity.upper()
    num_victims = max(1, int(num_victims))
    equipment_count = max(0, int(equipment_count))
    
    # Get base personnel
    base = PERSONNEL_BASE.get(scenario_type, PERSONNEL_BASE["general"])
    
    # Calculate victim ratio bonus
    victim_ratio = 0
    if num_victims > 3:
        victim_ratio = (num_victims - 3) // 2
    
    # Calculate severity bonus
    severity_bonus = 0
    if severity == "CRITICAL":
        severity_bonus = 2
    elif severity == "MODERATE":
        severity_bonus = 1
    
    # Calculate equipment operators
    equipment_operators = equipment_count // 2
    
    # Total minimum personnel
    minimum_personnel = base + victim_ratio + severity_bonus + equipment_operators
    
    # Recommended is minimum + 20% buffer (rounded up)
    recommended_personnel = math.ceil(minimum_personnel * 1.2)
    
    # Calculate role distribution
    roles = _distribute_roles(minimum_personnel, num_victims)
    
    return {
        "minimum_personnel": minimum_personnel,
        "recommended_personnel": recommended_personnel,
        "breakdown": {
            "base": base,
            "victim_ratio": victim_ratio,
            "severity_bonus": severity_bonus,
            "equipment_operators": equipment_operators
        },
        "roles": roles
    }


def _distribute_roles(total_personnel: int, num_victims: int) -> List[Dict[str, Any]]:
    """
    Distribute personnel into roles.
    
    Rules:
        - team_leader: 1 (always)
        - medic: 1 per 3 victims (min 1)
        - rescuer: remaining personnel
    """
    roles = []
    remaining = total_personnel
    
    # Team leader: always 1
    team_leaders = 1
    remaining -= team_leaders
    roles.append({"role": "team_leader", "count": team_leaders})
    
    # Medics: 1 per 3 victims, minimum 1
    medics = max(1, math.ceil(num_victims / 3))
    # Don't exceed remaining personnel
    medics = min(medics, remaining)
    remaining -= medics
    roles.append({"role": "medic", "count": medics})
    
    # Rescuers: everyone else
    rescuers = max(0, remaining)
    roles.append({"role": "rescuer", "count": rescuers})
    
    return roles


def get_role_descriptions() -> Dict[str, str]:
    """Return descriptions for each role."""
    return {
        "team_leader": "Coordinates rescue operation, communicates with command center",
        "medic": "Provides medical assessment and first aid to victims",
        "rescuer": "Performs physical rescue operations and equipment handling"
    }


# Test function
if __name__ == "__main__":
    print("=" * 60)
    print("TESTING PERSONNEL CALCULATOR")
    print("=" * 60)
    
    # Test 1: Building collapse, CRITICAL
    print("\nTest 1: Building collapse, 3 victims, CRITICAL")
    result = calculate_personnel(
        scenario_type="building_collapse",
        num_victims=3,
        severity="CRITICAL",
        equipment_count=0
    )
    print(f"  Minimum Personnel: {result['minimum_personnel']} (expected: 6)")
    print(f"  Recommended Personnel: {result['recommended_personnel']}")
    print(f"  Breakdown: {result['breakdown']}")
    print(f"  Roles:")
    for role in result['roles']:
        print(f"    - {role['role']}: {role['count']}")
    
    # base=4 + victim_ratio=0 + severity_bonus=2 + equipment=0 = 6
    assert result['minimum_personnel'] == 6, f"Test 1 FAILED: expected 6, got {result['minimum_personnel']}"
    assert result['breakdown']['base'] == 4, "Test 1 FAILED: base"
    assert result['breakdown']['severity_bonus'] == 2, "Test 1 FAILED: severity_bonus"
    print("  ✅ PASSED")
    
    # Test 2: Flood, MODERATE, with equipment
    print("\nTest 2: Flood, 5 victims, MODERATE, 4 equipment")
    result = calculate_personnel(
        scenario_type="flood",
        num_victims=5,
        severity="MODERATE",
        equipment_count=4
    )
    print(f"  Minimum Personnel: {result['minimum_personnel']} (expected: 7)")
    print(f"  Breakdown: {result['breakdown']}")
    
    # base=3 + victim_ratio=1 ((5-3)//2) + severity_bonus=1 + equipment=2 (4//2) = 7
    assert result['minimum_personnel'] == 7, f"Test 2 FAILED: expected 7, got {result['minimum_personnel']}"
    assert result['breakdown']['victim_ratio'] == 1, "Test 2 FAILED: victim_ratio"
    assert result['breakdown']['equipment_operators'] == 2, "Test 2 FAILED: equipment_operators"
    print("  ✅ PASSED")
    
    # Test 3: Medical, STABLE
    print("\nTest 3: Medical, 2 victims, STABLE")
    result = calculate_personnel(
        scenario_type="medical",
        num_victims=2,
        severity="STABLE",
        equipment_count=0
    )
    print(f"  Minimum Personnel: {result['minimum_personnel']} (expected: 2)")
    
    # base=2 + victim_ratio=0 + severity_bonus=0 + equipment=0 = 2
    assert result['minimum_personnel'] == 2, f"Test 3 FAILED: expected 2, got {result['minimum_personnel']}"
    assert result['breakdown']['severity_bonus'] == 0, "Test 3 FAILED: severity_bonus should be 0"
    print("  ✅ PASSED")
    
    # Test 4: Role distribution
    print("\nTest 4: Role distribution (6 personnel, 3 victims)")
    result = calculate_personnel(
        scenario_type="building_collapse",
        num_victims=3,
        severity="CRITICAL"
    )
    
    roles_dict = {r['role']: r['count'] for r in result['roles']}
    print(f"  Team Leaders: {roles_dict['team_leader']} (expected: 1)")
    print(f"  Medics: {roles_dict['medic']} (expected: 1)")
    print(f"  Rescuers: {roles_dict['rescuer']} (expected: 4)")
    
    # 6 personnel: 1 team_leader + 1 medic (ceil(3/3)=1) + 4 rescuers
    assert roles_dict['team_leader'] == 1, "Test 4 FAILED: team_leader"
    assert roles_dict['medic'] == 1, "Test 4 FAILED: medic"
    assert roles_dict['rescuer'] == 4, f"Test 4 FAILED: rescuer expected 4, got {roles_dict['rescuer']}"
    print("  ✅ PASSED")
    
    # Test 5: Large victim count role distribution
    print("\nTest 5: Role distribution (10 victims)")
    result = calculate_personnel(
        scenario_type="building_collapse",
        num_victims=10,
        severity="CRITICAL"
    )
    
    roles_dict = {r['role']: r['count'] for r in result['roles']}
    print(f"  Minimum Personnel: {result['minimum_personnel']} (expected: 9)")
    print(f"  Medics: {roles_dict['medic']} (expected: 4)")
    
    # base=4 + victim_ratio=3 ((10-3)//2) + severity=2 = 9
    # Medics: ceil(10/3) = 4
    assert result['minimum_personnel'] == 9, f"Test 5 FAILED: expected 9, got {result['minimum_personnel']}"
    assert roles_dict['medic'] == 4, f"Test 5 FAILED: medic expected 4, got {roles_dict['medic']}"
    print("  ✅ PASSED")
    
    # Test 6: Recommended personnel (20% buffer)
    print("\nTest 6: Recommended personnel calculation")
    result = calculate_personnel(
        scenario_type="fire",
        num_victims=5,
        severity="CRITICAL"
    )
    
    # base=4 + victim_ratio=1 + severity=2 = 7
    # recommended = ceil(7 * 1.2) = ceil(8.4) = 9
    print(f"  Minimum: {result['minimum_personnel']} (expected: 7)")
    print(f"  Recommended: {result['recommended_personnel']} (expected: 9)")
    
    assert result['minimum_personnel'] == 7, f"Test 6 FAILED: minimum expected 7, got {result['minimum_personnel']}"
    assert result['recommended_personnel'] == 9, f"Test 6 FAILED: recommended expected 9, got {result['recommended_personnel']}"
    print("  ✅ PASSED")
    
    # Test 7: Unknown scenario defaults
    print("\nTest 7: Unknown scenario uses 'general' base")
    result = calculate_personnel(
        scenario_type="unknown",
        num_victims=2,
        severity="STABLE"
    )
    
    assert result['breakdown']['base'] == 2, "Test 7 FAILED: should use general base of 2"
    print(f"  Base: {result['breakdown']['base']} (expected: 2)")
    print("  ✅ PASSED")
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! ✅")
    print("=" * 60)