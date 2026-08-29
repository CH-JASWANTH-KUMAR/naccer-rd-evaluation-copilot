from fastapi.testclient import TestClient


def test_institutional_analytics_endpoints(client: TestClient):
    # 1. GET /api/v1/analytics/overview
    ov_res = client.get("/api/v1/analytics/overview")
    assert ov_res.status_code == 200
    ov_data = ov_res.json()
    assert "proposals" in ov_data
    assert "evaluations" in ov_data
    assert "historical_corpus" in ov_data

    # 2. GET /api/v1/analytics/proposals/trend
    tr_res = client.get("/api/v1/analytics/proposals/trend?days=30")
    assert tr_res.status_code == 200
    assert isinstance(tr_res.json(), list)

    # 3. GET /api/v1/analytics/proposals/by-domain
    dom_res = client.get("/api/v1/analytics/proposals/by-domain")
    assert dom_res.status_code == 200
    assert isinstance(dom_res.json(), list)

    # 4. GET /api/v1/analytics/proposals/by-institution
    inst_res = client.get("/api/v1/analytics/proposals/by-institution")
    assert inst_res.status_code == 200
    assert isinstance(inst_res.json(), list)

    # 5. GET /api/v1/analytics/reviewers/workload
    wl_res = client.get("/api/v1/analytics/reviewers/workload")
    assert wl_res.status_code == 200
    assert isinstance(wl_res.json(), list)

    # 6. GET /api/v1/analytics/scrutiny
    scr_res = client.get("/api/v1/analytics/scrutiny")
    assert scr_res.status_code == 200
    assert "common_findings" in scr_res.json()

    # 7. GET /api/v1/analytics/financial
    fin_res = client.get("/api/v1/analytics/financial")
    assert fin_res.status_code == 200
    assert fin_res.json()["flagged_label"] == "FINANCIAL VALIDATION FLAG"

    # 8. GET /api/v1/analytics/historical
    hist_res = client.get("/api/v1/analytics/historical")
    assert hist_res.status_code == 200
    assert "utilization_percentage" in hist_res.json()

    # 9. GET /api/v1/analytics/ai
    ai_res = client.get("/api/v1/analytics/ai")
    assert ai_res.status_code == 200
    assert "cache_hit_rate_percentage" in ai_res.json()

    # 10. GET /api/v1/analytics/process-signals
    sig_res = client.get("/api/v1/analytics/process-signals")
    assert sig_res.status_code == 200
    sig_data = sig_res.json()
    assert isinstance(sig_data, list)
    assert len(sig_data) >= 1
    assert "suggested_operational_action" in sig_data[0]

    # 11. GET /api/v1/analytics/export.csv
    csv_res = client.get("/api/v1/analytics/export.csv")
    assert csv_res.status_code == 200
    assert "text/csv" in csv_res.headers["content-type"]
    assert "Metric Category,Metric Name,Value" in csv_res.text


def test_analytics_safety_boundaries():
    # Verify NO predictive decision or ranking endpoints exist
    disallowed_routes = [
        "/api/v1/analytics/approval-probability",
        "/api/v1/analytics/proposal-rankings",
        "/api/v1/analytics/reviewer-rankings",
    ]
    from fastapi.routing import APIRoute

    from app.main import app

    route_paths = [r.path for r in app.routes if isinstance(r, APIRoute)]
    for route in disallowed_routes:
        assert route not in route_paths
