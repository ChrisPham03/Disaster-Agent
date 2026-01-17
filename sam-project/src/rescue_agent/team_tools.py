"""
Rescue Team Management Tools

Provides real-time tracking and management of rescue teams,
including location updates, assignments, and status tracking.
"""

from typing import Any, Dict, Optional, List
from datetime import datetime, timezone
from google.adk.tools import ToolContext
from solace_ai_connector.common.log import log
import math

# In-memory team storage (use database in production)
_teams: Dict[str, Dict[str, Any]] = {
    "T-Alpha": {
        "team_id": "T-Alpha",
        "name": "Alpha Response Unit",
        "personnel": 6,
        "vehicle": "Heavy Rescue Truck",
        "status": "available",
        "location": {"lat": 13.7400, "lng": 100.5200},
        "assigned_to": None,
        "eta_minutes": None,
        "last_update": datetime.now(timezone.utc).isoformat(),
        "equipment": ["hydraulic_cutter", "airbag_lifter", "stretcher", "first_aid_kit"],
    },
    "T-Bravo": {
        "team_id": "T-Bravo",
        "name": "Bravo Medical Team",
        "personnel": 4,
        "vehicle": "Ambulance Unit",
        "status": "available",
        "location": {"lat": 13.7350, "lng": 100.5150},
        "assigned_to": None,
        "eta_minutes": None,
        "last_update": datetime.now(timezone.utc).isoformat(),
        "equipment": ["defibrillator", "oxygen_tank", "stretcher", "first_aid_kit", "iv_kit"],
    },
    "T-Charlie": {
        "team_id": "T-Charlie",
        "name": "Charlie SAR Team",
        "personnel": 8,
        "vehicle": "Rescue Boat + Truck",
        "status": "available",
        "location": {"lat": 13.7450, "lng": 100.5250},
        "assigned_to": None,
        "eta_minutes": None,
        "last_update": datetime.now(timezone.utc).isoformat(),
        "equipment": ["life_vest", "rescue_boat", "rope", "thermal_blanket", "first_aid_kit"],
    },
    "T-Delta": {
        "team_id": "T-Delta",
        "name": "Delta Fire Response",
        "personnel": 5,
        "vehicle": "Fire Engine",
        "status": "available",
        "location": {"lat": 13.7500, "lng": 100.5100},
        "assigned_to": None,
        "eta_minutes": None,
        "last_update": datetime.now(timezone.utc).isoformat(),
        "equipment": ["fire_extinguisher", "breathing_apparatus", "thermal_camera", "hose"],
    },
}


def _calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance between two coordinates in kilometers using Haversine formula."""
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


def _estimate_eta(distance_km: float, status: str = "en_route") -> int:
    """Estimate arrival time in minutes based on distance and conditions."""
    # Average speed: 40 km/h in urban emergency conditions
    avg_speed_kmh = 40
    base_time = (distance_km / avg_speed_kmh) * 60  # Convert to minutes
    
    # Add buffer for traffic, obstacles
    buffer = base_time * 0.2
    
    return max(1, int(base_time + buffer))


async def get_all_teams(
    status_filter: Optional[str] = None,
    tool_context: Optional[ToolContext] = None,
    tool_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Get status of all rescue teams.
    
    Args:
        status_filter: Optional filter by status ('available', 'en_route', 'on_scene')
        tool_context: Tool invocation context
        tool_config: Tool configuration
        
    Returns:
        Dictionary with list of teams and summary stats
    """
    log_identifier = "[GetAllTeams]"
    
    teams = list(_teams.values())
    
    if status_filter:
        teams = [t for t in teams if t["status"] == status_filter]
    
    available_count = len([t for t in _teams.values() if t["status"] == "available"])
    deployed_count = len([t for t in _teams.values() if t["status"] != "available"])
    
    log.info(f"{log_identifier} Retrieved {len(teams)} teams (filter: {status_filter})")
    
    return {
        "status": "success",
        "teams": teams,
        "total": len(_teams),
        "available": available_count,
        "deployed": deployed_count,
        "summary": {
            "available": available_count,
            "en_route": len([t for t in _teams.values() if t["status"] == "en_route"]),
            "on_scene": len([t for t in _teams.values() if t["status"] == "on_scene"]),
        }
    }


