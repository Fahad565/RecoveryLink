import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.database import Base, get_db
from app.services.recovery import ReadinessEngine
from app.services.ai import AIService
from app.services.messaging import messaging_service

# Setup in-memory SQLite database with StaticPool for cross-thread test persistence
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_readiness_engine():
    score, advice = ReadinessEngine.calculate_score(True, True, True, True)
    assert score == 100
    assert "Excellent" in advice

    score_low, advice_low = ReadinessEngine.calculate_score(False, False, False, False)
    assert score_low == 0
    assert "Low" in advice_low

def test_ai_service_rule_fallback():
    plan = AIService.generate_recovery_plan(
        "phone_lost",
        {"recovery_contact": "+254700000000", "recovery_email": "test@example.com"},
        {"recovery_contact_ready": True, "recovery_email_ready": True}
    )
    assert plan["provider"] == "rule_engine"
    assert "test@example.com" in plan["plan"]

def test_messaging_service_mock():
    res = messaging_service.send_sms(["+254700000000"], "Test message")
    assert res["status"] == "success"

def test_ussd_flow_main_menu():
    payload = {
        "sessionId": "sess_123",
        "serviceCode": "*384*123#",
        "phoneNumber": "+254711223344",
        "text": ""
    }
    response = client.post("/api/v1/ussd", data=payload)
    assert response.status_code == 200
    assert response.headers.get("at-ussd-hop-metadata") == "MainMenu"
    assert response.text.startswith("CON Welcome to RecoveryLink")

def test_ussd_flow_safety_check_and_score():
    phone = "+254711223344"
    # Step 1: Open Safety Check Menu
    res1 = client.post("/api/v1/ussd", data={"sessionId": "s1", "serviceCode": "*384#", "phoneNumber": phone, "text": "1"})
    assert res1.text.startswith("CON Digital Safety Check")

    # Step 2: Answer Contact = Yes
    res2 = client.post("/api/v1/ussd", data={"sessionId": "s1", "serviceCode": "*384#", "phoneNumber": phone, "text": "1*1*1"})
    assert "Recovery Contact marked as YES" in res2.text

    # Step 3: View Score
    res3 = client.post("/api/v1/ussd", data={"sessionId": "s1", "serviceCode": "*384#", "phoneNumber": phone, "text": "1*5"})
    assert res3.text.startswith("END Digital Readiness:")
    assert "25/100" in res3.text

def test_ussd_flow_profile_update():
    phone = "+254711223355"
    # Set email
    res = client.post("/api/v1/ussd", data={"sessionId": "s2", "serviceCode": "*384#", "phoneNumber": phone, "text": "2*2*user@recovery.org"})
    assert res.text.startswith("END Recovery email updated to: user@recovery.org")

    # Retrieve user profile via REST API
    user_res = client.get(f"/api/v1/users/{phone}")
    assert user_res.status_code == 200
    user_id = user_res.json()["id"]

    profile_res = client.get(f"/api/v1/profiles/{user_id}")
    assert profile_res.status_code == 200
    assert profile_res.json()["recovery_email"] == "user@recovery.org"

def test_ussd_flow_emergency_recovery():
    phone = "+254711223366"
    # Trigger Emergency Lost Phone
    res = client.post("/api/v1/ussd", data={"sessionId": "s3", "serviceCode": "*384#", "phoneNumber": phone, "text": "3*1"})
    assert res.text.startswith("END Emergency recovery initiated!")
    assert res.headers.get("at-ussd-hop-metadata") == "EmergencyRecovery_Triggered"

    # Verify incident created via REST API
    user_res = client.get(f"/api/v1/users/{phone}")
    user_id = user_res.json()["id"]

    incidents_res = client.get(f"/api/v1/incidents/{user_id}")
    assert incidents_res.status_code == 200
    incidents = incidents_res.json()
    assert len(incidents) >= 1
    assert incidents[0]["incident_type"] == "phone_lost"
    assert incidents[0]["sms_sent"] is True

def test_ussd_notification():
    payload = {
        "sessionId": "s3",
        "serviceCode": "*384#",
        "phoneNumber": "+254711223366",
        "status": "Success",
        "durationInMillis": "1200",
        "hopsCount": 2
    }
    response = client.post("/api/v1/ussd/notification", data=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "received"
