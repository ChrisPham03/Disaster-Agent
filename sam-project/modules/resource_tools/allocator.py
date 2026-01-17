"""
Resource Allocator Module for Resource Agent

Handles resource allocation and release for rescue missions.
"""

import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


# Track active allocations by mission_id
_active_allocations: Dict[str, Dict[str, Any]] = {}

# Team names for auto-assignment
TEAM_NAMES = ["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot"]
_next_team_index = 0


def _get_next_team_id() -> str:
    """Get next available team ID."""
    global _next_team_index
    team_name = TEAM_NAMES[_next_team_index % len(TEAM_NAMES)]
    _next_team_index += 1
    return f"T-{team_name}"


def _reset_allocator():
    """Reset allocator state (for testing)."""
    global _active_allocations, _next_team_index
    _active_allocations = {}
    _next_team_index = 0


def allocate_resources(
    request_id: str,
    mission_id: str,
    equipment_list: List[Dict[str, Any]],
    team_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Allocate resources for a rescue mission.
    
    Args:
        request_id: From EQUIPMENT_REQUEST (format: "REQ-{timestamp}")
        mission_id: From EQUIPMENT_REQUEST (format: "M-{timestamp}")
        equipment_list: List of {"item": str, "quantity": int, "priority": str}
        team_id: Optional team assignment, auto-generate if None
    
    Returns:
        ALLOCATION_RESPONSE dict:
        {
            "request_id": str,
            "mission_id": str,
            "allocated": bool,
            "team_id": str,
            "equipment_assigned": list[dict],
            "shortfall": list[dict],
            "allocated_at": str
        }
    """
    # Handle imports for both package and direct execution
    try:
        from .inventory import get_item_status, reserve_items, _initialize_inventory
    except ImportError:
        from inventory import get_item_status, reserve_items, _initialize_inventory
    
    _initialize_inventory()
    
    # Auto-assign team if not provided
    if team_id is None:
        team_id = _get_next_team_id()
    
    equipment_assigned: List[Dict[str, Any]] = []
    shortfall: List[Dict[str, Any]] = []
    
    # Process each equipment request
    for item_request in equipment_list:
        item_name = item_request.get("item", "").lower()
        requested_qty = item_request.get("quantity", 0)
        priority = item_request.get("priority", "required")
        
        # Check availability
        status = get_item_status(item_name)
        
        if "error" in status:
            # Item not found in inventory
            shortfall.append({
                "item": item_name,
                "quantity": requested_qty,
                "reason": "item_not_found"
            })
            continue
        
        available = status["available"]
        
        if available >= requested_qty:
            # Full allocation possible
            result = reserve_items(item_name, requested_qty)
            if result["success"]:
                equipment_assigned.append({
                    "item": item_name,
                    "quantity": requested_qty
                })
        elif available > 0:
            # Partial allocation
            result = reserve_items(item_name, available)
            if result["success"]:
                equipment_assigned.append({
                    "item": item_name,
                    "quantity": available
                })
            shortfall.append({
                "item": item_name,
                "quantity": requested_qty - available,
                "reason": "insufficient_stock"
            })
        else:
            # No stock available
            shortfall.append({
                "item": item_name,
                "quantity": requested_qty,
                "reason": "out_of_stock"
            })
    
    # Determine if allocation was successful (at least some items allocated)
    allocated = len(equipment_assigned) > 0
    
    # Store allocation for later release
    allocation_record = {
        "request_id": request_id,
        "mission_id": mission_id,
        "team_id": team_id,
        "equipment_assigned": equipment_assigned,
        "allocated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    _active_allocations[mission_id] = allocation_record
    
    return {
        "request_id": request_id,
        "mission_id": mission_id,
        "allocated": allocated,
        "team_id": team_id,
        "equipment_assigned": equipment_assigned,
        "shortfall": shortfall,
        "allocated_at": allocation_record["allocated_at"]
    }


def release_resources(mission_id: str) -> Dict[str, Any]:
    """
    Release resources when mission completes.
    
    Args:
        mission_id: Mission ID to release resources for
    
    Returns:
        {"mission_id": str, "released": bool, "items_returned": list}
    """
    # Handle imports for both package and direct execution
    try:
        from .inventory import release_items
    except ImportError:
        from inventory import release_items
    
    if mission_id not in _active_allocations:
        return {
            "mission_id": mission_id,
            "released": False,
            "error": f"Mission '{mission_id}' not found in active allocations",
            "items_returned": []
        }
    
    allocation = _active_allocations[mission_id]
    items_returned: List[Dict[str, Any]] = []
    
    # Release each allocated item
    for item in allocation["equipment_assigned"]:
        item_name = item["item"]
        quantity = item["quantity"]
        
        result = release_items(item_name, quantity)
        if result["success"]:
            items_returned.append({
                "item": item_name,
                "quantity": result["released"]
            })
    
    # Remove from active allocations
    del _active_allocations[mission_id]
    
    return {
        "mission_id": mission_id,
        "released": True,
        "items_returned": items_returned
    }


def get_active_allocations() -> Dict[str, Any]:
    """Get all active allocations."""
    return _active_allocations.copy()


def get_mission_allocation(mission_id: str) -> Optional[Dict[str, Any]]:
    """Get allocation details for a specific mission."""
    return _active_allocations.get(mission_id)


# Test function
if __name__ == "__main__":
    import sys
    import os
    
    # Add current directory to path for direct execution
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    from inventory import _reset_inventory, get_item_status, check_inventory
    
    print("=" * 60)
    print("TESTING ALLOCATOR")
    print("=" * 60)
    
    # Reset for clean test
    _reset_inventory()
    _reset_allocator()
    
    # Test 1: Basic allocation
    print("\nTest 1: Basic allocation")
    equipment = [
        {"item": "stretcher", "quantity": 3, "priority": "required"},
        {"item": "first_aid_kit", "quantity": 1, "priority": "required"},
        {"item": "hydraulic_cutter", "quantity": 1, "priority": "recommended"}
    ]
    
    result = allocate_resources(
        request_id="REQ-1704067500",
        mission_id="M-1704067500",
        equipment_list=equipment
    )
    
    print(f"  Request ID: {result['request_id']}")
    print(f"  Mission ID: {result['mission_id']}")
    print(f"  Allocated: {result['allocated']} (expected: True)")
    print(f"  Team ID: {result['team_id']} (expected: T-Alpha)")
    print(f"  Equipment assigned: {result['equipment_assigned']}")
    print(f"  Shortfall: {result['shortfall']}")
    
    assert result['allocated'] == True, "Test 1 FAILED!"
    assert result['team_id'] == "T-Alpha", "Test 1 FAILED!"
    assert len(result['equipment_assigned']) == 3, "Test 1 FAILED!"
    assert len(result['shortfall']) == 0, "Test 1 FAILED!"
    print("  ✅ PASSED")
    
    # Test 2: Verify inventory updated
    print("\nTest 2: Verify inventory updated after allocation")
    status = get_item_status("stretcher")
    print(f"  Stretcher available: {status['available']} (expected: 12)")
    print(f"  Stretcher reserved: {status['reserved']} (expected: 3)")
    assert status['available'] == 12, "Test 2 FAILED!"
    assert status['reserved'] == 3, "Test 2 FAILED!"
    print("  ✅ PASSED")
    
    # Test 3: Partial allocation
    print("\nTest 3: Partial allocation (request 5 airbag_lifters, only 2 available)")
    equipment = [
        {"item": "airbag_lifter", "quantity": 5, "priority": "required"}
    ]
    
    result = allocate_resources(
        request_id="REQ-1704067600",
        mission_id="M-1704067600",
        equipment_list=equipment
    )
    
    print(f"  Allocated: {result['allocated']} (expected: True)")
    print(f"  Equipment assigned: {result['equipment_assigned']}")
    print(f"  Shortfall: {result['shortfall']}")
    
    assert result['allocated'] == True, "Test 3 FAILED!"
    assert result['equipment_assigned'][0]['quantity'] == 2, "Test 3 FAILED!"
    assert len(result['shortfall']) == 1, "Test 3 FAILED!"
    assert result['shortfall'][0]['quantity'] == 3, "Test 3 FAILED!"
    print("  ✅ PASSED")
    
    # Test 4: Auto team assignment
    print("\nTest 4: Auto team assignment (should be T-Bravo)")
    assert result['team_id'] == "T-Bravo", "Test 4 FAILED!"
    print(f"  Team ID: {result['team_id']}")
    print("  ✅ PASSED")
    
    # Test 5: Custom team ID
    print("\nTest 5: Custom team ID")
    equipment = [{"item": "radio", "quantity": 2, "priority": "required"}]
    
    result = allocate_resources(
        request_id="REQ-1704067700",
        mission_id="M-1704067700",
        equipment_list=equipment,
        team_id="T-Special"
    )
    
    print(f"  Team ID: {result['team_id']} (expected: T-Special)")
    assert result['team_id'] == "T-Special", "Test 5 FAILED!"
    print("  ✅ PASSED")
    
    # Test 6: Release resources
    print("\nTest 6: Release resources for mission M-1704067500")
    status_before = get_item_status("stretcher")
    print(f"  Stretcher available before: {status_before['available']}")
    
    result = release_resources("M-1704067500")
    
    print(f"  Released: {result['released']} (expected: True)")
    print(f"  Items returned: {result['items_returned']}")
    
    status_after = get_item_status("stretcher")
    print(f"  Stretcher available after: {status_after['available']} (expected: 15)")
    
    assert result['released'] == True, "Test 6 FAILED!"
    assert len(result['items_returned']) == 3, "Test 6 FAILED!"
    assert status_after['available'] == 15, "Test 6 FAILED!"
    print("  ✅ PASSED")
    
    # Test 7: Release non-existent mission
    print("\nTest 7: Release non-existent mission")
    result = release_resources("M-INVALID")
    print(f"  Released: {result['released']} (expected: False)")
    assert result['released'] == False, "Test 7 FAILED!"
    print("  ✅ PASSED")
    
    # Test 8: Invalid item in request
    print("\nTest 8: Request with invalid item")
    equipment = [
        {"item": "invalid_item", "quantity": 1, "priority": "required"},
        {"item": "flashlight", "quantity": 2, "priority": "required"}
    ]
    
    result = allocate_resources(
        request_id="REQ-1704067800",
        mission_id="M-1704067800",
        equipment_list=equipment
    )
    
    print(f"  Allocated: {result['allocated']} (expected: True)")
    assert result['allocated'] == True, "Test 8 FAILED!"
    assert any(e['item'] == 'flashlight' for e in result['equipment_assigned']), "Test 8 FAILED!"
    assert any(s['item'] == 'invalid_item' for s in result['shortfall']), "Test 8 FAILED!"
    print("  ✅ PASSED")
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! ✅")
    print("=" * 60)