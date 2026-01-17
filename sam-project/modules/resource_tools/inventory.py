"""
Inventory Management Module for Resource Agent

Manages equipment inventory with tracking, status checking, and alerts.
"""

import time
import copy
from typing import Dict, Any, Optional
from datetime import datetime, timezone


# In-memory inventory (initialized with values from TEAM-COORDINATION-README)
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

# Valid equipment names (for validation)
VALID_EQUIPMENT = list(INITIAL_INVENTORY.keys())

# Global inventory state (mutable copy of initial inventory)
_inventory: Dict[str, Dict[str, int]] = {}
_alerts_sent: list = []


def _initialize_inventory():
    """Initialize inventory from INITIAL_INVENTORY if empty."""
    global _inventory
    if not _inventory:
        _inventory = copy.deepcopy(INITIAL_INVENTORY)


def _reset_inventory():
    """Reset inventory to initial state (for testing)."""
    global _inventory, _alerts_sent
    _inventory = copy.deepcopy(INITIAL_INVENTORY)
    _alerts_sent = []


def _calculate_item_status(item_data: Dict[str, int]) -> str:
    """
    Calculate status based on available quantity and threshold.
    
    Returns:
        "ok" | "low" | "critical" | "out"
    """
    available = item_data["total"] - item_data["reserved"]
    threshold = item_data["threshold"]
    
    if available <= 0:
        return "out"
    elif available <= threshold // 2:
        return "critical"
    elif available <= threshold:
        return "low"
    else:
        return "ok"


