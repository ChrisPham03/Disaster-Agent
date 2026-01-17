"""
Agent-to-Agent Communication Tools for Orchestrator
"""
from typing import Any, Dict, Optional
from google.adk.tools import ToolContext
from solace_ai_connector.common.log import log


async def call_severity_agent(
    description: str,
    victim_id: str,
    num_people: Optional[int] = None,
    tool_context: Optional[ToolContext] = None,
    tool_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Call the SeverityAgent to analyze a victim's situation.
    
    This tool sends a request to the SeverityAgent and waits for its
    severity score response.
    
    Args:
        description: Description of the victim's situation
        victim_id: Unique identifier for the victim
        num_people: Number of people affected (optional)
        tool_context: Tool invocation context from SAM
        tool_config: Tool configuration
        
    Returns:
        Dictionary with severity score and priority level
    """
    log_identifier = "[CallSeverityAgent]"
    
    if not tool_context:
        return {
            "status": "error",
            "message": "Tool context required for agent communication"
        }
    
    try:
        log.info(f"{log_identifier} Sending request to SeverityAgent for victim {victim_id}")
        
        # Get the host component which has the A2A communication capabilities
        host_component = getattr(tool_context._invocation_context, "agent", None)
        if host_component:
            host_component = getattr(host_component, "host_component", None)
        
        if not host_component:
            log.error(f"{log_identifier} Could not access host component")
            return {
                "status": "error",
                "message": "Could not access agent host component"
            }
        
        # Get the A2A service from the host component
        a2a_service = getattr(host_component, "a2a_service", None)
        if not a2a_service:
            log.error(f"{log_identifier} A2A service not available")
            return {
                "status": "error",
                "message": "A2A service not initialized"
            }
        
        # Prepare the request payload for SeverityAgent
        request_payload = {
            "description": description,
            "victim_id": victim_id
        }
        
        if num_people is not None:
            request_payload["num_people"] = num_people
        
        log.info(f"{log_identifier} Request payload: {request_payload}")
        
        # Send the request to SeverityAgent using A2A protocol
        # The target agent name must match exactly: "SeverityAgent"
        response = await a2a_service.send_agent_request(
            target_agent_name="SeverityAgent",
            user_message=f"Analyze this disaster situation: {description}",
            session_id=f"severity_request_{victim_id}",
            timeout_seconds=30
        )
        
        if response and response.get("status") == "success":
            log.info(f"{log_identifier} Received response from SeverityAgent")
            return response
        else:
            log.warning(f"{log_identifier} SeverityAgent returned no valid response")
            # Return a default score if the agent doesn't respond
            return {
                "status": "fallback",
                "score": 5,
                "priority_level": "SERIOUS",
                "reasoning": "Default score - SeverityAgent did not respond",
                "victim_id": victim_id
            }
        
    except Exception as e:
        log.error(f"{log_identifier} Error calling SeverityAgent: {e}")
        # Return a default score on error
        return {
            "status": "error",
            "score": 5,
            "priority_level": "SERIOUS",
            "reasoning": f"Error communicating with SeverityAgent: {str(e)}",
            "victim_id": victim_id
        }