from app.auth import AuthManager

def test_refresh_dashboard_maintains_session():
    auth = AuthManager()
    res = auth.refresh_dashboard()
    assert res["status"] == "logged_in", f"Expected logged_in status but got {res}"
