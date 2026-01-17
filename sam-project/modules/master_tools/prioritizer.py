"""
Victim Priority Calculator for Master Agent

Scoring Rules (from TEAM-COORDINATION-README.md):
  Severity: CRITICAL=50, MODERATE=30, STABLE=10
  People: 4 points each (max 20)
  Injuries: +15 points
  Hazards: +5 each (fire_hazard, flooding, structural_collapse)
  
  Priority Level:
    score >= 70 → CRITICAL
    score >= 40 → HIGH
    score >= 20 → MEDIUM
    score < 20  → LOW
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


def calculate_priority(
    severity: str,
    num_people: int,
    has_injuries: bool,
    additional_factors: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Calculate victim priority score based on severity factors.
    
    Args:
        severity: "CRITICAL" | "MODERATE" | "STABLE"
        num_people: Positive integer
        has_injuries: Boolean
        additional_factors: Optional dict with keys like "fire_hazard", "flooding", "structural_collapse"
    
    Returns:
        {
            "priority_score": int (0-100),
            "priority_level": str ("CRITICAL" | "HIGH" | "MEDIUM" | "LOW"),
            "reasoning": list[str],
            "calculated_at": str (ISO 8601)
        }
    """
    score = 0
    reasoning: List[str] = []
    
    # Severity scoring (0-50 points)
    severity_scores = {
        "CRITICAL": 50,
        "MODERATE": 30,
        "STABLE": 10
    }
    severity_upper = severity.upper()
    severity_score = severity_scores.get(severity_upper, 20)
    score += severity_score
    reasoning.append(f"Severity ({severity_upper}): +{severity_score} points")
    
    # People count scoring (max 20 points, 4 points per person)
    people_score = min(num_people * 4, 20)
    score += people_score
    reasoning.append(f"People count ({num_people}): +{people_score} points")
    
    # Injury scoring (+15 points if injuries)
    if has_injuries:
        score += 15
        reasoning.append("Injuries reported: +15 points")
    
    # Additional factors (each +5 points)
    if additional_factors:
        if additional_factors.get("fire_hazard"):
            score += 5
            reasoning.append("Fire hazard: +5 points")
        if additional_factors.get("flooding"):
            score += 5
            reasoning.append("Flooding: +5 points")
        if additional_factors.get("structural_collapse"):
            score += 5
            reasoning.append("Structural collapse: +5 points")
    
    # Cap score at 100
    final_score = min(score, 100)
    
    # Determine priority level
    if final_score >= 70:
        priority_level = "CRITICAL"
    elif final_score >= 40:
        priority_level = "HIGH"
    elif final_score >= 20:
        priority_level = "MEDIUM"
    else:
        priority_level = "LOW"
    
    return {
        "priority_score": final_score,
        "priority_level": priority_level,
        "reasoning": reasoning,
        "calculated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }


# Test function
if __name__ == "__main__":
    print("=" * 60)
    print("TESTING PRIORITIZER")
    print("=" * 60)
    
    # Test 1: Critical case (50 + 12 + 15 + 5 + 5 = 87)
    print("\nTest 1: CRITICAL severity, 3 people, injuries, collapse + fire")
    result = calculate_priority(
        severity="CRITICAL",
        num_people=3,
        has_injuries=True,
        additional_factors={"structural_collapse": True, "fire_hazard": True}
    )
    print(f"  Score: {result['priority_score']} (expected: 87)")
    print(f"  Level: {result['priority_level']} (expected: CRITICAL)")
    assert result['priority_score'] == 87, "Test 1 FAILED!"
    assert result['priority_level'] == "CRITICAL", "Test 1 FAILED!"
    print("  ✅ PASSED")
    
    # Test 2: Moderate case (30 + 8 + 0 = 38)
    print("\nTest 2: MODERATE severity, 2 people, no injuries")
    result = calculate_priority(
        severity="MODERATE",
        num_people=2,
        has_injuries=False
    )
    print(f"  Score: {result['priority_score']} (expected: 38)")
    print(f"  Level: {result['priority_level']} (expected: MEDIUM)")
    assert result['priority_score'] == 38, "Test 2 FAILED!"
    assert result['priority_level'] == "MEDIUM", "Test 2 FAILED!"
    print("  ✅ PASSED")
    
    # Test 3: Low priority (10 + 4 + 0 = 14)
    print("\nTest 3: STABLE severity, 1 person, no injuries")
    result = calculate_priority(
        severity="STABLE",
        num_people=1,
        has_injuries=False
    )
    print(f"  Score: {result['priority_score']} (expected: 14)")
    print(f"  Level: {result['priority_level']} (expected: LOW)")
    assert result['priority_score'] == 14, "Test 3 FAILED!"
    assert result['priority_level'] == "LOW", "Test 3 FAILED!"
    print("  ✅ PASSED")
    
    # Test 4: HIGH priority (30 + 16 + 15 = 61)
    print("\nTest 4: MODERATE severity, 4 people, with injuries")
    result = calculate_priority(
        severity="MODERATE",
        num_people=4,
        has_injuries=True
    )
    print(f"  Score: {result['priority_score']} (expected: 61)")
    print(f"  Level: {result['priority_level']} (expected: HIGH)")
    assert result['priority_score'] == 61, "Test 4 FAILED!"
    assert result['priority_level'] == "HIGH", "Test 4 FAILED!"
    print("  ✅ PASSED")
    
    # Test 5: Max people cap (50 + 20 + 15 = 85)
    print("\nTest 5: CRITICAL severity, 10 people (max cap), with injuries")
    result = calculate_priority(
        severity="CRITICAL",
        num_people=10,
        has_injuries=True
    )
    print(f"  Score: {result['priority_score']} (expected: 85)")
    print(f"  Level: {result['priority_level']} (expected: CRITICAL)")
    assert result['priority_score'] == 85, "Test 5 FAILED!"
    assert result['priority_level'] == "CRITICAL", "Test 5 FAILED!"
    print("  ✅ PASSED")
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! ✅")
    print("=" * 60)