def check_inventory(item_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Check inventory levels.
    
    Args:
        item_type: Specific item to check, or None for all items
    
    Returns:
        INVENTORY_STATUS dict:
        {
            "checked_at": str (ISO 8601),
            "items": dict[str, ITEM_STATUS]
        }
        
        Where ITEM_STATUS is:
        {
            "available": int,
            "total": int,
            "reserved": int,
            "threshold": int,
            "status": str ("ok" | "low" | "critical" | "out")
        }
    """
    _initialize_inventory()
    
    checked_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    if item_type is not None:
        # Check specific item
        item_type = item_type.lower()
        if item_type not in _inventory:
            return {
                "checked_at": checked_at,
                "items": {},
                "error": f"Item '{item_type}' not found in inventory"
            }
        
        item_data = _inventory[item_type]
        available = item_data["total"] - item_data["reserved"]
        
        return {
            "checked_at": checked_at,
            "items": {
                item_type: {
                    "available": available,
                    "total": item_data["total"],
                    "reserved": item_data["reserved"],
                    "threshold": item_data["threshold"],
                    "status": _calculate_item_status(item_data)
                }
            }
        }
    
    # Check all items
    items_status: Dict[str, Dict[str, Any]] = {}
    
    for item_name, item_data in _inventory.items():
        available = item_data["total"] - item_data["reserved"]
        items_status[item_name] = {
            "available": available,
            "total": item_data["total"],
            "reserved": item_data["reserved"],
            "threshold": item_data["threshold"],
            "status": _calculate_item_status(item_data)
        }
    
    return {
        "checked_at": checked_at,
        "items": items_status
    }


def get_item_status(item_name: str) -> Dict[str, Any]:
    """
    Get status of a single item.
    
    Args:
        item_name: Name of the equipment item
    
    Returns:
        ITEM_STATUS dict or {"error": "Item not found"}
    """
    _initialize_inventory()
    
    item_name = item_name.lower()
    
    if item_name not in _inventory:
        return {"error": f"Item '{item_name}' not found"}
    
    item_data = _inventory[item_name]
    available = item_data["total"] - item_data["reserved"]
    
    return {
        "available": available,
        "total": item_data["total"],
        "reserved": item_data["reserved"],
        "threshold": item_data["threshold"],
        "status": _calculate_item_status(item_data)
    }


def send_alert(item_name: str, alert_type: str, message: str) -> Dict[str, Any]:
    """
    Send inventory alert.
    
    Args:
        item_name: Equipment name
        alert_type: "low_stock" | "critical" | "out_of_stock"
        message: Alert description
    
    Returns:
        {"alert_id": str, "sent": bool, "timestamp": str}
    """
    global _alerts_sent
    
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    alert_id = f"ALERT-{int(time.time())}"
    
    alert = {
        "alert_id": alert_id,
        "item_name": item_name,
        "alert_type": alert_type,
        "message": message,
        "timestamp": timestamp
    }
    
    # Store alert (in production, this would send to notification system)
    _alerts_sent.append(alert)
    
    return {
        "alert_id": alert_id,
        "sent": True,
        "timestamp": timestamp
    }


def reserve_items(item_name: str, quantity: int) -> Dict[str, Any]:
    """
    Reserve items from inventory (increase reserved count).
    
    Args:
        item_name: Name of the equipment
        quantity: Number to reserve
    
    Returns:
        {"success": bool, "reserved": int, "available_after": int}
    """
    _initialize_inventory()
    
    item_name = item_name.lower()
    
    if item_name not in _inventory:
        return {
            "success": False,
            "error": f"Item '{item_name}' not found"
        }
    
    item_data = _inventory[item_name]
    available = item_data["total"] - item_data["reserved"]
    
    if quantity > available:
        return {
            "success": False,
            "error": f"Insufficient stock. Requested: {quantity}, Available: {available}",
            "available": available
        }
    
    # Reserve the items
    item_data["reserved"] += quantity
    available_after = item_data["total"] - item_data["reserved"]
    
    return {
        "success": True,
        "reserved": quantity,
        "available_after": available_after
    }


def release_items(item_name: str, quantity: int) -> Dict[str, Any]:
    """
    Release reserved items back to inventory.
    
    Args:
        item_name: Name of the equipment
        quantity: Number to release
    
    Returns:
        {"success": bool, "released": int, "available_after": int}
    """
    _initialize_inventory()
    
    item_name = item_name.lower()
    
    if item_name not in _inventory:
        return {
            "success": False,
            "error": f"Item '{item_name}' not found"
        }
    
    item_data = _inventory[item_name]
    
    # Can't release more than reserved
    actual_release = min(quantity, item_data["reserved"])
    item_data["reserved"] -= actual_release
    available_after = item_data["total"] - item_data["reserved"]
    
    return {
        "success": True,
        "released": actual_release,
        "available_after": available_after
    }


# Test function
if __name__ == "__main__":
    print("=" * 60)
    print("TESTING INVENTORY")
    print("=" * 60)
    
    # Reset inventory for clean test
    _reset_inventory()
    
    # Test 1: Check all inventory
    print("\nTest 1: Check all inventory")
    result = check_inventory()
    print(f"  Checked at: {result['checked_at']}")
    print(f"  Total items: {len(result['items'])} (expected: 20)")
    assert len(result['items']) == 20, "Test 1 FAILED!"
    assert "stretcher" in result['items'], "Test 1 FAILED!"
    print("  ✅ PASSED")
    
    # Test 2: Check specific item
    print("\nTest 2: Check specific item (stretcher)")
    result = check_inventory("stretcher")
    stretcher = result['items']['stretcher']
    print(f"  Available: {stretcher['available']} (expected: 15)")
    print(f"  Total: {stretcher['total']} (expected: 15)")
    print(f"  Status: {stretcher['status']} (expected: ok)")
    assert stretcher['available'] == 15, "Test 2 FAILED!"
    assert stretcher['total'] == 15, "Test 2 FAILED!"
    assert stretcher['status'] == "ok", "Test 2 FAILED!"
    print("  ✅ PASSED")
    
    # Test 3: Get item status
    print("\nTest 3: Get item status (first_aid_kit)")
    status = get_item_status("first_aid_kit")
    print(f"  Available: {status['available']} (expected: 30)")
    print(f"  Threshold: {status['threshold']} (expected: 10)")
    assert status['available'] == 30, "Test 3 FAILED!"
    assert status['threshold'] == 10, "Test 3 FAILED!"
    print("  ✅ PASSED")
    
    # Test 4: Reserve items
    print("\nTest 4: Reserve items (5 stretchers)")
    result = reserve_items("stretcher", 5)
    print(f"  Success: {result['success']} (expected: True)")
    print(f"  Reserved: {result['reserved']} (expected: 5)")
    print(f"  Available after: {result['available_after']} (expected: 10)")
    assert result['success'] == True, "Test 4 FAILED!"
    assert result['reserved'] == 5, "Test 4 FAILED!"
    assert result['available_after'] == 10, "Test 4 FAILED!"
    print("  ✅ PASSED")
    
    # Test 5: Check status after reservation
    print("\nTest 5: Check stretcher status after reservation")
    status = get_item_status("stretcher")
    print(f"  Available: {status['available']} (expected: 10)")
    print(f"  Reserved: {status['reserved']} (expected: 5)")
    assert status['available'] == 10, "Test 5 FAILED!"
    assert status['reserved'] == 5, "Test 5 FAILED!"
    print("  ✅ PASSED")
    
    # Test 6: Try to reserve more than available
    print("\nTest 6: Try to reserve more than available (20 stretchers)")
    result = reserve_items("stretcher", 20)
    print(f"  Success: {result['success']} (expected: False)")
    assert result['success'] == False, "Test 6 FAILED!"
    assert "error" in result, "Test 6 FAILED!"
    print("  ✅ PASSED")
    
    # Test 7: Send alert
    print("\nTest 7: Send low stock alert")
    result = send_alert("stretcher", "low_stock", "Stretcher inventory below threshold")
    print(f"  Alert ID: {result['alert_id']}")
    print(f"  Sent: {result['sent']} (expected: True)")
    assert result['sent'] == True, "Test 7 FAILED!"
    assert result['alert_id'].startswith("ALERT-"), "Test 7 FAILED!"
    print("  ✅ PASSED")
    
    # Test 8: Release items
    print("\nTest 8: Release items (3 stretchers)")
    result = release_items("stretcher", 3)
    print(f"  Success: {result['success']} (expected: True)")
    print(f"  Released: {result['released']} (expected: 3)")
    print(f"  Available after: {result['available_after']} (expected: 13)")
    assert result['success'] == True, "Test 8 FAILED!"
    assert result['released'] == 3, "Test 8 FAILED!"
    assert result['available_after'] == 13, "Test 8 FAILED!"
    print("  ✅ PASSED")
    
    # Test 9: Invalid item
    print("\nTest 9: Check invalid item")
    status = get_item_status("invalid_item")
    print(f"  Error: {status.get('error')}")
    assert "error" in status, "Test 9 FAILED!"
    print("  ✅ PASSED")
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! ✅")
    print("=" * 60)