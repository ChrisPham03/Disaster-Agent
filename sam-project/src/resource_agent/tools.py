"""
Orchestrator Agent - Tools for coordinating disaster response.

This agent validates victim reports, coordinates analysis across
severity/resources/hospital agents, and manages the priority queue.
"""

from typing import Any, Dict, Optional, List
from google.adk.tools import ToolContext
from solace_ai_connector.common.log import log
import uuid


async def validate_victim_report(
    location: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    description: Optional[str] = None,
    num_people: Optional[int] = None,
    tool_context: Optional[ToolContext] = None,
    tool_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Validate if a victim report has all required information.
    
    Required fields:
    - Location (either location description OR lat/lng coordinates)
    - Description of the situation
    - Number of people affected
    
    Args:
        location: Location description (optional if lat/lng provided)
        latitude: GPS latitude (optional if location provided)
        longitude: GPS longitude (optional if location provided)
        description: Situation description
        num_people: Number of people affected
        tool_context: Tool invocation context
        tool_config: Tool configuration
        
    Returns:
        Dictionary with validation status and next question to ask
    """
    log_identifier = "[ValidateReport]"
    
    missing_fields = []
    next_question = None
    
    # Check location
    has_coordinates = latitude is not None and longitude is not None
    has_location_desc = location is not None and len(str(location).strip()) > 0
    
    if not has_coordinates and not has_location_desc:
        missing_fields.append("location")
        next_question = "What is your exact location? Please provide either an address/landmark or GPS coordinates."
    
    # Check description
    if not description or len(str(description).strip()) < 5:
        missing_fields.append("description")
        if next_question is None:
            next_question = "Can you describe what happened? Please include details about any injuries, hazards, or urgent conditions."
    
    # Check number of people
    if num_people is None or num_people < 1:
        missing_fields.append("num_people")
        if next_question is None:
            next_question = "How many people need assistance?"
    
    is_valid = len(missing_fields) == 0
    
    if is_valid:
        log.info(f"{log_identifier} Report validation successful - all required fields present")
        return {
            "status": "success",
            "is_valid": True,
            "message": "All required information collected",
            "data": {
                "location": location,
                "latitude": latitude,
                "longitude": longitude,
                "description": description,
                "num_people": num_people
            }
        }
    else:
        log.info(f"{log_identifier} Report incomplete - missing: {', '.join(missing_fields)}")
        return {
            "status": "incomplete",
            "is_valid": False,
            "missing_fields": missing_fields,
            "next_question": next_question,
            "message": f"Missing required information: {', '.join(missing_fields)}"
        }


async def process_validated_report(
    location: str,
    latitude: float,
    longitude: float,
    description: str,
    num_people: int,
    severity_score: int,
    severity_level: str,
    tool_context: Optional[ToolContext] = None,
    tool_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process a validated victim report by coordinating with other agents.
    
    This tool should ONLY be called after:
    1. validate_victim_report returns is_valid=True
    2. call_severity_agent returns a severity score
    
    Args:
        location: Location description
        latitude: GPS latitude
        longitude: GPS longitude
        description: Situation description
        num_people: Number of people affected
        severity_score: Severity score from SeverityAgent (1-10)
        severity_level: Priority level from SeverityAgent (CRITICAL/URGENT/etc)
        tool_context: Tool invocation context
        tool_config: Tool configuration
        
    Returns:
        Dictionary with processing status and victim ID
    """
    log_identifier = "[ProcessReport]"
    
    if not tool_context:
        return {"status": "error", "message": "Tool context required"}
    
    try:
        # Generate unique victim ID
        victim_id = f"V-{uuid.uuid4().hex[:8]}"
        
        log.info(f"{log_identifier} Processing report for {victim_id} with severity {severity_score}/10")
        
        # Get host component
        host_component = getattr(tool_context._invocation_context, "agent", None)
        if host_component:
            host_component = getattr(host_component, "host_component", None)
        
        if not host_component:
            return {"status": "error", "message": "Could not access agent host component"}
        
        # Log immediate location
        log.info(f"{log_identifier} [IMMEDIATE] Location: {latitude}, {longitude}")
        
        # Use the severity score from SeverityAgent
        severity_result = {
            "score": severity_score,
            "priority_level": severity_level,
            "reasoning": "Score provided by SeverityAgent"
        }
        
        # Resources placeholder (in full system, would call ResourcesAgent)
        resources_result = {
            "food": {"priority": "MEDIUM", "quantity": num_people},
            "water": {"priority": "HIGH", "quantity": num_people * 2},
            "medical_supplies": {"priority": "HIGH" if severity_score >= 7 else "MEDIUM", "items": ["first_aid_kit", "bandages"]}
        }
        
        # Hospital needs placeholder
        hospital_result = {
            "bed_type": "ICU" if severity_score >= 9 else "GENERAL",
            "urgency": "IMMEDIATE" if severity_score >= 9 else "STANDARD"
        }
        
        # Get priority queue service
        queue_service = host_component.get_agent_specific_state("queue_service")
        if not queue_service:
            return {"status": "error", "message": "Priority queue service not initialized"}
        
        # Add to priority queue
        queue_result = await queue_service.add_or_update_victim(
            victim_id=victim_id,
            score=severity_score,
            location={
                "lat": latitude, 
                "lng": longitude, 
                "description": location
            },
            description=description,
            resources=resources_result,
            hospital_needs=hospital_result,
            num_people=num_people
        )
        
        # Update statistics
        total = host_component.get_agent_specific_state("total_victims_processed", 0)
        host_component.set_agent_specific_state("total_victims_processed", total + 1)
        
        log.info(f"{log_identifier} Successfully processed {victim_id}, queue position: {queue_result['position']}")
        
        return {
            "status": "success",
            "victim_id": victim_id,
            "severity_score": severity_score,
            "priority_level": severity_level,
            "queue_position": queue_result["position"],
            "total_in_queue": queue_result["total_queue_size"],
            "message": f"Report processed. Victim {victim_id} (severity {severity_score}/10 - {severity_level}) added to priority queue at position {queue_result['position']}. Rescue teams have been notified."
        }
        
    except Exception as e:
        log.error(f"{log_identifier} Error processing report: {e}")
        return {
            "status": "error",
            "message": f"Failed to process report: {str(e)}"
        }


async def get_priority_queue(
    limit: Optional[int] = 20,
    status_filter: Optional[str] = None,
    tool_context: Optional[ToolContext] = None,
    tool_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Get the current priority queue of victims awaiting rescue.
    
    Args:
        limit: Maximum number of victims to return (default 20)
        status_filter: Filter by status ('pending', 'in_progress', 'resolved', 'all')
        tool_context: Tool invocation context
        tool_config: Tool configuration
        
    Returns:
        Dictionary with queue information
    """
    log_identifier = "[GetQueue]"
    
    if not tool_context:
        return {"status": "error", "message": "Tool context required"}
    
    try:
        # Get host component
        host_component = getattr(tool_context._invocation_context, "agent", None)
        if host_component:
            host_component = getattr(host_component, "host_component", None)
        
        if not host_component:
            return {"status": "error", "message": "Could not access agent host component"}
        
        # Get queue service
        queue_service = host_component.get_agent_specific_state("queue_service")
        if not queue_service:
            return {"status": "error", "message": "Priority queue service not initialized"}
        
        # Get queue with filters
        queue_result = await queue_service.get_priority_queue(
            limit=limit or 20,
            status_filter=status_filter
        )
        
        log.info(f"{log_identifier} Retrieved {len(queue_result.get('victims', []))} victims from queue")
        
        return queue_result
        
    except Exception as e:
        log.error(f"{log_identifier} Error getting priority queue: {e}")
        return {
            "status": "error",
            "message": f"Failed to get priority queue: {str(e)}"
        }


async def update_victim_status(
    victim_id: str,
    status: str,
    tool_context: Optional[ToolContext] = None,
    tool_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Update the status of a victim (pending, in_progress, resolved).
    
    Args:
        victim_id: Unique identifier for the victim
        status: New status (pending/in_progress/resolved)
        tool_context: Tool invocation context
        tool_config: Tool configuration
        
    Returns:
        Dictionary with update status
    """
    log_identifier = "[UpdateStatus]"
    
    if not tool_context:
        return {"status": "error", "message": "Tool context required"}
    
    valid_statuses = ["pending", "in_progress", "resolved"]
    if status not in valid_statuses:
        return {
            "status": "error",
            "message": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}"
        }
    
    try:
        # Get host component
        host_component = getattr(tool_context._invocation_context, "agent", None)
        if host_component:
            host_component = getattr(host_component, "host_component", None)
        
        if not host_component:
            return {"status": "error", "message": "Could not access agent host component"}
        
        # Get queue service
        queue_service = host_component.get_agent_specific_state("queue_service")
        if not queue_service:
            return {"status": "error", "message": "Priority queue service not initialized"}
        
        # Update status
        update_result = await queue_service.update_victim_status(victim_id, status)
        
        if update_result.get("success"):
            log.info(f"{log_identifier} Updated {victim_id} status to '{status}'")
            return {
                "status": "success",
                "victim_id": victim_id,
                "new_status": status,
                "message": f"Victim {victim_id} status updated to '{status}'"
            }
        else:
            return {
                "status": "error",
                "victim_id": victim_id,
                "message": update_result.get("message", "Update failed")
            }
        
    except Exception as e:
        log.error(f"{log_identifier} Error updating victim status: {e}")
        return {
            "status": "error",
            "message": f"Failed to update status: {str(e)}"
        }


async def get_victim_details(
    victim_id: str,
    tool_context: Optional[ToolContext] = None,
    tool_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Get detailed information about a specific victim.
    
    Args:
        victim_id: Unique identifier for the victim
        tool_context: Tool invocation context
        tool_config: Tool configuration
        
    Returns:
        Dictionary with victim details
    """
    log_identifier = "[GetVictimDetails]"
    
    if not tool_context:
        return {"status": "error", "message": "Tool context required"}
    
    try:
        # Get host component
        host_component = getattr(tool_context._invocation_context, "agent", None)
        if host_component:
            host_component = getattr(host_component, "host_component", None)
        
        if not host_component:
            return {"status": "error", "message": "Could not access agent host component"}
        
        # Get queue service
        queue_service = host_component.get_agent_specific_state("queue_service")
        if not queue_service:
            return {"status": "error", "message": "Priority queue service not initialized"}
        
        # Get victim details
        victim = await queue_service.get_victim_by_id(victim_id)
        
        if victim:
            log.info(f"{log_identifier} Retrieved details for victim {victim_id}")
            return {
                "status": "success",
                "victim": victim
            }
        else:
            return {
                "status": "error",
                "message": f"Victim {victim_id} not found"
            }
        
    except Exception as e:
        log.error(f"{log_identifier} Error getting victim details: {e}")
        return {
            "status": "error",
            "message": f"Failed to get victim details: {str(e)}"
        }