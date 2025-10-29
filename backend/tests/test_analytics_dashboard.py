"""
Tests for Analytics Dashboard API
Tests comprehensive analytics endpoints, KPIs, trends, and predictions.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models.models import User, Service, QueueEntry, ServiceCounter, Appointment, Analytics
from app.services.auth_service import create_access_token
import json


# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_analytics_dashboard.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def test_db():
    """Create test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_db):
    """Create database session for each test"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """Create test client with database override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db_session):
    """Create admin user for testing"""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    user = User(
        name="Admin Test",
        email="admin@test.com",
        password_hash=pwd_context.hash("testpass123"),
        role="admin",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(admin_user):
    """Create authentication headers"""
    token = create_access_token(data={"sub": admin_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_data(db_session):
    """Create sample data for analytics testing"""
    # Create services
    services = [
        Service(id=1, name="General Medicine", queue_length=5),
        Service(id=2, name="Emergency", queue_length=10),
        Service(id=3, name="Pediatrics", queue_length=3)
    ]
    for service in services:
        db_session.add(service)
    
    # Create service counters
    counters = [
        ServiceCounter(id=1, name="Counter 1", service_id=1, is_active=1, staff_member="Dr. Smith"),
        ServiceCounter(id=2, name="Counter 2", service_id=1, is_active=1, staff_member="Dr. Jones"),
        ServiceCounter(id=3, name="Counter 3", service_id=2, is_active=1, staff_member="Dr. Brown")
    ]
    for counter in counters:
        db_session.add(counter)
    
    # Create queue entries (last 7 days)
    base_time = datetime.utcnow() - timedelta(days=7)
    queue_entries = []
    
    for day in range(7):
        for hour in range(8, 17):  # 8 AM to 5 PM
            for i in range(3):  # 3 patients per hour
                entry = QueueEntry(
                    queue_number=f"Q{day:02d}{hour:02d}{i:02d}",
                    service_id=(i % 3) + 1,
                    created_at=base_time + timedelta(days=day, hours=hour, minutes=i*20),
                    status="completed" if i % 2 == 0 else "waiting",
                    ai_predicted_wait=15 + (i * 5)
                )
                queue_entries.append(entry)
                db_session.add(entry)
    
    # Create appointments
    # Note: Appointment model doesn't have fee field, so revenue analytics will need adjustment
    appointments = []
    for day in range(7):
        for i in range(5):
            appt = Appointment(
                patient_id=1,  # Use admin user as patient
                service_id=(i % 3) + 1,
                appointment_date=base_time + timedelta(days=day, hours=9+i),
                duration=30 + (i * 10),
                status="completed" if i % 2 == 0 else "scheduled",
                notes=f"Test appointment {day}{i}"
            )
            appointments.append(appt)
            db_session.add(appt)
    
    db_session.commit()
    
    return {
        "services": services,
        "counters": counters,
        "queue_entries": queue_entries,
        "appointments": appointments
    }


# ==================== TESTS ====================

class TestDashboardOverview:
    """Test dashboard overview endpoint"""
    
    def test_get_overview_success(self, client, auth_headers, sample_data):
        """Test successful overview retrieval"""
        response = client.get(
            "/api/analytics/dashboard/overview?period_days=7",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check all required fields
        assert data["total_patients"] > 0
        assert "avg_wait_time" in data
        assert "active_services" in data
        assert "efficiency_score" in data
        assert "patient_satisfaction" in data
        assert "total_appointments" in data  # Changed from revenue
        assert "period_days" in data
        
        # Check data types and values
        assert isinstance(data["total_patients"], int)
        assert data["total_patients"] > 0
        assert isinstance(data["avg_wait_time"], (int, float))
        assert data["active_services"] == 3  # From sample_data
        assert 0 <= data["efficiency_score"] <= 1
        assert data["period_days"] == 7
    
    def test_get_overview_different_periods(self, client, auth_headers, sample_data):
        """Test overview with different time periods"""
        for days in [1, 7, 30]:
            response = client.get(
                f"/api/analytics/dashboard/overview?period_days={days}",
                headers=auth_headers
            )
            assert response.status_code == 200
            assert response.json()["period_days"] == days
    
    def test_get_overview_unauthorized(self, client, sample_data):
        """Test overview without authentication"""
        response = client.get("/api/analytics/dashboard/overview")
        assert response.status_code == 401


class TestServiceAnalytics:
    """Test service analytics endpoint"""
    
    def test_get_all_services(self, client, auth_headers, sample_data):
        """Test retrieving analytics for all services"""
        response = client.get(
            "/api/analytics/dashboard/services?period_days=7",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 3  # From sample_data
        
        # Check first service structure
        service = data[0]
        assert "service_id" in service
        assert "service_name" in service
        assert "total_patients" in service
        assert "avg_wait_time" in service
        assert "throughput" in service
        assert "utilization" in service
        assert "active_counters" in service
        assert "current_queue_length" in service
    
    def test_get_specific_service(self, client, auth_headers, sample_data):
        """Test retrieving analytics for specific service"""
        response = client.get(
            "/api/analytics/dashboard/services?service_id=1&period_days=7",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["service_id"] == 1


class TestStaffPerformance:
    """Test staff performance endpoint"""
    
    def test_get_staff_performance_as_admin(self, client, auth_headers, sample_data):
        """Test staff performance retrieval as admin"""
        response = client.get(
            "/api/analytics/dashboard/staff-performance?period_days=7",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        # Check structure if staff exists
        if len(data) > 0:
            staff = data[0]
            assert "user_id" in staff
            assert "name" in staff
            assert "role" in staff
            assert "patients_served" in staff
            assert "avg_service_time" in staff
            assert "active_hours" in staff
            assert "efficiency_rating" in staff
    
    def test_staff_performance_non_admin(self, client, db_session, sample_data):
        """Test staff performance access for non-admin users"""
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Create regular user
        user = User(
            name="Regular User",
            email="user@test.com",
            password_hash=pwd_context.hash("testpass123"),
            role="patient",
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        
        token = create_access_token(data={"sub": user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(
            "/api/analytics/dashboard/staff-performance",
            headers=headers
        )
        
        assert response.status_code == 403


class TestTrends:
    """Test trend analysis endpoints"""
    
    def test_wait_time_trends(self, client, auth_headers, sample_data):
        """Test wait time trends"""
        response = client.get(
            "/api/analytics/dashboard/trends/wait-times?period_days=7",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        if len(data) > 0:
            trend = data[0]
            assert "date" in trend
            assert "avg_wait_time" in trend
            assert "min_wait_time" in trend
            assert "max_wait_time" in trend
            assert "patient_count" in trend
    
    def test_hourly_traffic(self, client, auth_headers, sample_data):
        """Test hourly traffic patterns"""
        response = client.get(
            "/api/analytics/dashboard/trends/hourly-traffic?period_days=7",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        if len(data) > 0:
            traffic = data[0]
            assert "hour" in traffic
            assert "avg_patients" in traffic
            assert "avg_wait_time" in traffic
            assert 0 <= traffic["hour"] <= 23
    
    def test_service_trends(self, client, auth_headers, sample_data):
        """Test service usage trends"""
        response = client.get(
            "/api/analytics/dashboard/trends/services?period_days=7",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 3  # From sample_data
        
        if len(data) > 0:
            service = data[0]
            assert "service_id" in service
            assert "service_name" in service
            assert "daily_trends" in service
            assert isinstance(service["daily_trends"], list)


class TestPredictions:
    """Test predictive analytics endpoints"""
    
    def test_peak_time_predictions(self, client, auth_headers, sample_data):
        """Test peak time predictions"""
        response = client.get(
            "/api/analytics/dashboard/predictions/peak-times?look_ahead_days=7",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        if len(data) > 0:
            prediction = data[0]
            assert "day_of_week" in prediction
            assert "hour" in prediction
            assert "expected_patients" in prediction
            assert "confidence_level" in prediction
            assert 0 <= prediction["day_of_week"] <= 6
            assert 0 <= prediction["hour"] <= 23
            assert 0 <= prediction["confidence_level"] <= 1


class TestBottlenecks:
    """Test bottleneck identification"""
    
    def test_identify_bottlenecks(self, client, auth_headers, sample_data):
        """Test bottleneck identification"""
        response = client.get(
            "/api/analytics/dashboard/bottlenecks",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        if len(data) > 0:
            bottleneck = data[0]
            assert "bottleneck_type" in bottleneck
            assert "description" in bottleneck
            assert "severity" in bottleneck
            assert "affected_entity" in bottleneck
            assert "recommended_action" in bottleneck
            assert bottleneck["severity"] in ["critical", "high", "medium", "low"]


class TestComparison:
    """Test period comparison"""
    
    def test_compare_periods(self, client, auth_headers, sample_data):
        """Test period-over-period comparison"""
        response = client.get(
            "/api/analytics/dashboard/comparison?current_days=7&previous_days=7",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "current_period" in data
        assert "previous_period" in data
        assert "changes" in data
        assert "comparison_note" in data
        
        # Check changes structure
        changes = data["changes"]
        assert "total_patients" in changes
        assert "avg_wait_time" in changes
        assert "total_appointments" in changes  # Changed from revenue
        assert "patient_satisfaction" in changes


class TestRevenue:
    """Test revenue analytics"""
    
    def test_revenue_analytics_as_admin(self, client, auth_headers, sample_data):
        """Test appointment analytics as admin (revenue not available)"""
        response = client.get(
            "/api/analytics/dashboard/revenue?period_days=7",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Updated to match appointment-based analytics
        assert "total_appointments" in data
        assert "appointments_by_service" in data
        assert "appointment_trend" in data
        assert "status_breakdown" in data
        assert "scheduled_appointments" in data
        assert "period_days" in data
        
        assert isinstance(data["appointments_by_service"], list)
        assert isinstance(data["appointment_trend"], list)
        assert isinstance(data["status_breakdown"], list)


class TestRealTime:
    """Test real-time metrics"""
    
    def test_realtime_metrics(self, client, auth_headers, sample_data):
        """Test real-time dashboard metrics"""
        response = client.get(
            "/api/analytics/dashboard/real-time",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "current_patients_waiting" in data
        assert "active_counters" in data
        assert "avg_current_wait" in data
        assert "services_status" in data
        assert "recent_activities" in data
        assert "timestamp" in data
        
        assert isinstance(data["services_status"], list)
        assert isinstance(data["recent_activities"], list)
        assert len(data["services_status"]) == 3  # From sample_data


class TestExport:
    """Test analytics export"""
    
    def test_export_json(self, client, auth_headers, sample_data):
        """Test JSON export"""
        response = client.get(
            "/api/analytics/dashboard/export?period_days=7&format=json",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "overview" in data
        assert "services" in data
        assert "staff_performance" in data
        assert "wait_time_trends" in data
        assert "export_metadata" in data
    
    def test_export_csv(self, client, auth_headers, sample_data):
        """Test CSV export"""
        response = client.get(
            "/api/analytics/dashboard/export?period_days=7&format=csv",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment" in response.headers.get("content-disposition", "")


# ==================== INTEGRATION TESTS ====================

class TestAnalyticsIntegration:
    """Integration tests for analytics dashboard"""
    
    def test_full_dashboard_workflow(self, client, auth_headers, sample_data):
        """Test complete dashboard workflow"""
        # 1. Get overview
        overview_response = client.get(
            "/api/analytics/dashboard/overview?period_days=7",
            headers=auth_headers
        )
        assert overview_response.status_code == 200
        
        # 2. Get service analytics
        services_response = client.get(
            "/api/analytics/dashboard/services?period_days=7",
            headers=auth_headers
        )
        assert services_response.status_code == 200
        
        # 3. Get trends
        trends_response = client.get(
            "/api/analytics/dashboard/trends/wait-times?period_days=7",
            headers=auth_headers
        )
        assert trends_response.status_code == 200
        
        # 4. Get predictions
        predictions_response = client.get(
            "/api/analytics/dashboard/predictions/peak-times",
            headers=auth_headers
        )
        assert predictions_response.status_code == 200
        
        # 5. Get real-time data
        realtime_response = client.get(
            "/api/analytics/dashboard/real-time",
            headers=auth_headers
        )
        assert realtime_response.status_code == 200
        
        # All requests successful
        assert all([
            overview_response.status_code == 200,
            services_response.status_code == 200,
            trends_response.status_code == 200,
            predictions_response.status_code == 200,
            realtime_response.status_code == 200
        ])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
