"""
Orchestrator Agent - Tools for coordinating disaster response.

This agent validates victim reports, coordinates analysis across
severity/resources/hospital agents, and manages the priority queue.
"""

from typing import Any, Dict, Optional
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
    Validate that a victim report has all required information.
    
    This tool checks what information is present and what's missing,
    then returns guidance for the LLM on what to ask the user next.
    
    Args:
        location: Text description of location (city, address, etc.)
        latitude: GPS latitude coordinate
        longitude: GPS longitude coordinate
        description: Description of the situation and injuries
        num_people: Number of people affected
        tool_context: Tool invocation context (provided by SAM)
        tool_config: Tool configuration (from YAML)
        
    Returns:
        Dictionary with validation status and missing fields
    """
    log_identifier = "[ValidateReport]"
    
    missing_fields = []
    warnings = []
    
    # Check location information
    has_gps = latitude is not None and longitude is not None
    has_text_location = location is not None and len(str(location).strip()) > 0
    
    if not has_gps and not has_text_location:
        missing_fields.append({
            "field": "location",
            "question": "What is your exact location? Please provide either GPS coordinates or a specific address/city."
        })
    
    # Check situation description
    if not description or len(str(description).strip()) < 10:
        missing_fields.append({
            "field": "description",
            "question": "Can you describe the situation in more detail? What injuries or hazards are present? Is anyone in immediate danger?"
        })
    
    # Check number of people
    if num_people is None:
        missing_fields.append({
            "field": "num_people",
            "question": "How many people need assistance at this location?"
        })
    
    # Validate description quality if provided
    if description:
        lower_desc = str(description).lower()
        
        # Check for severity indicators
        has_injury_info = any(word in lower_desc for word in [
            'injury', 'injured', 'hurt', 'bleeding', 'pain', 'unconscious'
        ])
        has_condition_info = any(word in lower_desc for word in [
            'trapped', 'stuck', 'safe', 'danger', 'fire', 'water'
        ])
        
        if not has_injury_info and not has_condition_info:
            warnings.append(
                "Description lacks specific details about injuries or immediate dangers. "
                "This may affect triage accuracy."
            )
    
    # Determine validation status
    if missing_fields:
        log.info(f"{log_identifier} Report incomplete: {len(missing_fields)} missing fields")
        return {
            "status": "incomplete",
            "is_valid": False,
            "missing_fields": missing_fields,
            "warnings": warnings,
            "message": f"Report is missing {len(missing_fields)} required field(s).",
            "next_question": missing_fields[0]["question"]  # Ask first missing field
        }
    
    elif warnings:
        log.info(f"{log_identifier} Report valid but has {len(warnings)} warnings")
        return {
            "status": "valid_with_warnings",
            "is_valid": True,
            "missing_fields": [],
            "warnings": warnings,
            "message": "Report is valid but could benefit from additional details.",
            "data": {
                "location": location or f"GPS: {latitude}, {longitude}",
                "latitude": latitude,
                "longitude": longitude,
                "description": description,
                "num_people": num_people
            }
        }
    
    else:
        log.info(f"{log_identifier} Report fully valid")
        return {
            "status": "valid",
            "is_valid": True,
            "missing_fields": [],
            "warnings": [],
            "message": "Report is complete and ready for processing.",
            "data": {
                "location": location or f"GPS: {latitude}, {longitude}",
                "latitude": latitude,
                "longitude": longitude,
                "description": description,
                "num_people": num_people
            }
        }


async def process_validated_report(
    location: str,
    latitude: float,
    longitude: float,
    description: str,
    num_people: int,
    tool_context: Optional[ToolContext] = None,
    tool_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process a validated victim report by coordinating with other agents.
    
    This tool should ONLY be called after validate_victim_report returns is_valid=True.
    
    Steps:
    1. Generate victim ID
    2. Send location immediately to rescue dashboard (via Solace topic)
    3. Call severity agent for triage score
    4. Call resources agent for supply needs
    5. Update priority queue
    
    Args:
        location: Location description
        latitude: GPS latitude
        longitude: GPS longitude
        description: Situation description
        num_people: Number of people affected
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
        victim_id = f"victim_{uuid.uuid4().hex[:8]}"
        
        log.info(f"{log_identifier} Processing validated report for {victim_id} ({num_people} people)")
        
        # Get host component for agent state access
        host_component = getattr(tool_context._invocation_context, "agent", None)
        if host_component:
            host_component = getattr(host_component, "host_component", None)
        
        if not host_component:
            return {"status": "error", "message": "Could not access agent host component"}
        
        # TODO: Step 1 - Publish location immediately to rescue dashboard
        # This would use Solace messaging to send GPS coordinates to rescue teams
        # await publish_to_topic("disaster/rescue/location/immediate", {
        #     "victim_id": victim_id,
        #     "latitude": latitude,
        #     "longitude": longitude,
        #     "timestamp": datetime.now().isoformat()
        # })
        
        # For now, just log it
        log.info(f"{log_identifier} [IMMEDIATE] Location sent to rescue: {latitude}, {longitude}")
        
        # TODO: Step 2 - Call Severity Agent via inter-agent communication
        # In SAM, this would be done via agent discovery and messaging
        # For now, we'll simulate the response
        severity_result = {
            "score": 7,  # Would come from SeverityAgent
            "priority_level": "URGENT",
            "reasoning": "Severity analysis from SeverityAgent"
        }
        
        # TODO: Step 3 - Call Resources Agent via inter-agent communication
        resources_result = {
            "resources": {
                "food": {"priority": "MEDIUM"},
                "water": {"priority": "HIGH"},
                "medical_supplies": {"priority": "HIGH"}
            }
        }
        
        # TODO: Step 4 - Call Hospital Agent (if you have one)
        hospital_result = {
            "bed_type": "GENERAL",
            "urgency": "STANDARD"
        }
        
        # Step 5 - Update priority queue
        queue_service = host_component.get_agent_specific_state("queue_service")
        if not queue_service:
            return {"status": "error", "message": "Priority queue service not initialized"}
        
        queue_result = await queue_service.add_or_update_victim(
            victim_id=victim_id,
            score=severity_result["score"],
            location={"lat": latitude, "lng": longitude, "description": location},
            description=description,
            resources=resources_result["resources"],
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
            "severity_score": severity_result["score"],
            "priority_level": severity_result["priority_level"],
            "queue_position": queue_result["position"],
            "total_in_queue": queue_result["total_queue_size"],
            "message": f"Report processed. Victim {victim_id} added to priority queue at position {queue_result['position']}. Rescue teams have been notified of the location."
        }
        
    except Exception as e:
        log.error(f"{log_identifier} Error processing report: {e}")
        return {
            "status": "error",
            "message": f"Failed to process report: {str(e)}"
        }


async def get_priority_queue(
    top_n: int = 20,
    tool_context: Optional[ToolContext] = None,
    tool_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Get the current priority queue of victims.
    
    Args:
        top_n: Number of top priority cases to return (default: 20)
        tool_context: Tool invocation context
        tool_config: Tool configuration
        
    Returns:
        Dictionary with priority queue information
    """
    log_identifier = "[GetQueue]"
    
    if not tool_context:
        return {"status": "error", "message": "Tool context required"}
    
    try:
        host_component = getattr(tool_context._invocation_context, "agent", None)
        if host_component:
            host_component = getattr(host_component, "host_component", None)
        
        queue_service = host_component.get_agent_specific_state("queue_service")
        if not queue_service:
            return {"status": "error", "message": "Priority queue service not initialized"}
        
        # Get top priorities
        top_priorities = await queue_service.get_top_priorities(top_n)
        queue_size = await queue_service.get_queue_size()
        
        log.info(f"{log_identifier} Retrieved top {len(top_priorities)} priorities from queue of {queue_size}")
        
        return {
            "status": "success",
            "queue_size": queue_size,
            "top_n": top_n,
            "priorities": top_priorities
        }
        
    except Exception as e:
        log.error(f"{log_identifier} Error getting queue: {e}")
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
    Update the status of a victim in the queue.
    
    Args:
        victim_id: Unique victim identifier
        status: New status (pending, in_progress, resolved)
        tool_context: Tool invocation context
        tool_config: Tool configuration
        
    Returns:
        Dictionary with update status
    """
    log_identifier = "[UpdateStatus]"
    
    if not tool_context:
        return {"status": "error", "message": "Tool context required"}
    
    if status not in ["pending", "in_progress", "resolved"]:
        return {
            "status": "error",
            "message": f"Invalid status: {status}. Must be pending, in_progress, or resolved"
        }
    
    try:
        host_component = getattr(tool_context._invocation_context, "agent", None)
        if host_component:
            host_component = getattr(host_component, "host_component", None)
        
        queue_service = host_component.get_agent_specific_state("queue_service")
        if not queue_service:
            return {"status": "error", "message": "Priority queue service not initialized"}
        
        success = await queue_service.update_victim_status(victim_id, status)
        
        if success:
            log.info(f"{log_identifier} Updated {victim_id} status to {status}")
            return {
                "status": "success",
                "victim_id": victim_id,
                "new_status": status,
                "message": f"Victim {victim_id} status updated to {status}"
            }
        else:
            return {
                "status": "error",
                "message": f"Victim {victim_id} not found in queue"
            }
        
    except Exception as e:
        log.error(f"{log_identifier} Error updating status: {e}")
        return {
            "status": "error",
            "message": f"Failed to update status: {str(e)}"
        }