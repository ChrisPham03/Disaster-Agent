"""
Severity Agent - Tools for analyzing disaster victim severity.

This agent analyzes victim descriptions and assigns severity scores 1-10
for emergency triage prioritization.
"""

from typing import Any, Dict, Optional
from google.adk.tools import ToolContext
from solace_ai_connector.common.log import log


async def analyze_severity(
    description: str,
    victim_id: str,
    tool_context: Optional[ToolContext] = None,
    tool_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyze victim situation and assign severity score 1-10.
    
    Scoring Criteria:
    - 9-10: CRITICAL - Immediate life threat
    - 7-8: URGENT - Serious injuries needing care within 1 hour
    - 5-6: SERIOUS - Moderate injuries needing care within 4 hours
    - 3-4: MINOR - Can wait 8+ hours
    - 1-2: NON-URGENT - Uninjured but needs assistance
    
    Args:
        description: Description of victim's current situation
        victim_id: Unique identifier for the victim
        tool_context: Tool invocation context (provided by SAM)
        tool_config: Tool configuration (from YAML)
        
    Returns:
        Dictionary with severity score, reasoning, and keywords
    """
    log_identifier = "[SeverityAnalysis]"
    log.info(f"{log_identifier} Analyzing severity for victim {victim_id}")
    
    if not description or len(description.strip()) < 5:
        return {
            "status": "error",
            "victim_id": victim_id,
            "message": "Description too short for analysis"
        }
    
    try:
        lower_desc = description.lower()
        
        # Define keyword categories for severity assessment
        critical_keywords = [
            'unconscious', 'not breathing', 'no pulse', 'severe bleeding',
            'cardiac arrest', 'heart attack', 'stroke', 'severe burns',
            'multiple injuries', 'crushed', 'impaled'
        ]
        
        urgent_keywords = [
            'bleeding', 'fracture', 'broken bone', 'chest pain',
            'difficulty breathing', 'severe pain', 'head injury',
            'internal bleeding', 'moderate burns', 'deep cut'
        ]
        
        serious_keywords = [
            'injured', 'pain', 'cut', 'laceration', 'sprain',
            'minor burn', 'bruised', 'trapped', 'stuck'
        ]
        
        minor_keywords = [
            'bruise', 'scratch', 'anxiety', 'scared', 'shaken',
            'minor injury', 'superficial'
        ]
        
        # Calculate base score from keywords
        base_score = 2  # Default: non-urgent
        identified_keywords = []
        
        if any(kw in lower_desc for kw in critical_keywords):
            base_score = 9
            identified_keywords.extend([kw for kw in critical_keywords if kw in lower_desc])
        elif any(kw in lower_desc for kw in urgent_keywords):
            base_score = 7
            identified_keywords.extend([kw for kw in urgent_keywords if kw in lower_desc])
        elif any(kw in lower_desc for kw in serious_keywords):
            base_score = 5
            identified_keywords.extend([kw for kw in serious_keywords if kw in lower_desc])
        elif any(kw in lower_desc for kw in minor_keywords):
            base_score = 3
            identified_keywords.extend([kw for kw in minor_keywords if kw in lower_desc])
        
        # Apply modifiers based on additional risk factors
        final_score = base_score
        modifiers = []
        
        # Vulnerability modifiers
        if any(word in lower_desc for word in ['child', 'baby', 'infant', 'toddler']):
            final_score = min(10, final_score + 1)
            modifiers.append("vulnerable: child")
        
        if any(word in lower_desc for word in ['elderly', 'senior', 'old']):
            final_score = min(10, final_score + 1)
            modifiers.append("vulnerable: elderly")
        
        if any(word in lower_desc for word in ['pregnant', 'pregnancy']):
            final_score = min(10, final_score + 1)
            modifiers.append("vulnerable: pregnant")
        
        # Environmental threat modifiers
        if any(word in lower_desc for word in ['fire', 'smoke', 'burning', 'flames']):
            final_score = min(10, final_score + 2)
            modifiers.append("threat: fire")
        
        if any(word in lower_desc for word in ['collapse', 'collapsing', 'rubble', 'debris']):
            final_score = min(10, final_score + 2)
            modifiers.append("threat: structural collapse")
        
        if any(word in lower_desc for word in ['flood', 'flooding', 'water rising', 'drowning']):
            final_score = min(10, final_score + 1)
            modifiers.append("threat: flooding")
        
        if any(word in lower_desc for word in ['gas leak', 'chemical', 'toxic']):
            final_score = min(10, final_score + 2)
            modifiers.append("threat: hazardous materials")
        
        # Medical complication modifiers
        if any(word in lower_desc for word in ['diabetes', 'diabetic', 'insulin']):
            final_score = min(10, final_score + 1)
            modifiers.append("medical: diabetes")
        
        if any(word in lower_desc for word in ['heart condition', 'cardiac', 'pacemaker']):
            final_score = min(10, final_score + 1)
            modifiers.append("medical: cardiac condition")
        
        if any(word in lower_desc for word in ['medication', 'medicine', 'prescription']):
            final_score = min(10, final_score + 1)
            modifiers.append("medical: medication dependent")
        
        # Build reasoning string
        if modifiers:
            reasoning = f"Base severity: {base_score}/10. Adjusted for: {', '.join(modifiers)}. Final score: {final_score}/10."
        else:
            reasoning = f"Severity assessed at {final_score}/10 based on injury description."
        
        # Determine priority level name
        if final_score >= 9:
            priority_level = "CRITICAL"
        elif final_score >= 7:
            priority_level = "URGENT"
        elif final_score >= 5:
            priority_level = "SERIOUS"
        elif final_score >= 3:
            priority_level = "MINOR"
        else:
            priority_level = "NON-URGENT"
        
        result = {
            "status": "success",
            "victim_id": victim_id,
            "score": final_score,
            "priority_level": priority_level,
            "reasoning": reasoning,
            "keywords": identified_keywords[:5],  # Limit to top 5 keywords
            "modifiers": modifiers
        }
        
        log.info(f"{log_identifier} Analysis complete: {priority_level} ({final_score}/10) for victim {victim_id}")
        return result
        
    except Exception as e:
        log.error(f"{log_identifier} Error analyzing severity: {e}")
        return {
            "status": "error",
            "victim_id": victim_id,
            "message": f"Analysis failed: {str(e)}"
        }