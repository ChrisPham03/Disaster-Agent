"""
Standalone REST API Server for Disaster Response Dashboard Testing.

This server provides REST endpoints that the frontend can call directly,
without requiring the full Solace Agent Mesh infrastructure to be running.

Run with: python -m src.api.server
Or: uvicorn src.api.server:app --host 0.0.0.0 --port 5050 --reload
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uvicorn
import uuid
import math

# Initialize FastAPI app
app = FastAPI(
    title="Disaster Response API",
    description="REST API for Disaster Response Command Center",
    version="1.0.0"
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# IN-MEMORY DATA STORES (Replace with database in production)
# ============================================================

priority_queue: List[Dict[str, Any]] = []

teams = {
    "T-Alpha": {
        "team_id": "T-Alpha",
        "name": "Alpha Response Unit",
        "personnel": 6,
        "vehicle": "Heavy Rescue Truck",
        "status": "available",
        "location": {"lat": 13.7400, "lng": 100.5200},
        "assigned_to": None,
        "eta_minutes": None,
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
        "equipment": ["fire_extinguisher", "breathing_apparatus", "thermal_camera", "hose"],
    },
}

inventory = {
    "stretcher": {"total": 15, "available": 15, "allocated": 0},
    "first_aid_kit": {"total": 50, "available": 50, "allocated": 0},
    "hydraulic_cutter": {"total": 4, "available": 4, "allocated": 0},
    "oxygen_tank": {"total": 20, "available": 20, "allocated": 0},
    "defibrillator": {"total": 6, "available": 6, "allocated": 0},
    "life_vest": {"total": 30, "available": 30, "allocated": 0},
    "thermal_blanket": {"total": 100, "available": 100, "allocated": 0},
    "fire_extinguisher": {"total": 20, "available": 20, "allocated": 0},
    "breathing_apparatus": {"total": 10, "available": 10, "allocated": 0},
}


# ============================================================
# PYDANTIC MODELS
# ============================================================

class VictimReportRequest(BaseModel):
    location: Optional[str] = Field(None, description="Location description")
    latitude: Optional[float] = Field(None, description="GPS latitude")
    longitude: Optional[float] = Field(None, description="GPS longitude")
    description: str = Field(..., min_length=5, description="Situation description")
    num_people: int = Field(1, ge=1, description="Number of people affected")
    reporter_contact: Optional[str] = None


class VictimStatusUpdate(BaseModel):
    victim_id: str
    status: str = Field(..., pattern="^(pending|in_progress|resolved)$")


class TeamAssignRequest(BaseModel):
    team_id: str
    victim_id: str
    victim_location: Optional[Dict[str, float]] = None


class ResourceAllocationRequest(BaseModel):
    request_id: Optional[str] = None
    mission_id: Optional[str] = None
    equipment_list: List[Dict[str, Any]]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def analyze_severity(description: str) -> Dict[str, Any]:
    """Analyze description and return severity score."""
    lower_desc = description.lower()
    
    critical = ['unconscious', 'not breathing', 'cardiac', 'severe bleeding', 'crushed', 'trapped', 'fire']
    urgent = ['bleeding', 'fracture', 'broken', 'head injury', 'chest pain', 'collapse']
    serious = ['injured', 'pain', 'cut', 'sprain', 'stuck']
    
    score = 3
    if any(kw in lower_desc for kw in critical):
        score = 9
    elif any(kw in lower_desc for kw in urgent):
        score = 7
    elif any(kw in lower_desc for kw in serious):
        score = 5
    
    # Modifiers
    if any(word in lower_desc for word in ['child', 'baby', 'elderly', 'pregnant']):
        score = min(10, score + 1)
    if any(word in lower_desc for word in ['fire', 'smoke', 'gas leak', 'flood']):
        score = min(10, score + 1)
    
    levels = {10: "CRITICAL", 9: "CRITICAL", 8: "URGENT", 7: "URGENT", 
              6: "SERIOUS", 5: "SERIOUS", 4: "MINOR", 3: "MINOR", 2: "NON-URGENT", 1: "NON-URGENT"}
    
    return {"score": score, "priority_level": levels.get(score, "MINOR")}


def calculate_eta(team_loc: Dict, victim_loc: Dict) -> int:
    """Calculate ETA in minutes based on distance."""
    lat1, lng1 = team_loc["lat"], team_loc["lng"]
    lat2, lng2 = victim_loc.get("lat", lat1), victim_loc.get("lng", lng1)
    dist = math.sqrt((lat2 - lat1)**2 + (lng2 - lng1)**2) * 111  # km
    return max(1, int(dist / 40 * 60))  # 40 km/h average


# ============================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================

@app.get("/api/health")
async def health_check():
    """System health check endpoint."""
    return {
        "status": "ok",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agents": [
            {"name": "OrchestratorAgent", "status": "active"},
            {"name": "SeverityAgent", "status": "active"},
            {"name": "ResourcesAgent", "status": "active"},
            {"name": "RescueAgent", "status": "active"},
        ],
        "queue_size": len(priority_queue),
        "teams_available": len([t for t in teams.values() if t["status"] == "available"])
    }


# ============================================================
# VICTIM MANAGEMENT ENDPOINTS
# ============================================================

@app.post("/api/victim/report")
async def submit_victim_report(request: VictimReportRequest):
    """Submit a new victim/emergency report."""
    
    if not request.location and (request.latitude is None or request.longitude is None):
        raise HTTPException(400, "Location description or coordinates required")
    
    # Generate victim ID
    victim_id = f"V-{uuid.uuid4().hex[:8]}"
    
    # Analyze severity
    severity = analyze_severity(request.description)
    
    # Create entry
    entry = {
        "victim_id": victim_id,
        "score": severity["score"],
        "priority_level": severity["priority_level"],
        "location": {
            "lat": request.latitude or 13.7563,
            "lng": request.longitude or 100.5018,
            "description": request.location or "Unknown location"
        },
        "description": request.description,
        "num_people": request.num_people,
        "status": "pending",
        "color_code": "red" if severity["score"] >= 9 else "orange" if severity["score"] >= 5 else "yellow",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    
    # Add and sort queue
    priority_queue.append(entry)
    priority_queue.sort(key=lambda x: (-x["score"], x["timestamp"]))
    
    # Find position
    position = next((i+1 for i, v in enumerate(priority_queue) if v["victim_id"] == victim_id), -1)
    
    return {
        "status": "success",
        "victim_id": victim_id,
        "severity_score": severity["score"],
        "priority_level": severity["priority_level"],
        "queue_position": position,
        "total_in_queue": len(priority_queue),
        "message": f"Report processed. Victim {victim_id} added at position {position}."
    }


@app.get("/api/victim/queue")
async def get_victim_queue(
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, pattern="^(pending|in_progress|resolved|all)$")
):
    """Get the priority queue of victims."""
    victims = priority_queue
    
    if status and status != "all":
        victims = [v for v in victims if v.get("status") == status]
    
    return {
        "status": "success",
        "victims": victims[:limit],
        "total_victims": len(priority_queue),
        "filtered_count": len(victims[:limit])
    }


@app.post("/api/victim/status")
async def update_victim_status(request: VictimStatusUpdate):
    """Update a victim's status."""
    for victim in priority_queue:
        if victim["victim_id"] == request.victim_id:
            victim["status"] = request.status
            victim["status_updated"] = datetime.now(timezone.utc).isoformat()
            return {
                "status": "success",
                "victim_id": request.victim_id,
                "new_status": request.status
            }
    
    raise HTTPException(404, f"Victim {request.victim_id} not found")


