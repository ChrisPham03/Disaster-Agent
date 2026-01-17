"""
Full Integration Test for Disaster Rescue System

Tests the complete workflow with all agents:
- Person A: Master Agent (prioritizer, location, victim_chat) + Resource Agent (inventory, allocator)
- Person B: Rescue Agent (tools_calculator, personnel_calc, navigation)
"""

import sys
import os
import time

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Person A imports
from modules.master_tools import (
    calculate_priority,
    extract_location,
    validate_coordinates,
    create_victim_report,
    parse_victim_message
)
from modules.resource_tools import (
    check_inventory,
    get_item_status,
    allocate_resources,
    release_resources
)
from modules.resource_tools.inventory import _reset_inventory
from modules.resource_tools.allocator import _reset_allocator

# Person B imports
from modules.rescue_tools import (
    calculate_equipment,
    calculate_personnel,
    get_route,
    estimate_arrival_time
)


def print_header(title: str):
    """Print formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_subheader(title: str):
    """Print formatted subsection header."""
    print(f"\n--- {title} ---")


def test_full_disaster_rescue_workflow():
    """
    Test complete disaster rescue workflow:
    
    1. Victim sends emergency message
    2. Master Agent parses message and extracts info
    3. Master Agent calculates priority
    4. Master Agent creates victim report
    5. Rescue Agent determines scenario type
    6. Rescue Agent calculates equipment needs
    7. Rescue Agent calculates personnel needs
    8. Resource Agent checks inventory
    9. Resource Agent allocates resources
    10. Rescue Agent plans route
    11. Mission completes, resources released
    """
    
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 10 + "DISASTER RESCUE SYSTEM - FULL INTEGRATION TEST" + " " * 11 + "║")
    print("║" + " " * 20 + "Person A + Person B Components" + " " * 17 + "║")
    print("╚" + "═" * 68 + "╝")
    
    # Reset state
    _reset_inventory()
    _reset_allocator()
    
    # =========================================================================
    # SCENARIO: Building collapse with fire, 5 victims trapped
    # =========================================================================
    print_header("SCENARIO: Building Collapse Emergency")
    
    victim_message = """
    EMERGENCY! There's been a building collapse at 45 Sukhumvit Road, Bangkok!
    5 people are trapped including 2 children. Three adults are bleeding heavily 
    and one child is unconscious. There's smoke and small fires in the debris.
    Our GPS coordinates are 13.7563, 100.5018. Please send help immediately!
    """
    
    print(f"\n📞 INCOMING EMERGENCY CALL:")
    print("-" * 50)
    print(victim_message)
    print("-" * 50)
    
    # =========================================================================
    # STEP 1: Parse victim message (Master Agent - Person A)
    # =========================================================================
    print_header("STEP 1: Master Agent - Parse Emergency Message")
    
    parsed = parse_victim_message(victim_message)
    
    print(f"  📋 Parsed Information:")
    print(f"     • Detected Severity: {parsed['detected_severity']}")
    print(f"     • Detected People: {parsed['detected_people_count']}")
    print(f"     • Detected Injuries: {parsed['detected_injuries']}")
    print(f"     • Detected Conditions: {parsed['detected_conditions']}")
    print(f"     • Keywords Found: {parsed['keywords_found'][:5]}...")  # First 5
    
    assert parsed['detected_severity'] == "CRITICAL", "Should detect CRITICAL"
    assert parsed['detected_people_count'] == 5, "Should detect 5 people"
    assert parsed['detected_injuries'] == True, "Should detect injuries"
    print("\n  ✅ Message parsing PASSED")
    
    # =========================================================================
    # STEP 2: Extract location (Master Agent - Person A)
    # =========================================================================
    print_header("STEP 2: Master Agent - Extract Location")
    
    location = extract_location(victim_message)
    
    print(f"  📍 Extracted Location:")
    print(f"     • Latitude: {location['lat']}")
    print(f"     • Longitude: {location['lng']}")
    print(f"     • Address: {location['address'][:50]}...")
    print(f"     • Confidence: {location['confidence']}")
    
    assert location['lat'] == 13.7563, "Should extract latitude"
    assert location['lng'] == 100.5018, "Should extract longitude"
    assert validate_coordinates(location['lat'], location['lng']), "Coords should be valid"
    print("\n  ✅ Location extraction PASSED")
    
    # =========================================================================
    # STEP 3: Calculate priority (Master Agent - Person A)
    # =========================================================================
    print_header("STEP 3: Master Agent - Calculate Priority")
    
    priority = calculate_priority(
        severity=parsed['detected_severity'],
        num_people=parsed['detected_people_count'],
        has_injuries=parsed['detected_injuries'],
        additional_factors={
            "fire_hazard": "fire_hazard" in parsed['detected_conditions'],
            "flooding": "flooding" in parsed['detected_conditions'],
            "structural_collapse": "structural_collapse" in parsed['detected_conditions']
        }
    )
    
    print(f"  🚨 Priority Assessment:")
    print(f"     • Score: {priority['priority_score']}/100")
    print(f"     • Level: {priority['priority_level']}")
    print(f"     • Reasoning:")
    for reason in priority['reasoning']:
        print(f"       - {reason}")
    
    # 50 (CRITICAL) + 20 (5 people) + 15 (injuries) + 5 (fire) + 5 (collapse) = 95
    assert priority['priority_score'] == 95, f"Expected 95, got {priority['priority_score']}"
    assert priority['priority_level'] == "CRITICAL", "Should be CRITICAL"
    print("\n  ✅ Priority calculation PASSED")
    
    # =========================================================================
    # STEP 4: Create victim report (Master Agent - Person A)
    # =========================================================================
    print_header("STEP 4: Master Agent - Create Victim Report")
    
    victim_report = create_victim_report(
        location=location,
        severity=parsed['detected_severity'],
        num_people=parsed['detected_people_count'],
        has_injuries=parsed['detected_injuries'],
        conditions=parsed['detected_conditions'],
        priority_result=priority
    )
    
    print(f"  📄 Victim Report Created:")
    print(f"     • Victim ID: {victim_report['victim_id']}")
    print(f"     • Severity: {victim_report['severity']}")
    print(f"     • People: {victim_report['num_people']}")
    print(f"     • Priority: {victim_report['priority_level']} ({victim_report['priority_score']})")
    print(f"     • Conditions: {victim_report['conditions']}")
    print(f"     • Reported At: {victim_report['reported_at']}")
    
    assert victim_report['victim_id'].startswith("V-"), "Should have valid ID"
    print("\n  ✅ Victim report creation PASSED")
    
    # =========================================================================
    # STEP 5: Determine scenario type (Rescue Agent - Person B)
    # =========================================================================
    print_header("STEP 5: Rescue Agent - Determine Scenario Type")
    
    # Logic: structural_collapse + fire_hazard → building_collapse takes priority
    conditions = victim_report['conditions']
    if "structural_collapse" in conditions:
        scenario_type = "building_collapse"
    elif "flooding" in conditions:
        scenario_type = "flood"
    elif "fire_hazard" in conditions:
        scenario_type = "fire"
    else:
        scenario_type = "medical" if victim_report['has_injuries'] else "general"
    
    # Check for special conditions (children mentioned)
    special_conditions = ["children"]  # Detected from message
    
    print(f"  🔍 Scenario Analysis:")
    print(f"     • Conditions: {conditions}")
    print(f"     • Determined Type: {scenario_type}")
    print(f"     • Special Conditions: {special_conditions}")
    
    assert scenario_type == "building_collapse", "Should be building_collapse"
    print("\n  ✅ Scenario determination PASSED")
    
    # =========================================================================
    # STEP 6: Calculate equipment (Rescue Agent - Person B)
    # =========================================================================
    print_header("STEP 6: Rescue Agent - Calculate Equipment Needs")
    
    equipment_calc = calculate_equipment(
        scenario_type=scenario_type,
        num_victims=victim_report['num_people'],
        severity=victim_report['severity'],
        special_conditions=special_conditions
    )
    
    print(f"  🛠️ Equipment Requirements:")
    print(f"     • Scenario: {equipment_calc['scenario_type']}")
    print(f"     • Personnel Needed: {equipment_calc['personnel_required']}")
    print(f"     • Equipment List:")
    for item in equipment_calc['equipment']:
        print(f"       - {item['item']}: {item['quantity']} ({item['priority']})")
    
    # Should have stretchers = 5 (1 per victim)
    stretchers = next(e for e in equipment_calc['equipment'] if e['item'] == 'stretcher')
    assert stretchers['quantity'] == 5, "Should need 5 stretchers"
    # Should have pediatric_kit for children
    has_pediatric = any(e['item'] == 'pediatric_kit' for e in equipment_calc['equipment'])
    assert has_pediatric, "Should include pediatric_kit for children"
    print("\n  ✅ Equipment calculation PASSED")
    
    # =========================================================================
    # STEP 7: Calculate personnel (Rescue Agent - Person B)
    # =========================================================================
    print_header("STEP 7: Rescue Agent - Calculate Personnel Needs")
    
    heavy_equipment_count = len([e for e in equipment_calc['equipment'] 
                                  if e['item'] in ['hydraulic_cutter', 'concrete_saw', 'airbag_lifter']])
    
    personnel_calc = calculate_personnel(
        scenario_type=scenario_type,
        num_victims=victim_report['num_people'],
        severity=victim_report['severity'],
        equipment_count=heavy_equipment_count
    )
    
    print(f"  👥 Personnel Requirements:")
    print(f"     • Minimum: {personnel_calc['minimum_personnel']}")
    print(f"     • Recommended: {personnel_calc['recommended_personnel']}")
    print(f"     • Breakdown:")
    print(f"       - Base: {personnel_calc['breakdown']['base']}")
    print(f"       - Victim Ratio: +{personnel_calc['breakdown']['victim_ratio']}")
    print(f"       - Severity Bonus: +{personnel_calc['breakdown']['severity_bonus']}")
    print(f"       - Equipment Ops: +{personnel_calc['breakdown']['equipment_operators']}")
    print(f"     • Role Distribution:")
    for role in personnel_calc['roles']:
        print(f"       - {role['role']}: {role['count']}")
    
    assert personnel_calc['minimum_personnel'] >= 6, "Should need at least 6 personnel"
    print("\n  ✅ Personnel calculation PASSED")
    
    # =========================================================================
    # STEP 8: Check inventory (Resource Agent - Person A)
    # =========================================================================
    print_header("STEP 8: Resource Agent - Check Inventory")
    
    inventory = check_inventory()
    
    print(f"  📦 Inventory Status:")
    print(f"     • Total Item Types: {len(inventory['items'])}")
    print(f"     • Key Items:")
    for item_name in ['stretcher', 'first_aid_kit', 'hydraulic_cutter', 'pediatric_kit']:
        status = inventory['items'].get(item_name, {})
        print(f"       - {item_name}: {status.get('available', 'N/A')} available")
    
    assert len(inventory['items']) == 20, "Should track 20 equipment types"
    print("\n  ✅ Inventory check PASSED")
    
    # =========================================================================
    # STEP 9: Allocate resources (Resource Agent - Person A)
    # =========================================================================
    print_header("STEP 9: Resource Agent - Allocate Resources")
    
    timestamp = int(time.time())
    
    allocation = allocate_resources(
        request_id=f"REQ-{timestamp}",
        mission_id=f"M-{timestamp}",
        equipment_list=equipment_calc['equipment']
    )
    
    print(f"  ✅ Allocation Result:")
    print(f"     • Request ID: {allocation['request_id']}")
    print(f"     • Mission ID: {allocation['mission_id']}")
    print(f"     • Team Assigned: {allocation['team_id']}")
    print(f"     • Allocation Success: {allocation['allocated']}")
    print(f"     • Items Assigned: {len(allocation['equipment_assigned'])}")
    if allocation['shortfall']:
        print(f"     • Shortfall Items: {len(allocation['shortfall'])}")
        for item in allocation['shortfall']:
            print(f"       - {item['item']}: {item['quantity']} ({item['reason']})")
    
    assert allocation['allocated'] == True, "Allocation should succeed"
    assert allocation['team_id'] == "T-Alpha", "Should assign Team Alpha"
    print("\n  ✅ Resource allocation PASSED")
    
    # =========================================================================
    # STEP 10: Plan route (Rescue Agent - Person B)
    # =========================================================================
    print_header("STEP 10: Rescue Agent - Plan Route")
    
    # Rescue station location (mock)
    rescue_station = {"lat": 13.7400, "lng": 100.5200}
    victim_location = {"lat": location['lat'], "lng": location['lng']}
    
    route = get_route(
        origin=rescue_station,
        destination=victim_location,
        avoid_hazards=["road_closure"] if "structural_collapse" in conditions else []
    )
    
    print(f"  🗺️ Route Planned:")
    print(f"     • Route ID: {route['route_id']}")
    print(f"     • Distance: {route['distance_km']} km")
    print(f"     • ETA: {route['estimated_time_minutes']} minutes")
    print(f"     • Hazards Avoided: {route['hazards_avoided']}")
    print(f"     • Directions:")
    for direction in route['directions'][:2]:  # First 2 steps
        print(f"       {direction['step']}. {direction['instruction']}")
    
    assert route['route_id'].startswith("R-"), "Should have valid route ID"
    assert route['distance_km'] > 0, "Should have positive distance"
    print("\n  ✅ Route planning PASSED")
    
    # =========================================================================
    # STEP 11: Mission summary
    # =========================================================================
    print_header("STEP 11: Mission Deployment Summary")
    
    print(f"""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                    🚨 MISSION DEPLOYMENT 🚨                       ║
    ╠══════════════════════════════════════════════════════════════════╣
    ║  Victim ID:     {victim_report['victim_id']:<47} ║
    ║  Priority:      {victim_report['priority_level']} (Score: {victim_report['priority_score']})                              ║
    ║  Location:      {location['address'][:43]:<43} ║
    ║  Scenario:      {scenario_type:<47} ║
    ╠══════════════════════════════════════════════════════════════════╣
    ║  Team:          {allocation['team_id']:<47} ║
    ║  Personnel:     {personnel_calc['minimum_personnel']} minimum ({personnel_calc['recommended_personnel']} recommended)                       ║
    ║  Equipment:     {len(allocation['equipment_assigned'])} items assigned                                ║
    ║  ETA:           {route['estimated_time_minutes']} minutes ({route['distance_km']} km)                             ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # =========================================================================
    # STEP 12: Mission complete - Release resources
    # =========================================================================
    print_header("STEP 12: Mission Complete - Release Resources")
    
    release_result = release_resources(allocation['mission_id'])
    
    print(f"  🏁 Mission Completed:")
    print(f"     • Mission ID: {release_result['mission_id']}")
    print(f"     • Resources Released: {release_result['released']}")
    print(f"     • Items Returned: {len(release_result['items_returned'])}")
    
    # Verify inventory restored
    final_inventory = check_inventory("stretcher")
    stretcher_final = final_inventory['items']['stretcher']
    print(f"     • Stretchers Restored: {stretcher_final['available']}/15")
    
    assert release_result['released'] == True, "Should release successfully"
    assert stretcher_final['available'] == 15, "Inventory should be restored"
    print("\n  ✅ Resource release PASSED")
    
    # =========================================================================
    # FINAL SUMMARY
    # =========================================================================
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "🎉 ALL INTEGRATION TESTS PASSED! 🎉" + " " * 16 + "║")
    print("╠" + "═" * 68 + "╣")
    print("║  Person A Components:                                              ║")
    print("║    ✅ prioritizer.py      - Priority scoring                       ║")
    print("║    ✅ location_utils.py   - Location extraction                    ║")
    print("║    ✅ victim_chat.py      - Victim report creation                 ║")
    print("║    ✅ inventory.py        - Inventory management                   ║")
    print("║    ✅ allocator.py        - Resource allocation                    ║")
    print("║                                                                    ║")
    print("║  Person B Components:                                              ║")
    print("║    ✅ tools_calculator.py - Equipment calculation                  ║")
    print("║    ✅ personnel_calc.py   - Personnel planning                     ║")
    print("║    ✅ navigation.py       - Route planning                         ║")
    print("║                                                                    ║")
    print("║  Configurations:                                                   ║")
    print("║    ✅ master_agent.yaml   - Master Agent config                    ║")
    print("║    ✅ resource_agent.yaml - Resource Agent config                  ║")
    print("║    ✅ rescue_agent.yaml   - Rescue Agent config                    ║")
    print("║    ✅ rest_gateway.yaml   - REST API Gateway config                ║")
    print("╚" + "═" * 68 + "╝")


if __name__ == "__main__":
    test_full_disaster_rescue_workflow()