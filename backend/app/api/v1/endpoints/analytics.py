from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.institutional_analytics import InstitutionalAnalyticsService

router = APIRouter()


@router.get("/overview", summary="Get institutional analytics overview")
def get_analytics_overview(db: Session = Depends(get_db)):
    """Retrieve top-level operational metrics across proposals, evaluations, decision packs, and historical corpus."""
    service = InstitutionalAnalyticsService(db)
    return service.get_overview()


@router.get("/proposals/trend", summary="Get proposal intake time-series trend")
def get_proposal_trend(
    days: int = Query(30, description="Timeframe in days"),
    db: Session = Depends(get_db),
):
    """Retrieve time-series proposal intake count over specified days."""
    service = InstitutionalAnalyticsService(db)
    return service.get_proposal_trend(days=days)


@router.get("/proposals/by-domain", summary="Get proposal count by domain")
def get_proposals_by_domain(db: Session = Depends(get_db)):
    """Retrieve proposal count grouped by technical domain."""
    service = InstitutionalAnalyticsService(db)
    return service.get_proposals_by_domain()


@router.get("/proposals/by-institution", summary="Get proposal count by institution")
def get_proposals_by_institution(db: Session = Depends(get_db)):
    """Retrieve proposal count grouped by proposing institution."""
    service = InstitutionalAnalyticsService(db)
    return service.get_proposals_by_institution()


@router.get("/reviewers/workload", summary="Get reviewer workload distribution")
def get_reviewer_workload(db: Session = Depends(get_db)):
    """Retrieve reviewer assignment and progress workload metrics."""
    service = InstitutionalAnalyticsService(db)
    return service.get_reviewer_workload()


@router.get("/scrutiny", summary="Get preliminary scrutiny findings analytics")
def get_scrutiny_analytics(db: Session = Depends(get_db)):
    """Retrieve common preliminary scrutiny finding metrics."""
    service = InstitutionalAnalyticsService(db)
    return service.get_scrutiny_analytics()


@router.get("/financial", summary="Get financial validation analytics")
def get_financial_analytics(db: Session = Depends(get_db)):
    """Retrieve financial check pass/flag counts and arithmetic mismatch stats."""
    service = InstitutionalAnalyticsService(db)
    return service.get_financial_analytics()


@router.get("/historical", summary="Get historical evidence utilization analytics")
def get_historical_utilization(db: Session = Depends(get_db)):
    """Retrieve historical project search usage and citation rate metrics."""
    service = InstitutionalAnalyticsService(db)
    return service.get_historical_utilization()


@router.get("/ai", summary="Get AI usage and provider reliability analytics")
def get_ai_usage_analytics(db: Session = Depends(get_db)):
    """Retrieve AI analysis count, cache hit rate, and provider fallback telemetry."""
    service = InstitutionalAnalyticsService(db)
    return service.get_ai_usage_analytics()


@router.get("/process-signals", summary="Get deterministic process improvement signals")
def get_process_improvement_signals(db: Session = Depends(get_db)):
    """Retrieve deterministic process improvement signals for operational refinement."""
    service = InstitutionalAnalyticsService(db)
    return service.get_process_improvement_signals()


@router.get("/export.csv", summary="Export operational analytics CSV")
def export_analytics_csv(db: Session = Depends(get_db)):
    """Export operational analytics metrics as CSV file."""
    service = InstitutionalAnalyticsService(db)
    csv_data = service.export_analytics_csv()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=naccer_institutional_analytics.csv"},
    )
