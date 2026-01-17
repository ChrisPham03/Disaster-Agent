"""
Victim Chat Module for Master Agent

Creates standardized victim reports following the VICTIM_REPORT contract.
"""

import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


def create_victim_report(
    location: Dict[str, Any],
    severity: str,
    num_people: int,
    has_injuries: bool,
    conditions: Optional[List[str]] = None,
    priority_result: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a standardized victim report following VICTIM_REPORT contract.
    
    Args:
        location: Dict with lat, lng, address keys
        severity: "CRITICAL" | "MODERATE" | "STABLE"
        num_people: Number of people needing rescue (minimum 1)
        has_injuries: Whether injuries are reported
        conditions: List of conditions e.g., ["fire_hazard", "flooding", "structural_collapse"]
        priority_result: Optional pre-calculated priority result from calculate_priority()
    
    Returns:
        Complete VICTIM_REPORT dict:
        {
            "victim_id": str,          # Format: "V-{timestamp}"
            "location": {
                "lat": float,
                "lng": float,
                "address": str
            },
            "severity": str,           # ENUM: "CRITICAL" | "MODERATE" | "STABLE"
            "num_people": int,
            "has_injuries": bool,
            "conditions": list[str],
            "priority_score": int,     # Range: 0-100
            "priority_level": str,     # ENUM: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
            "reported_at": str         # ISO 8601 format
        }
    """
    # Generate victim ID with timestamp
    timestamp = int(time.time())
    victim_id = f"V-{timestamp}"
    
    # Normalize severity to uppercase
    severity_normalized = severity.upper()
    if severity_normalized not in ["CRITICAL", "MODERATE", "STABLE"]:
        severity_normalized = "MODERATE"  # Default if invalid
    
    # Ensure num_people is at least 1
    num_people = max(1, int(num_people))
    
    # Normalize conditions
    conditions = conditions or []
    valid_conditions = ["fire_hazard", "flooding", "structural_collapse"]
    conditions = [c for c in conditions if c in valid_conditions]
    
    # Calculate priority if not provided
    if priority_result is None:
        from .prioritizer import calculate_priority
        
        # Build additional factors from conditions
        additional_factors = {
            "fire_hazard": "fire_hazard" in conditions,
            "flooding": "flooding" in conditions,
            "structural_collapse": "structural_collapse" in conditions
        }
        
        priority_result = calculate_priority(
            severity=severity_normalized,
            num_people=num_people,
            has_injuries=has_injuries,
            additional_factors=additional_factors
        )
    
    # Build location dict
    location_data = {
        "lat": location.get("lat"),
        "lng": location.get("lng"),
        "address": location.get("address", "Unknown")
    }
    
    # Create the victim report
    report: Dict[str, Any] = {
        "victim_id": victim_id,
        "location": location_data,
        "severity": severity_normalized,
        "num_people": num_people,
        "has_injuries": has_injuries,
        "conditions": conditions,
        "priority_score": priority_result.get("priority_score", 0),
        "priority_level": priority_result.get("priority_level", "LOW"),
        "reported_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    return report


def parse_victim_message(message: str) -> Dict[str, Any]:
    """
    Parse a victim's natural language message to extract key information.
    
    Args:
        message: Raw message from victim
    
    Returns:
        Dict with extracted information:
        {
            "detected_severity": str or None,
            "detected_people_count": int or None,
            "detected_injuries": bool or None,
            "detected_conditions": list[str],
            "keywords_found": list[str]
        }
    """
    import re
    message_lower = message.lower()
    
    result = {
        "detected_severity": None,
        "detected_people_count": None,
        "detected_injuries": None,
        "detected_conditions": [],
        "keywords_found": []
    }
    
    # Severity detection
    critical_keywords = ["dying", "bleeding heavily", "unconscious", "not breathing", 
                        "heart attack", "stroke", "critical", "emergency", "urgent"]
    moderate_keywords = ["injured", "hurt", "broken", "bleeding", "pain", "wound"]
    stable_keywords = ["okay", "safe", "stable", "minor", "small"]
    
    for keyword in critical_keywords:
        if keyword in message_lower:
            result["detected_severity"] = "CRITICAL"
            result["keywords_found"].append(keyword)
            break
    
    if result["detected_severity"] is None:
        for keyword in moderate_keywords:
            if keyword in message_lower:
                result["detected_severity"] = "MODERATE"
                result["keywords_found"].append(keyword)
                break
    
    if result["detected_severity"] is None:
        for keyword in stable_keywords:
            if keyword in message_lower:
                result["detected_severity"] = "STABLE"
                result["keywords_found"].append(keyword)
                break
    
    # People count detection - number patterns
    number_patterns = [
        (r'(\d+)\s*(?:people|persons|of us|victims)', 1),
        (r'(?:there are|we are|about)\s*(\d+)', 1),
        (r'(\d+)\s*(?:adults?|children|kids)', 1),
    ]
    
    for pattern, group in number_patterns:
        match = re.search(pattern, message_lower)
        if match:
            try:
                result["detected_people_count"] = int(match.group(group))
                break
            except ValueError:
                pass
    
    # Word-based numbers
    word_numbers = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
    }
    if result["detected_people_count"] is None:
        for word, num in word_numbers.items():
            if re.search(rf'\b{word}\b.*(?:people|persons|of us)', message_lower):
                result["detected_people_count"] = num
                break
    
    # Injury detection
    injury_keywords = ["injured", "hurt", "bleeding", "broken", "wound", "pain", 
                       "unconscious", "not breathing"]
    no_injury_keywords = ["not injured", "no injuries", "uninjured", "okay", "fine"]
    
    for keyword in no_injury_keywords:
        if keyword in message_lower:
            result["detected_injuries"] = False
            break
    
    if result["detected_injuries"] is None:
        for keyword in injury_keywords:
            if keyword in message_lower:
                result["detected_injuries"] = True
                break
    
    # Condition detection
    condition_keywords = {
        "fire_hazard": ["fire", "smoke", "burning", "flames"],
        "flooding": ["flood", "water rising", "drowning", "submerged"],
        "structural_collapse": ["collapse", "collapsed", "rubble", "debris", 
                                "building fell", "trapped under"]
    }
    
    for condition, keywords in condition_keywords.items():
        for keyword in keywords:
            if keyword in message_lower:
                if condition not in result["detected_conditions"]:
                    result["detected_conditions"].append(condition)
                    result["keywords_found"].append(keyword)
                break
    
    return result


# Test function
if __name__ == "__main__":
    # Need to handle imports for standalone testing
    import sys
    import os
    
    # Add parent directory to path for imports
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    print("=" * 60)
    print("TESTING VICTIM CHAT")
    print("=" * 60)
    
    # Test 1: Create basic victim report
    print("\nTest 1: Create victim report")
    location = {
        "lat": 13.7563,
        "lng": 100.5018,
        "address": "45 Sukhumvit Road, Bangkok"
    }
    
    # Mock priority result to avoid import issues in standalone test
    mock_priority = {
        "priority_score": 87,
        "priority_level": "CRITICAL"
    }
    
    report = create_victim_report(
        location=location,
        severity="CRITICAL",
        num_people=3,
        has_injuries=True,
        conditions=["structural_collapse", "fire_hazard"],
        priority_result=mock_priority
    )
    
    print(f"  Victim ID: {report['victim_id']}")
    print(f"  Location: {report['location']}")
    print(f"  Severity: {report['severity']} (expected: CRITICAL)")
    print(f"  Num People: {report['num_people']} (expected: 3)")
    print(f"  Has Injuries: {report['has_injuries']} (expected: True)")
    print(f"  Conditions: {report['conditions']}")
    print(f"  Priority Score: {report['priority_score']} (expected: 87)")
    print(f"  Priority Level: {report['priority_level']} (expected: CRITICAL)")
    
    assert report['victim_id'].startswith("V-"), "Test 1 FAILED!"
    assert report['severity'] == "CRITICAL", "Test 1 FAILED!"
    assert report['num_people'] == 3, "Test 1 FAILED!"
    assert report['has_injuries'] == True, "Test 1 FAILED!"
    assert report['priority_score'] == 87, "Test 1 FAILED!"
    assert report['priority_level'] == "CRITICAL", "Test 1 FAILED!"
    assert "reported_at" in report, "Test 1 FAILED!"
    print("  ✅ PASSED")
    
    # Test 2: Parse victim message - critical
    print("\nTest 2: Parse critical victim message")
    message = "Help! There are 5 people trapped. Two are bleeding heavily. There's smoke everywhere!"
    parsed = parse_victim_message(message)
    
    print(f"  Message: '{message}'")
    print(f"  Detected Severity: {parsed['detected_severity']} (expected: CRITICAL)")
    print(f"  Detected People: {parsed['detected_people_count']} (expected: 5)")
    print(f"  Detected Injuries: {parsed['detected_injuries']} (expected: True)")
    print(f"  Detected Conditions: {parsed['detected_conditions']}")
    
    assert parsed['detected_severity'] == "CRITICAL", "Test 2 FAILED!"
    assert parsed['detected_people_count'] == 5, "Test 2 FAILED!"
    assert parsed['detected_injuries'] == True, "Test 2 FAILED!"
    assert "fire_hazard" in parsed['detected_conditions'], "Test 2 FAILED!"
    print("  ✅ PASSED")
    
    # Test 3: Parse victim message - moderate
    print("\nTest 3: Parse moderate victim message")
    message = "We need help. 3 people are injured but stable. Building is flooding."
    parsed = parse_victim_message(message)
    
    print(f"  Message: '{message}'")
    print(f"  Detected Severity: {parsed['detected_severity']} (expected: MODERATE)")
    print(f"  Detected People: {parsed['detected_people_count']} (expected: 3)")
    print(f"  Detected Conditions: {parsed['detected_conditions']}")
    
    assert parsed['detected_severity'] == "MODERATE", "Test 3 FAILED!"
    assert parsed['detected_people_count'] == 3, "Test 3 FAILED!"
    assert "flooding" in parsed['detected_conditions'], "Test 3 FAILED!"
    print("  ✅ PASSED")
    
    # Test 4: Victim ID format
    print("\nTest 4: Verify victim ID format (V-{timestamp})")
    import re
    pattern = r"^V-\d+$"
    assert re.match(pattern, report['victim_id']), "Test 4 FAILED!"
    print(f"  Victim ID: {report['victim_id']}")
    print("  ✅ PASSED")
    
    # Test 5: Timestamp format (ISO 8601)
    print("\nTest 5: Verify timestamp format (ISO 8601)")
    pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
    assert re.match(pattern, report['reported_at']), "Test 5 FAILED!"
    print(f"  Timestamp: {report['reported_at']}")
    print("  ✅ PASSED")
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! ✅")
    print("=" * 60)