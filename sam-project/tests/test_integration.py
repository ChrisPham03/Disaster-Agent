"""
Integration Test for Person A Components

Tests the full workflow:
1. Parse victim message
2. Extract location
3. Calculate priority
4. Create victim report
5. Allocate resources
6. Release resources
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

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


def test_full_workflow():
    """Test complete disaster rescue workflow."""
    
    print("=" * 70)
    print("INTEGRATION TEST: Full Disaster Rescue Workflow")
    print("=" * 70)
    
    # Reset state
    _reset_inventory()
    _reset_allocator()
    
    # =========================================================================
    # STEP 1: Victim sends emergency message
    # =========================================================================
    print("\n" + "=" * 70)
    print("STEP 1: Victim Emergency Message")
    print("=" * 70)
    
    victim_message = """
    Help! There's been a building collapse at 45 Sukhumvit Road, Bangkok!
    There are 5 people trapped here. Two are bleeding heavily and one is 
    unconscious. There's smoke coming from the debris. Please hurry!
    GPS: 13.7563, 100.5018
    """
    
    print(f"\nVictim Message:\n{victim_message}")
    
    # Parse the message
    parsed = parse_victim_message(victim_message)
    print(f"\nParsed Information:")
    print(f"  Detected Severity: {parsed['detected_severity']}")
    print(f"  Detected People: {parsed['detected_people_count']}")
    print(f"  Detected Injuries: {parsed['detected_injuries']}")
    print(f"  Detected Conditions: {parsed['detected_conditions']}")
    
    assert parsed['detected_severity'] == "CRITICAL", "Should detect CRITICAL severity"
    assert parsed['detected_people_count'] == 5, "Should detect 5 people"
    assert parsed['detected_injuries'] == True, "Should detect injuries"
    assert "fire_hazard" in parsed['detected_conditions'], "Should detect fire hazard"
    assert "structural_collapse" in parsed['detected_conditions'], "Should detect collapse"
    print("\n✅ Message parsing PASSED")
    
    # =========================================================================
    # STEP 2: Extract Location
    # =========================================================================
    print("\n" + "=" * 70)
    print("STEP 2: Extract Location")
    print("=" * 70)
    
    location = extract_location(victim_message)
    print(f"\nExtracted Location:")
    print(f"  Latitude: {location['lat']}")
    print(f"  Longitude: {location['lng']}")
    print(f"  Address: {location['address']}")
    print(f"  Confidence: {location['confidence']}")
    
    assert location['lat'] == 13.7563, "Should extract correct latitude"
    assert location['lng'] == 100.5018, "Should extract correct longitude"
    assert location['confidence'] == "high", "Should have high confidence with GPS"
    assert validate_coordinates(location['lat'], location['lng']), "Coordinates should be valid"
    print("\n✅ Location extraction PASSED")
    
    # =========================================================================
    # STEP 3: Calculate Priority
    # =========================================================================
    print("\n" + "=" * 70)
    print("STEP 3: Calculate Priority")
    print("=" * 70)
    
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
    
    print(f"\nPriority Calculation:")
    print(f"  Score: {priority['priority_score']}")
    print(f"  Level: {priority['priority_level']}")
    print(f"  Reasoning:")
    for reason in priority['reasoning']:
        print(f"    - {reason}")
    
    # Expected: 50 (CRITICAL) + 20 (5 people) + 15 (injuries) + 5 (fire) + 5 (collapse) = 95
    assert priority['priority_score'] == 95, f"Expected 95, got {priority['priority_score']}"
    assert priority['priority_level'] == "CRITICAL", "Should be CRITICAL priority"
    print("\n✅ Priority calculation PASSED")
    
    # =========================================================================
    # STEP 4: Create Victim Report
    # =========================================================================
    print("\n" + "=" * 70)
    print("STEP 4: Create Victim Report")
    print("=" * 70)
    
    report = create_victim_report(
        location=location,
        severity=parsed['detected_severity'],
        num_people=parsed['detected_people_count'],
        has_injuries=parsed['detected_injuries'],
        conditions=parsed['detected_conditions'],
        priority_result=priority
    )
    
    print(f"\nVictim Report:")
    print(f"  Victim ID: {report['victim_id']}")
    print(f"  Location: {report['location']['address']}")
    print(f"  Severity: {report['severity']}")
    print(f"  Num People: {report['num_people']}")
    print(f"  Has Injuries: {report['has_injuries']}")
    print(f"  Conditions: {report['conditions']}")
    print(f"  Priority Score: {report['priority_score']}")
    print(f"  Priority Level: {report['priority_level']}")
    print(f"  Reported At: {report['reported_at']}")
    
    assert report['victim_id'].startswith("V-"), "Should have valid victim ID format"
    assert report['severity'] == "CRITICAL", "Should preserve severity"
    assert report['num_people'] == 5, "Should preserve people count"
    assert report['priority_score'] == 95, "Should preserve priority score"
    print("\n✅ Victim report creation PASSED")
    
    # =========================================================================
    # STEP 5: Check Inventory
    # =========================================================================
    print("\n" + "=" * 70)
    print("STEP 5: Check Inventory Before Allocation")
    print("=" * 70)
    
    inventory = check_inventory()
    stretcher_status = get_item_status("stretcher")
    
    print(f"\nInventory Status:")
    print(f"  Total Items Tracked: {len(inventory['items'])}")
    print(f"  Stretchers Available: {stretcher_status['available']}")
    print(f"  Stretchers Total: {stretcher_status['total']}")
    
    assert len(inventory['items']) == 20, "Should track 20 equipment types"
    assert stretcher_status['available'] == 15, "Should have 15 stretchers available"
    print("\n✅ Inventory check PASSED")
    
    # =========================================================================
    # STEP 6: Allocate Resources
    # =========================================================================
    print("\n" + "=" * 70)
    print("STEP 6: Allocate Resources")
    print("=" * 70)
    
    import time
    timestamp = int(time.time())
    
    equipment_request = [
        {"item": "stretcher", "quantity": 5, "priority": "required"},
        {"item": "first_aid_kit", "quantity": 2, "priority": "required"},
        {"item": "hydraulic_cutter", "quantity": 2, "priority": "required"},
        {"item": "breathing_apparatus", "quantity": 4, "priority": "required"},
        {"item": "flashlight", "quantity": 5, "priority": "recommended"},
        {"item": "radio", "quantity": 3, "priority": "recommended"}
    ]
    
    allocation = allocate_resources(
        request_id=f"REQ-{timestamp}",
        mission_id=f"M-{timestamp}",
        equipment_list=equipment_request
    )
    
    print(f"\nAllocation Result:")
    print(f"  Request ID: {allocation['request_id']}")
    print(f"  Mission ID: {allocation['mission_id']}")
    print(f"  Allocated: {allocation['allocated']}")
    print(f"  Team ID: {allocation['team_id']}")
    print(f"  Equipment Assigned:")
    for item in allocation['equipment_assigned']:
        print(f"    - {item['item']}: {item['quantity']}")
    if allocation['shortfall']:
        print(f"  Shortfall:")
        for item in allocation['shortfall']:
            print(f"    - {item['item']}: {item['quantity']} ({item['reason']})")
    
    assert allocation['allocated'] == True, "Should successfully allocate"
    assert allocation['team_id'] == "T-Alpha", "Should assign Team Alpha"
    assert len(allocation['equipment_assigned']) == 6, "Should allocate all 6 items"
    print("\n✅ Resource allocation PASSED")
    
    # =========================================================================
    # STEP 7: Verify Inventory Updated
    # =========================================================================
    print("\n" + "=" * 70)
    print("STEP 7: Verify Inventory After Allocation")
    print("=" * 70)
    
    stretcher_after = get_item_status("stretcher")
    print(f"\nStretcher Status After Allocation:")
    print(f"  Available: {stretcher_after['available']} (was 15)")
    print(f"  Reserved: {stretcher_after['reserved']}")
    
    assert stretcher_after['available'] == 10, "Should have 10 stretchers available"
    assert stretcher_after['reserved'] == 5, "Should have 5 stretchers reserved"
    print("\n✅ Inventory update PASSED")
    
    # =========================================================================
    # STEP 8: Release Resources (Mission Complete)
    # =========================================================================
    print("\n" + "=" * 70)
    print("STEP 8: Release Resources (Mission Complete)")
    print("=" * 70)
    
    release_result = release_resources(allocation['mission_id'])
    
    print(f"\nRelease Result:")
    print(f"  Mission ID: {release_result['mission_id']}")
    print(f"  Released: {release_result['released']}")
    print(f"  Items Returned:")
    for item in release_result['items_returned']:
        print(f"    - {item['item']}: {item['quantity']}")
    
    assert release_result['released'] == True, "Should successfully release"
    
    # Verify inventory restored
    stretcher_final = get_item_status("stretcher")
    print(f"\nStretcher Status After Release:")
    print(f"  Available: {stretcher_final['available']} (should be 15)")
    
    assert stretcher_final['available'] == 15, "Should restore stretchers to 15"
    print("\n✅ Resource release PASSED")
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 70)
    print("🎉 ALL INTEGRATION TESTS PASSED! 🎉")
    print("=" * 70)
    print("""
    Summary of Person A Components:
    
    ✅ modules/master_tools/prioritizer.py    - Priority scoring
    ✅ modules/master_tools/location_utils.py - Location extraction
    ✅ modules/master_tools/victim_chat.py    - Victim report creation
    ✅ modules/resource_tools/inventory.py    - Inventory management
    ✅ modules/resource_tools/allocator.py    - Resource allocation
    ✅ configs/agents/master_agent.yaml       - Master Agent config
    ✅ configs/agents/resource_agent.yaml     - Resource Agent config
    
    Ready for integration with Person B!
    """)


if __name__ == "__main__":
    test_full_workflow()