async def get_team_details(
    team_id: str,
    tool_context: Optional[ToolContext] = None,
    tool_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Get detailed information about a specific team.
    
    Args:
        team_id: Unique team identifier
        tool_context: Tool invocation context
        tool_config: Tool configuration
        
    Returns:
        Dictionary with team details
    """
    log_identifier = "[GetTeamDetails]"
    
    if team_id not in _teams:
        log.warning(f"{log_identifier} Team {team_id} not found")
        return {
            "status": "error",
            "message": f"Team {team_id} not found"
        }
    
    team = _teams[team_id]
    log.info(f"{log_identifier} Retrieved details for team {team_id}")
    
    return {
        "status": "success",
        "team": team
    }


async def update_team_location(
    team_id: str,
    latitude: float,
    longitude: float,
    tool_context: Optional[ToolContext] = None,
    tool_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Update a team's GPS location (for real-time tracking).
    
    Args:
        team_id: Unique team identifier
        latitude: New GPS latitude
        longitude: New GPS longitude
        tool_context: Tool invocation context
        tool_config: Tool configuration
        
    Returns:
        Dictionary with updated location
    """
    log_identifier = "[UpdateTeamLocation]"
    
    if team_id not in _teams:
        log.warning(f"{log_identifier} Team {team_id} not found")
        return {
            "status": "error",
            "message": f"Team {team_id} not found"
        }
    
    old_location = _teams[team_id]["location"]
    _teams[team_id]["location"] = {"lat": latitude, "lng": longitude}
    _teams[team_id]["last_update"] = datetime.now(timezone.utc).isoformat()
    
    # If team is assigned, recalculate ETA
    if _teams[team_id]["assigned_to"]:
        # Would need victim location here - simplified for now
        log.info(f"{log_identifier} Team {team_id} location updated, ETA recalculation needed")
    
    log.info(f"{log_identifier} Team {team_id} location updated: ({latitude}, {longitude})")
    
    return {
        "status": "success",
        "team_id": team_id,
        "previous_location": old_location,
        "new_location": _teams[team_id]["location"],
        "timestamp": _teams[team_id]["last_update"]
    }


async def assign_team_to_victim(
    team_id: str,
    victim_id: str,
    victim_location: Optional[Dict[str, float]] = None,
    tool_context: Optional[ToolContext] = None,
    tool_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Assign a rescue team to a victim.
    
    Args:
        team_id: Unique team identifier
        victim_id: Victim identifier to assign to
        victim_location: Optional dict with lat/lng of victim
        tool_context: Tool invocation context
        tool_config: Tool configuration
        
    Returns:
        Dictionary with assignment details including ETA
    """
    log_identifier = "[AssignTeam]"
    
    if team_id not in _teams:
        log.warning(f"{log_identifier} Team {team_id} not found")
        return {
            "status": "error",
            "message": f"Team {team_id} not found"
        }
    
    team = _teams[team_id]
    
    if team["status"] != "available":
        log.warning(f"{log_identifier} Team {team_id} is not available (status: {team['status']})")
        return {
            "status": "error",
            "message": f"Team {team_id} is not available. Current status: {team['status']}",
            "current_assignment": team["assigned_to"]
        }
    
    # Calculate ETA if victim location provided
    eta_minutes = None
    distance_km = None
    if victim_location:
        distance_km = _calculate_distance(
            team["location"]["lat"], team["location"]["lng"],
            victim_location["lat"], victim_location["lng"]
        )
        eta_minutes = _estimate_eta(distance_km)
    
    # Update team status
    _teams[team_id]["status"] = "en_route"
    _teams[team_id]["assigned_to"] = victim_id
    _teams[team_id]["eta_minutes"] = eta_minutes
    _teams[team_id]["last_update"] = datetime.now(timezone.utc).isoformat()
    
    log.info(f"{log_identifier} Team {team_id} assigned to victim {victim_id}, ETA: {eta_minutes} min")
    
    return {
        "status": "success",
        "team_id": team_id,
        "assigned_to": victim_id,
        "team_status": "en_route",
        "distance_km": round(distance_km, 2) if distance_km else None,
        "eta_minutes": eta_minutes,
        "team_location": team["location"],
        "message": f"Team {team['name']} dispatched to victim {victim_id}. ETA: {eta_minutes} minutes."
    }


async def update_team_status(
    team_id: str,
    status: str,
    tool_context: Optional[ToolContext] = None,
    tool_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Update a team's operational status.
    
    Args:
        team_id: Unique team identifier
        status: New status ('available', 'en_route', 'on_scene', 'returning')
        tool_context: Tool invocation context
        tool_config: Tool configuration
        
    Returns:
        Dictionary with status update result
    """
    log_identifier = "[UpdateTeamStatus]"
    
    valid_statuses = ["available", "en_route", "on_scene", "returning"]
    
    if team_id not in _teams:
        return {"status": "error", "message": f"Team {team_id} not found"}
    
    if status not in valid_statuses:
        return {
            "status": "error",
            "message": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}"
        }
    
    old_status = _teams[team_id]["status"]
    _teams[team_id]["status"] = status
    _teams[team_id]["last_update"] = datetime.now(timezone.utc).isoformat()
    
    # If team is now available, clear assignment
    if status == "available":
        _teams[team_id]["assigned_to"] = None
        _teams[team_id]["eta_minutes"] = None
    
    # If on_scene, set ETA to 0
    if status == "on_scene":
        _teams[team_id]["eta_minutes"] = 0
    
    log.info(f"{log_identifier} Team {team_id} status changed: {old_status} -> {status}")
    
    return {
        "status": "success",
        "team_id": team_id,
        "previous_status": old_status,
        "new_status": status,
        "timestamp": _teams[team_id]["last_update"]
    }


async def release_team(
    team_id: str,
    tool_context: Optional[ToolContext] = None,
    tool_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Release a team from their current assignment (mission complete).
    
    Args:
        team_id: Unique team identifier
        tool_context: Tool invocation context
        tool_config: Tool configuration
        
    Returns:
        Dictionary with release status
    """
    log_identifier = "[ReleaseTeam]"
    
    if team_id not in _teams:
        return {"status": "error", "message": f"Team {team_id} not found"}
    
    team = _teams[team_id]
    previous_assignment = team["assigned_to"]
    
    _teams[team_id]["status"] = "available"
    _teams[team_id]["assigned_to"] = None
    _teams[team_id]["eta_minutes"] = None
    _teams[team_id]["last_update"] = datetime.now(timezone.utc).isoformat()
    
    log.info(f"{log_identifier} Team {team_id} released from assignment {previous_assignment}")
    
    return {
        "status": "success",
        "team_id": team_id,
        "released_from": previous_assignment,
        "new_status": "available",
        "message": f"Team {team['name']} is now available for new assignments."
    }


async def get_nearest_available_team(
    victim_location: Dict[str, float],
    required_equipment: Optional[List[str]] = None,
    tool_context: Optional[ToolContext] = None,
    tool_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Find the nearest available team to a victim location.
    
    Args:
        victim_location: Dict with lat/lng of victim
        required_equipment: Optional list of required equipment items
        tool_context: Tool invocation context
        tool_config: Tool configuration
        
    Returns:
        Dictionary with nearest team info and ETA
    """
    log_identifier = "[NearestTeam]"
    
    available_teams = [t for t in _teams.values() if t["status"] == "available"]
    
    if not available_teams:
        log.warning(f"{log_identifier} No available teams")
        return {
            "status": "error",
            "message": "No teams currently available"
        }
    
    # Filter by equipment if specified
    if required_equipment:
        available_teams = [
            t for t in available_teams
            if all(eq in t.get("equipment", []) for eq in required_equipment)
        ]
        if not available_teams:
            log.warning(f"{log_identifier} No teams with required equipment: {required_equipment}")
            return {
                "status": "error",
                "message": f"No available teams with required equipment: {required_equipment}"
            }
    
    # Calculate distances and find nearest
    teams_with_distance = []
    for team in available_teams:
        distance = _calculate_distance(
            team["location"]["lat"], team["location"]["lng"],
            victim_location["lat"], victim_location["lng"]
        )
        eta = _estimate_eta(distance)
        teams_with_distance.append({
            "team": team,
            "distance_km": round(distance, 2),
            "eta_minutes": eta
        })
    
    # Sort by distance
    teams_with_distance.sort(key=lambda x: x["distance_km"])
    nearest = teams_with_distance[0]
    
    log.info(f"{log_identifier} Nearest team: {nearest['team']['team_id']} ({nearest['distance_km']} km)")
    
    return {
        "status": "success",
        "nearest_team": nearest["team"],
        "distance_km": nearest["distance_km"],
        "eta_minutes": nearest["eta_minutes"],
        "alternatives": teams_with_distance[1:3] if len(teams_with_distance) > 1 else []
    }


# Reset function for testing
def _reset_teams():
    """Reset all teams to available status."""
    for team_id in _teams:
        _teams[team_id]["status"] = "available"
        _teams[team_id]["assigned_to"] = None
        _teams[team_id]["eta_minutes"] = None
        _teams[team_id]["last_update"] = datetime.now(timezone.utc).isoformat()
