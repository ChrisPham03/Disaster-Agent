"""
Priority Queue Service for Orchestrator Agent.

This service manages the persistent priority queue of disaster victims,
storing it in SAM's artifact service for persistence across restarts.
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from solace_ai_connector.common.log import log


class PriorityQueueService:
    """
    Service for managing the disaster response priority queue.
    
    Uses SAM's artifact service to persist the queue, ensuring
    data survives agent restarts.
    """
    
    def __init__(self, artifact_service, app_name: str):
        """
        Initialize the priority queue service.
        
        Args:
            artifact_service: SAM's artifact service instance
            app_name: Application name for artifact storage
        """
        self.artifact_service = artifact_service
        self.app_name = app_name
        self.user_id = "system"  # System-level storage
        self.queue_filename = "disaster_priority_queue.json"
        self.queue_cache: List[Dict[str, Any]] = []
        self.log_identifier = "[PriorityQueueService]"
        
        log.info(f"{self.log_identifier} Initialized with artifact service")
    
    async def load_queue(self) -> List[Dict[str, Any]]:
        """
        Load the priority queue from persistent storage.
        
        Returns:
            List of victim entries, sorted by priority
        """
        try:
            # Attempt to load from artifact storage
            result = await self.artifact_service.load_artifact(
                app_name=self.app_name,
                user_id=self.user_id,
                filename=self.queue_filename
            )
            
            if result and result.get("content"):
                queue_data = json.loads(result["content"])
                self.queue_cache = queue_data
                log.info(f"{self.log_identifier} Loaded {len(queue_data)} items from persistent storage")
                return queue_data
            else:
                log.info(f"{self.log_identifier} No existing queue found, starting fresh")
                self.queue_cache = []
                return []
                
        except Exception as e:
            log.warning(f"{self.log_identifier} Error loading queue: {e}, starting fresh")
            self.queue_cache = []
            return []
    
    async def save_queue(self) -> bool:
        """
        Save the current priority queue to persistent storage.
        
        Returns:
            True if save successful, False otherwise
        """
        try:
            # Convert queue to JSON
            content = json.dumps(self.queue_cache, indent=2, default=str)
            
            # Save using artifact service helper
            from solace_agent_mesh.agent.utils.artifact_helpers import save_artifact_with_metadata
            
            result = await save_artifact_with_metadata(
                artifact_service=self.artifact_service,
                app_name=self.app_name,
                user_id=self.user_id,
                session_id=None,  # System-level, not session-specific
                filename=self.queue_filename,
                content_bytes=content.encode('utf-8'),
                mime_type="application/json",
                metadata_dict={
                    "description": "Disaster response priority queue",
                    "queue_size": len(self.queue_cache),
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "top_score": self.queue_cache[0]["score"] if self.queue_cache else None
                },
                timestamp=datetime.now(timezone.utc)
            )
            
            success = result.get("status") == "success"
            if success:
                log.info(f"{self.log_identifier} Saved {len(self.queue_cache)} items to persistent storage")
            else:
                log.error(f"{self.log_identifier} Failed to save queue: {result.get('message')}")
            
            return success
            
        except Exception as e:
            log.error(f"{self.log_identifier} Error saving queue: {e}")
            return False
    
    async def add_or_update_victim(
        self,
        victim_id: str,
        score: int,
        location: Dict[str, float],
        description: str,
        resources: Dict[str, Any],
        hospital_needs: Dict[str, Any],
        num_people: int = 1
    ) -> Dict[str, Any]:
        """
        Add a new victim to the queue or update an existing entry.
        
        Args:
            victim_id: Unique identifier
            score: Severity score (1-10)
            location: {"lat": float, "lng": float}
            description: Situation description
            resources: Resource needs from resources agent
            hospital_needs: Hospital needs assessment
            num_people: Number of people affected
            
        Returns:
            Dictionary with updated queue info
        """
        # Ensure queue is loaded
        if not self.queue_cache:
            await self.load_queue()
        
        # Check if victim already exists
        existing_idx = next(
            (i for i, v in enumerate(self.queue_cache) if v["victim_id"] == victim_id),
            None
        )
        
        # Create queue entry
        queue_entry = {
            "victim_id": victim_id,
            "score": score,
            "location": location,
            "description": description,
            "resources": resources,
            "hospital_needs": hospital_needs,
            "num_people": num_people,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "color_code": self._get_color_code(score),
            "status": "pending"  # pending, in_progress, resolved
        }
        
        if existing_idx is not None:
            # Update existing entry
            self.queue_cache[existing_idx] = queue_entry
            log.info(f"{self.log_identifier} Updated existing entry for victim {victim_id}")
        else:
            # Add new entry
            self.queue_cache.append(queue_entry)
            log.info(f"{self.log_identifier} Added new entry for victim {victim_id}")
        
        # Sort queue: higher score first, then earlier timestamp
        self.queue_cache.sort(key=lambda x: (-x["score"], x["timestamp"]))
        
        # Save to persistent storage
        await self.save_queue()
        
        return {
            "victim_id": victim_id,
            "score": score,
            "position": self._get_position(victim_id),
            "total_queue_size": len(self.queue_cache)
        }
    
    async def get_top_priorities(self, n: int = 20) -> List[Dict[str, Any]]:
        """
        Get the top N highest priority victims from the queue.
        
        Args:
            n: Number of top priorities to return
            
        Returns:
            List of top N victim entries
        """
        if not self.queue_cache:
            await self.load_queue()
        
        return self.queue_cache[:n]
    
    async def get_queue_size(self) -> int:
        """Get the total number of victims in the queue."""
        if not self.queue_cache:
            await self.load_queue()
        
        return len(self.queue_cache)
    
    async def update_victim_status(self, victim_id: str, status: str) -> bool:
        """
        Update the status of a victim (pending, in_progress, resolved).
        
        Args:
            victim_id: Victim identifier
            status: New status value
            
        Returns:
            True if updated successfully
        """
        if not self.queue_cache:
            await self.load_queue()
        
        for entry in self.queue_cache:
            if entry["victim_id"] == victim_id:
                entry["status"] = status
                entry["status_updated"] = datetime.now(timezone.utc).isoformat()
                await self.save_queue()
                log.info(f"{self.log_identifier} Updated victim {victim_id} status to {status}")
                return True
        
        log.warning(f"{self.log_identifier} Victim {victim_id} not found for status update")
        return False
    
    async def remove_victim(self, victim_id: str) -> bool:
        """
        Remove a victim from the queue (e.g., after rescue completed).
        
        Args:
            victim_id: Victim identifier
            
        Returns:
            True if removed successfully
        """
        if not self.queue_cache:
            await self.load_queue()
        
        original_size = len(self.queue_cache)
        self.queue_cache = [v for v in self.queue_cache if v["victim_id"] != victim_id]
        
        if len(self.queue_cache) < original_size:
            await self.save_queue()
            log.info(f"{self.log_identifier} Removed victim {victim_id} from queue")
            return True
        else:
            log.warning(f"{self.log_identifier} Victim {victim_id} not found for removal")
            return False
    
    def _get_color_code(self, score: int) -> str:
        """Get color code based on severity score."""
        if score >= 8:
            return "red"
        elif score >= 5:
            return "orange"
        else:
            return "yellow"
    
    def _get_position(self, victim_id: str) -> int:
        """Get the position of a victim in the queue (1-indexed)."""
        for i, entry in enumerate(self.queue_cache):
            if entry["victim_id"] == victim_id:
                return i + 1
        return -1