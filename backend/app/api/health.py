"""
Health Score API Routes
Calculates and returns financial health score
"""
from fastapi import APIRouter, HTTPException, Request
from typing import Optional, List
from pydantic import BaseModel
import logging

from app.agents.health_agent import HealthScoreAgent

logger = logging.getLogger(__name__)

router = APIRouter()


class HealthScoreRequest(BaseModel):
    monthly_income: float
    monthly_expenses: float
    total_savings: float = 0
    total_debt: float = 0
    emergency_fund: float = 0
    age: Optional[int] = None


class HealthScoreResponse(BaseModel):
    overall_score: float
    grade: str
    summary: str
    components: dict
    action_items: List[dict]
    peer_comparison: Optional[dict] = None


@router.post("/calculate", response_model=HealthScoreResponse)
async def calculate_health_score(
    data: HealthScoreRequest,
    request: Request
):
    """
    Calculate financial health score
    """
    try:
        llm_service = request.app.state.llm_service
        vector_service = request.app.state.vector_service
        agent = HealthScoreAgent(llm_service, vector_service)
        
        # Calculate score
        health_data = agent.calculate_health_score(
            monthly_income=data.monthly_income,
            monthly_expenses=data.monthly_expenses,
            total_savings=data.total_savings,
            total_debt=data.total_debt,
            emergency_fund=data.emergency_fund
        )
        
        # Generate action items
        action_items = await agent.generate_action_items(health_data)
        
        # Compare to peers
        peer_comparison = None
        if data.age:
            peer_comparison = agent.compare_to_peers(
                score=health_data["overall_score"],
                age=data.age
            )
        
        logger.info(f"Calculated health score: {health_data['overall_score']}")
        
        return HealthScoreResponse(
            overall_score=health_data["overall_score"],
            grade=health_data["grade"],
            summary=health_data["summary"],
            components=health_data["components"],
            action_items=action_items,
            peer_comparison=peer_comparison
        )
        
    except Exception as e:
        logger.error(f"Health score calculation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/benchmark")
async def get_benchmarks():
    """
    Get financial health benchmarks and targets
    """
    return {
        "emergency_fund": {
            "target": "3-6 months of expenses",
            "minimum": "3 months",
            "ideal": "6+ months"
        },
        "debt_to_income": {
            "excellent": "<15%",
            "good": "15-28%",
            "fair": "28-36%",
            "poor": ">36%"
        },
        "savings_rate": {
            "excellent": ">20%",
            "good": "10-20%",
            "fair": "5-10%",
            "poor": "<5%"
        },
        "budget_adherence": {
            "excellent": "<70% of income on expenses",
            "good": "70-80%",
            "fair": "80-90%",
            "poor": ">90%"
        }
    }