@app.get("/api/victim/{victim_id}")
async def get_victim_details(victim_id: str):
    """Get details for a specific victim."""
    for victim in priority_queue:
        if victim["victim_id"] == victim_id:
            return {"status": "success", "victim": victim}
    
    raise HTTPException(404, f"Victim {victim_id} not found")


# ============================================================
# RESCUE TEAM ENDPOINTS
# ============================================================

@app.get("/api/rescue/teams")
async def get_all_teams(status: Optional[str] = None):
    """Get all rescue teams."""
    team_list = list(teams.values())
    
    if status:
        team_list = [t for t in team_list if t["status"] == status]
    
    return {
        "status": "success",
        "teams": team_list,
        "total": len(teams),
        "available": len([t for t in teams.values() if t["status"] == "available"]),
        "deployed": len([t for t in teams.values() if t["status"] != "available"]),
        "summary": {
            "available": len([t for t in teams.values() if t["status"] == "available"]),
            "en_route": len([t for t in teams.values() if t["status"] == "en_route"]),
            "on_scene": len([t for t in teams.values() if t["status"] == "on_scene"]),
        }
    }


@app.get("/api/rescue/teams/{team_id}")
async def get_team_details(team_id: str):
    """Get details for a specific team."""
    if team_id not in teams:
        raise HTTPException(404, f"Team {team_id} not found")
    
    return {"status": "success", "team": teams[team_id]}


