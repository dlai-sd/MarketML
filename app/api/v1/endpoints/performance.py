"""
Performance monitoring endpoints.
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any

from app.utils.performance import performance_monitor

router = APIRouter()


@router.get("/performance/stats")
async def get_performance_stats() -> Dict[str, Any]:
    """Get performance statistics for all monitored operations."""
    return {
        "metrics": performance_monitor.get_stats(),
        "summary": _generate_summary(performance_monitor.get_stats())
    }


@router.get("/performance/stats/{operation}")
async def get_operation_stats(operation: str) -> Dict[str, Any]:
    """Get performance statistics for a specific operation."""
    stats = performance_monitor.get_stats(operation)
    if not stats:
        return {"error": f"No stats found for operation: {operation}"}
    return stats


@router.post("/performance/reset")
async def reset_performance_stats() -> Dict[str, str]:
    """Reset all performance statistics."""
    performance_monitor.reset()
    return {"message": "Performance statistics reset successfully"}


def _generate_summary(metrics: Dict) -> Dict[str, Any]:
    """Generate summary of performance metrics."""
    if not metrics:
        return {}
    
    total_operations = sum(m["count"] for m in metrics.values())
    slowest = max(metrics.items(), key=lambda x: x[1]["max_ms"], default=(None, {}))
    fastest = min(metrics.items(), key=lambda x: x[1]["avg_ms"], default=(None, {}))
    
    return {
        "total_operations": total_operations,
        "monitored_operations": len(metrics),
        "slowest_operation": {
            "name": slowest[0],
            "max_ms": slowest[1].get("max_ms", 0)
        } if slowest[0] else None,
        "fastest_operation": {
            "name": fastest[0],
            "avg_ms": fastest[1].get("avg_ms", 0)
        } if fastest[0] else None
    }
