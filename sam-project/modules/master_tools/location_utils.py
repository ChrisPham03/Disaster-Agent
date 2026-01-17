"""
Location Utilities for Master Agent

Functions for extracting and validating location information from victim input.
"""

import re
from typing import Dict, Any, Optional, Tuple


def extract_location(user_input: str) -> Dict[str, Any]:
    """
    Extract location from natural language input.
    
    Args:
        user_input: Raw text like "I'm at 123 Main St" or "near the old factory on 5th avenue"
                   Can also contain GPS coordinates like "13.7563, 100.5018"
    
    Returns:
        {
            "lat": float or None,
            "lng": float or None,
            "address": str,
            "confidence": str ("high" | "medium" | "low"),
            "raw_input": str
        }
    """
    result = {
        "lat": None,
        "lng": None,
        "address": "",
        "confidence": "low",
        "raw_input": user_input
    }
    
    # Try to extract GPS coordinates
    # Pattern: decimal degrees like "13.7563, 100.5018" or "13.7563 100.5018"
    coord_pattern = r'(-?\d{1,3}\.\d+)[,\s]+(-?\d{1,3}\.\d+)'
    coord_match = re.search(coord_pattern, user_input)
    
    if coord_match:
        try:
            lat = float(coord_match.group(1))
            lng = float(coord_match.group(2))
            
            if validate_coordinates(lat, lng):
                result["lat"] = lat
                result["lng"] = lng
                result["confidence"] = "high"
        except ValueError:
            pass
    
    # Extract address information
    address = _extract_address(user_input)
    result["address"] = address
    
    # Determine confidence based on what we found
    if result["lat"] is not None and result["lng"] is not None:
        result["confidence"] = "high"
    elif address:
        # Check if it's a detailed address
        if _is_detailed_address(address):
            result["confidence"] = "medium"
        else:
            result["confidence"] = "low"
    
    return result


def validate_coordinates(lat: float, lng: float) -> bool:
    """
    Validate GPS coordinates are within valid range.
    
    Args:
        lat: Latitude value
        lng: Longitude value
    
    Returns:
        True if valid (-90 <= lat <= 90 and -180 <= lng <= 180)
    """
    return -90 <= lat <= 90 and -180 <= lng <= 180


def _extract_address(text: str) -> str:
    """
    Extract address from natural language text.
    
    Args:
        text: Raw user input
    
    Returns:
        Extracted address string
    """
    # Remove common prefixes
    prefixes_to_remove = [
        r"i'?m\s+at\s+",
        r"i\s+am\s+at\s+",
        r"we'?re\s+at\s+",
        r"we\s+are\s+at\s+",
        r"located\s+at\s+",
        r"location\s*:?\s*",
        r"address\s*:?\s*",
        r"help!?\s*",
        r"emergency!?\s*",
        r"please\s+help!?\s*",
    ]
    
    cleaned = text.strip()
    for prefix in prefixes_to_remove:
        cleaned = re.sub(prefix, "", cleaned, flags=re.IGNORECASE)
    
    # Remove GPS coordinates if present (we extract those separately)
    cleaned = re.sub(r'-?\d{1,3}\.\d+[,\s]+-?\d{1,3}\.\d+', '', cleaned)
    
    # Clean up extra whitespace
    cleaned = ' '.join(cleaned.split())
    
    return cleaned.strip()


def _is_detailed_address(address: str) -> bool:
    """
    Check if the address appears to be detailed enough.
    
    Args:
        address: Address string
    
    Returns:
        True if address seems detailed (has street number, street name, etc.)
    """
    # Check for street numbers
    has_number = bool(re.search(r'\d+', address))
    
    # Check for common street suffixes
    street_suffixes = [
        'street', 'st', 'avenue', 'ave', 'road', 'rd', 'boulevard', 'blvd',
        'drive', 'dr', 'lane', 'ln', 'way', 'court', 'ct', 'place', 'pl',
        'highway', 'hwy', 'parkway', 'pkwy', 'soi'
    ]
    has_street = any(
        re.search(rf'\b{suffix}\b', address, re.IGNORECASE) 
        for suffix in street_suffixes
    )
    
    # Consider detailed if has number + street, or has 4+ words
    word_count = len(address.split())
    
    return (has_number and has_street) or word_count >= 4


# Test function
if __name__ == "__main__":
    print("=" * 60)
    print("TESTING LOCATION UTILS")
    print("=" * 60)
    
    # Test 1: GPS coordinates
    print("\nTest 1: Extract GPS coordinates")
    result = extract_location("We're at 13.7563, 100.5018")
    print(f"  Input: 'We're at 13.7563, 100.5018'")
    print(f"  Lat: {result['lat']} (expected: 13.7563)")
    print(f"  Lng: {result['lng']} (expected: 100.5018)")
    print(f"  Confidence: {result['confidence']} (expected: high)")
    assert result['lat'] == 13.7563, "Test 1 FAILED!"
    assert result['lng'] == 100.5018, "Test 1 FAILED!"
    assert result['confidence'] == "high", "Test 1 FAILED!"
    print("  ✅ PASSED")
    
    # Test 2: Street address
    print("\nTest 2: Extract street address")
    result = extract_location("I'm at 45 Sukhumvit Road, Bangkok")
    print(f"  Input: 'I'm at 45 Sukhumvit Road, Bangkok'")
    print(f"  Address: '{result['address']}'")
    print(f"  Confidence: {result['confidence']} (expected: medium)")
    assert "45" in result['address'], "Test 2 FAILED!"
    assert "Sukhumvit" in result['address'], "Test 2 FAILED!"
    assert result['confidence'] == "medium", "Test 2 FAILED!"
    print("  ✅ PASSED")
    
    # Test 3: Vague location
    print("\nTest 3: Vague location (low confidence)")
    result = extract_location("near the factory")
    print(f"  Input: 'near the factory'")
    print(f"  Address: '{result['address']}'")
    print(f"  Confidence: {result['confidence']} (expected: low)")
    assert result['confidence'] == "low", "Test 3 FAILED!"
    print("  ✅ PASSED")
    
    # Test 4: Validate coordinates - valid
    print("\nTest 4: Validate valid coordinates")
    valid = validate_coordinates(13.7563, 100.5018)
    print(f"  Coords: (13.7563, 100.5018)")
    print(f"  Valid: {valid} (expected: True)")
    assert valid == True, "Test 4 FAILED!"
    print("  ✅ PASSED")
    
    # Test 5: Validate coordinates - invalid
    print("\nTest 5: Validate invalid coordinates")
    valid = validate_coordinates(91.0, 100.0)  # lat > 90
    print(f"  Coords: (91.0, 100.0)")
    print(f"  Valid: {valid} (expected: False)")
    assert valid == False, "Test 5 FAILED!"
    print("  ✅ PASSED")
    
    # Test 6: Emergency message with address
    print("\nTest 6: Emergency message with address")
    result = extract_location("Help! We're trapped at 123 Main Street, Building A")
    print(f"  Input: 'Help! We're trapped at 123 Main Street, Building A'")
    print(f"  Address: '{result['address']}'")
    print(f"  Confidence: {result['confidence']}")
    assert "123" in result['address'], "Test 6 FAILED!"
    assert "Main Street" in result['address'], "Test 6 FAILED!"
    print("  ✅ PASSED")
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! ✅")
    print("=" * 60)