@app.post("/api/rescue/assign")
async def assign_team_to_victim(request: TeamAssignRequest):
    """Assign a rescue team to a victim."""
    if request.team_id not in teams:
        raise HTTPException(404, f"Team {request.team_id} not found")
    
    team = teams[request.team_id]
    
    if team["status"] != "available":
        raise HTTPException(400, f"Team {request.team_id} is not available (status: {team['status']})")
    
    # Find victim
    victim = None
    for v in priority_queue:
        if v["victim_id"] == request.victim_id:
            victim = v
            break
    
    if not victim:
        raise HTTPException(404, f"Victim {request.victim_id} not found")
    
    # Calculate ETA
    victim_loc = request.victim_location or victim.get("location", {})
    eta = calculate_eta(team["location"], victim_loc)
    
    # Update team
    teams[request.team_id]["status"] = "en_route"
    teams[request.team_id]["assigned_to"] = request.victim_id
    teams[request.team_id]["eta_minutes"] = eta
    
    # Update victim
    victim["status"] = "in_progress"
    victim["assigned_team"] = request.team_id
    
    return {
        "status": "success",
        "team_id": request.team_id,
        "assigned_to": request.victim_id,
        "team_status": "en_route",
        "eta_minutes": eta,
        "team_location": team["location"],
        "message": f"Team {team['name']} dispatched. ETA: {eta} minutes."
    }


@app.post("/api/rescue/release")
async def release_team(team_id: str):
    """Release a team from their current assignment."""
    if team_id not in teams:
        raise HTTPException(404, f"Team {team_id} not found")
    
    prev_assignment = teams[team_id]["assigned_to"]
    
    teams[team_id]["status"] = "available"
    teams[team_id]["assigned_to"] = None
    teams[team_id]["eta_minutes"] = None
    
    return {
        "status": "success",
        "team_id": team_id,
        "released_from": prev_assignment,
        "new_status": "available"
    }


# ============================================================
# RESOURCE MANAGEMENT ENDPOINTS
# ============================================================

@app.get("/api/resource/inventory")
async def get_inventory(item: Optional[str] = None):
    """Get current inventory status."""
    if item:
        if item not in inventory:
            raise HTTPException(404, f"Item {item} not found")
        return {"status": "success", "items": {item: inventory[item]}}
    
    return {"status": "success", "items": inventory}


@app.post("/api/resource/allocate")
async def allocate_resources(request: ResourceAllocationRequest):
    """Allocate resources to a mission."""
    mission_id = request.mission_id or f"M-{uuid.uuid4().hex[:8]}"
    
    allocated = []
    shortfall = []
    
    for item in request.equipment_list:
        item_name = item.get("item") or item.get("name")
        quantity = item.get("quantity", 1)
        
        if item_name in inventory:
            available = inventory[item_name]["available"]
            if available >= quantity:
                inventory[item_name]["available"] -= quantity
                inventory[item_name]["allocated"] += quantity
                allocated.append({"item": item_name, "quantity": quantity})
            else:
                if available > 0:
                    inventory[item_name]["available"] = 0
                    inventory[item_name]["allocated"] += available
                    allocated.append({"item": item_name, "quantity": available})
                shortfall.append({"item": item_name, "needed": quantity, "available": available})
    
    return {
        "status": "success",
        "mission_id": mission_id,
        "allocated": len(shortfall) == 0,
        "equipment_assigned": allocated,
        "shortfall": shortfall
    }


@app.post("/api/resource/release")
async def release_resources(mission_id: str):
    """Release resources from a completed mission (simplified - releases all allocations)."""
    # In production, would track which resources are allocated to which mission
    released = []
    for item_name, data in inventory.items():
        if data["allocated"] > 0:
            amount = data["allocated"]
            inventory[item_name]["available"] += amount
            inventory[item_name]["allocated"] = 0
            released.append({"item": item_name, "quantity": amount})
    
    return {
        "status": "success",
        "mission_id": mission_id,
        "released": True,
        "items_returned": released
    }


# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  DISASTER RESPONSE REST API SERVER")
    print("=" * 60)
    print(f"  Starting server on http://0.0.0.0:5050")
    print(f"  API Docs: http://localhost:5050/docs")
    print(f"  OpenAPI: http://localhost:5050/openapi.json")
    print("=" * 60)
    
    uvicorn.run(
        "src.api.server:app",
        host="0.0.0.0",
        port=5050,
        reload=True,
        log_level="info"
    )
