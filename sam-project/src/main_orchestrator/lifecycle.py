"""
Lifecycle functions for the Orchestrator Agent.

Lifecycle functions run at specific points in the agent's lifetime:
- initialize: Run once when agent starts (setup resources)
- cleanup: Run once when agent stops (cleanup resources)

These are configured in the YAML file under:
  agent_init_function: (calls initialize)
  agent_cleanup_function: (calls cleanup)
"""

from typing import Any
from pydantic import BaseModel, Field
from solace_ai_connector.common.log import log
from .services.priority_queue_service import PriorityQueueService


class OrchestratorInitConfig(BaseModel):
    """
    Configuration model for Orchestrator initialization.
    
    This validates the config passed from the YAML file.
    """
    startup_message: str = Field(
        default="Orchestrator Agent is ready to coordinate disaster response!",
        description="Message to log on startup"
    )
    max_queue_size: int = Field(
        default=1000,
        description="Maximum size of priority queue"
    )


def initialize_orchestrator_agent(
    host_component: Any,
    init_config: OrchestratorInitConfig
):
    """
    Initialize the Orchestrator Agent with priority queue service.
    
    This function is called ONCE when the agent starts up.
    It sets up any resources, services, or state that the agent needs.
    
    Args:
        host_component: The agent host component (gives access to agent state)
        init_config: Validated configuration from YAML file
    """
    log_identifier = f"[{host_component.agent_name}:init]"
    log.info(f"{log_identifier} Starting Orchestrator initialization...")
    
    try:
        # Get artifact service from the agent's context
        # This is provided by SAM automatically
        artifact_service = host_component.artifact_service
        app_name = host_component.app_name
        
        if not artifact_service:
            raise ValueError("Artifact service not available - ensure it's configured in YAML")
        
        # Initialize the priority queue service
        queue_service = PriorityQueueService(
            artifact_service=artifact_service,
            app_name=app_name
        )
        
        # Store the service in agent-specific state
        # This makes it available to all tools via tool_context
        host_component.set_agent_specific_state("queue_service", queue_service)
        
        # Store configuration
        host_component.set_agent_specific_state("config", {
            "max_queue_size": init_config.max_queue_size
        })
        
        # Initialize tracking for pending requests (victims being analyzed)
        host_component.set_agent_specific_state("pending_requests", {})
        
        # Log startup message
        log.info(f"{log_identifier} {init_config.startup_message}")
        
        # Store initialization metadata
        host_component.set_agent_specific_state("initialized_at", "now")
        host_component.set_agent_specific_state("total_victims_processed", 0)
        
        log.info(f"{log_identifier} Orchestrator initialization completed successfully")
        
    except Exception as e:
        log.error(f"{log_identifier} Failed to initialize Orchestrator: {e}")
        raise


def cleanup_orchestrator_agent(host_component: Any):
    """
    Clean up Orchestrator Agent resources.
    
    This function is called ONCE when the agent shuts down.
    It cleans up any resources to prevent memory leaks.
    
    Args:
        host_component: The agent host component
    """
    log_identifier = f"[{host_component.agent_name}:cleanup]"
    log.info(f"{log_identifier} Starting Orchestrator cleanup...")
    
    try:
        # Get the queue service
        queue_service = host_component.get_agent_specific_state("queue_service")
        
        if queue_service:
            # No async cleanup needed for artifact-based storage
            # Just log final statistics
            log.info(f"{log_identifier} Priority queue service cleaned up")
        
        # Log final statistics
        total_processed = host_component.get_agent_specific_state("total_victims_processed", 0)
        log.info(f"{log_identifier} Orchestrator processed {total_processed} victims during its lifetime")
        
        log.info(f"{log_identifier} Orchestrator cleanup completed successfully")
        
    except Exception as e:
        log.error(f"{log_identifier} Error during cleanup: {e}")