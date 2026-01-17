"""
Navigation Module for Rescue Agent

Provides route planning and arrival time estimation.
Note: Uses mock data for hackathon. Real implementation would use Google Maps API.
"""

import math
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


def get_route(
    origin: Dict[str, float],
    destination: Dict[str, float],
    avoid_hazards: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Get optimal route to victim location.
    
    Args:
        origin: {"lat": float, "lng": float} - rescue team location
        destination: {"lat": float, "lng": float} - victim location
        avoid_hazards: Optional list of hazard types to avoid routes through
    
    Returns:
        {
            "route_id": str,
            "origin": dict,
            "destination": dict,
            "distance_km": float,
            "estimated_time_minutes": int,
            "directions": [
                {"step": int, "instruction": str, "distance_m": int}
            ],
            "hazards_avoided": list,
            "calculated_at": str
        }
    
    Note: For hackathon, uses Haversine formula for distance.
    Real implementation would call Google Maps / OpenStreetMap API.
    """
    avoid_hazards = avoid_hazards or []
    
    # Validate inputs
    if not _validate_location(origin) or not _validate_location(destination):
        return {
            "error": "Invalid coordinates provided",
            "origin": origin,
            "destination": destination
        }
    
    # Calculate distance using Haversine formula
    distance_km = _haversine_distance(
        origin["lat"], origin["lng"],
        destination["lat"], destination["lng"]
    )
    
    # Estimate time based on distance and hazards
    traffic_level = "heavy" if avoid_hazards else "normal"
    eta = estimate_arrival_time(distance_km, traffic_level)
    
    # Generate mock directions
    directions = _generate_directions(origin, destination, distance_km)
    
    # Generate route ID
    route_id = f"R-{int(time.time())}"
    
    return {
        "route_id": route_id,
        "origin": origin,
        "destination": destination,
        "distance_km": round(distance_km, 2),
        "estimated_time_minutes": eta["estimated_minutes"],
        "directions": directions,
        "hazards_avoided": avoid_hazards,
        "calculated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }


def estimate_arrival_time(
    distance_km: float,
    traffic_level: str = "normal"
) -> Dict[str, Any]:
    """
    Estimate arrival time based on distance and traffic.
    
    Args:
        distance_km: Distance in kilometers
        traffic_level: "light" | "normal" | "heavy"
    
    Returns:
        {
            "estimated_minutes": int,
            "traffic_level": str,
            "speed_kmh": int
        }
    
    Speed assumptions:
        - light: 60 km/h
        - normal: 40 km/h
        - heavy: 20 km/h
    """
    # Speed based on traffic level
    speeds = {
        "light": 60,
        "normal": 40,
        "heavy": 20
    }
    
    traffic_level = traffic_level.lower()
    speed_kmh = speeds.get(traffic_level, speeds["normal"])
    
    # Calculate time in minutes
    if speed_kmh > 0 and distance_km > 0:
        time_hours = distance_km / speed_kmh
        estimated_minutes = max(1, round(time_hours * 60))
    else:
        estimated_minutes = 1  # Minimum 1 minute
    
    return {
        "estimated_minutes": estimated_minutes,
        "traffic_level": traffic_level,
        "speed_kmh": speed_kmh
    }


def _haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate distance between two GPS coordinates using Haversine formula.
    
    Returns:
        Distance in kilometers
    """
    # Earth's radius in kilometers
    R = 6371.0
    
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    
    # Haversine formula
    a = math.sin(delta_lat / 2) ** 2 + \
        math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance


def _validate_location(location: Dict[str, float]) -> bool:
    """Validate location has valid lat/lng."""
    if not isinstance(location, dict):
        return False
    
    lat = location.get("lat")
    lng = location.get("lng")
    
    if lat is None or lng is None:
        return False
    
    return -90 <= lat <= 90 and -180 <= lng <= 180


def _generate_directions(
    origin: Dict[str, float],
    destination: Dict[str, float],
    total_distance_km: float
) -> List[Dict[str, Any]]:
    """
    Generate mock directions for the route.
    
    Note: For hackathon demo. Real implementation would use mapping API.
    """
    total_distance_m = int(total_distance_km * 1000)
    
    # Simple mock directions
    directions = [
        {
            "step": 1,
            "instruction": f"Start from rescue station at ({origin['lat']:.4f}, {origin['lng']:.4f})",
            "distance_m": 0
        },
        {
            "step": 2,
            "instruction": "Head towards the incident location",
            "distance_m": int(total_distance_m * 0.3)
        },
        {
            "step": 3,
            "instruction": "Continue on main road",
            "distance_m": int(total_distance_m * 0.5)
        },
        {
            "step": 4,
            "instruction": f"Arrive at destination ({destination['lat']:.4f}, {destination['lng']:.4f})",
            "distance_m": int(total_distance_m * 0.2)
        }
    ]
    
    return directions


def calculate_nearest_station(
    destination: Dict[str, float],
    stations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Find the nearest rescue station to the incident.
    
    Args:
        destination: Victim location {"lat": float, "lng": float}
        stations: List of station dicts with "name", "lat", "lng"
    
    Returns:
        Nearest station with distance added
    """
    if not stations:
        return {"error": "No stations provided"}
    
    nearest = None
    min_distance = float('inf')
    
    for station in stations:
        distance = _haversine_distance(
            station["lat"], station["lng"],
            destination["lat"], destination["lng"]
        )
        
        if distance < min_distance:
            min_distance = distance
            nearest = station.copy()
            nearest["distance_km"] = round(distance, 2)
    
    return nearest


# Test function
if __name__ == "__main__":
    print("=" * 60)
    print("TESTING NAVIGATION")
    print("=" * 60)
    
    # Test 1: Basic route calculation
    print("\nTest 1: Basic route calculation")
    origin = {"lat": 13.7563, "lng": 100.5018}  # Bangkok center
    destination = {"lat": 13.7963, "lng": 100.5518}  # ~6km away
    
    result = get_route(origin, destination)
    print(f"  Route ID: {result['route_id']}")
    print(f"  Distance: {result['distance_km']} km")
    print(f"  ETA: {result['estimated_time_minutes']} minutes")
    print(f"  Directions count: {len(result['directions'])}")
    
    assert result['route_id'].startswith("R-"), "Test 1 FAILED: route_id format"
    assert result['distance_km'] > 0, "Test 1 FAILED: distance should be > 0"
    assert result['estimated_time_minutes'] > 0, "Test 1 FAILED: ETA should be > 0"
    assert len(result['directions']) == 4, "Test 1 FAILED: should have 4 direction steps"
    print("  ✅ PASSED")
    
    # Test 2: Route with hazards to avoid
    print("\nTest 2: Route with hazards to avoid")
    result = get_route(
        origin=origin,
        destination=destination,
        avoid_hazards=["flooding", "road_closure"]
    )
    
    print(f"  Hazards avoided: {result['hazards_avoided']}")
    print(f"  ETA (with hazards): {result['estimated_time_minutes']} minutes")
    
    assert result['hazards_avoided'] == ["flooding", "road_closure"], "Test 2 FAILED: hazards"
    # With hazards, traffic is "heavy", so ETA should be longer
    print("  ✅ PASSED")
    
    # Test 3: Estimate arrival time - light traffic
    print("\nTest 3: Estimate arrival time - light traffic")
    eta = estimate_arrival_time(distance_km=12.0, traffic_level="light")
    
    print(f"  Distance: 12 km")
    print(f"  Speed: {eta['speed_kmh']} km/h (expected: 60)")
    print(f"  ETA: {eta['estimated_minutes']} minutes (expected: 12)")
    
    assert eta['speed_kmh'] == 60, "Test 3 FAILED: speed"
    assert eta['estimated_minutes'] == 12, f"Test 3 FAILED: ETA expected 12, got {eta['estimated_minutes']}"
    print("  ✅ PASSED")
    
    # Test 4: Estimate arrival time - heavy traffic
    print("\nTest 4: Estimate arrival time - heavy traffic")
    eta = estimate_arrival_time(distance_km=10.0, traffic_level="heavy")
    
    print(f"  Distance: 10 km")
    print(f"  Speed: {eta['speed_kmh']} km/h (expected: 20)")
    print(f"  ETA: {eta['estimated_minutes']} minutes (expected: 30)")
    
    assert eta['speed_kmh'] == 20, "Test 4 FAILED: speed"
    assert eta['estimated_minutes'] == 30, f"Test 4 FAILED: ETA expected 30, got {eta['estimated_minutes']}"
    print("  ✅ PASSED")
    
    # Test 5: Haversine distance calculation
    print("\nTest 5: Haversine distance (Bangkok to Pattaya ~147km)")
    bangkok = {"lat": 13.7563, "lng": 100.5018}
    pattaya = {"lat": 12.9236, "lng": 100.8825}
    
    distance = _haversine_distance(
        bangkok["lat"], bangkok["lng"],
        pattaya["lat"], pattaya["lng"]
    )
    
    print(f"  Calculated distance: {distance:.1f} km")
    print(f"  Expected: ~100-150 km")
    
    assert 100 < distance < 150, f"Test 5 FAILED: distance {distance} not in expected range"
    print("  ✅ PASSED")
    
    # Test 6: Invalid coordinates
    print("\nTest 6: Invalid coordinates handling")
    result = get_route(
        origin={"lat": 200, "lng": 100},  # Invalid lat > 90
        destination=destination
    )
    
    assert "error" in result, "Test 6 FAILED: should return error for invalid coordinates"
    print(f"  Error: {result['error']}")
    print("  ✅ PASSED")
    
    # Test 7: Find nearest station
    print("\nTest 7: Find nearest rescue station")
    stations = [
        {"name": "Station Alpha", "lat": 13.7600, "lng": 100.5100},
        {"name": "Station Bravo", "lat": 13.8000, "lng": 100.6000},
        {"name": "Station Charlie", "lat": 13.7000, "lng": 100.4500}
    ]
    incident = {"lat": 13.7563, "lng": 100.5018}
    
    nearest = calculate_nearest_station(incident, stations)
    
    print(f"  Incident location: {incident}")
    print(f"  Nearest station: {nearest['name']}")
    print(f"  Distance: {nearest['distance_km']} km")
    
    assert nearest['name'] == "Station Alpha", f"Test 7 FAILED: expected Station Alpha, got {nearest['name']}"
    print("  ✅ PASSED")
    
    # Test 8: Timestamp format
    print("\nTest 8: Timestamp format (ISO 8601)")
    result = get_route(origin, destination)
    
    import re
    pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
    assert re.match(pattern, result['calculated_at']), "Test 8 FAILED: timestamp format"
    print(f"  Timestamp: {result['calculated_at']}")
    print("  ✅ PASSED")
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! ✅")
    print("=" * 60)