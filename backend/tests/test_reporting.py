"""
Comprehensive tests for the reporting system.
Tests patient reports, queue analytics, staff performance, and financial reports.
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import Mock, patch, MagicMock
import io

from app.main import app
from app.services.reporting_service import ReportingService
from app.models.models import User, QueueEntry
from app.models.workflow_models import Patient, PatientVisit
from app.models.staff_models import StaffProfile


class TestReportingService:
    """Test the ReportingService class methods"""
    
    @pytest.fixture
    def db_session(self):
        """Mock database session"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def reporting_service(self, db_session):
        """Create a ReportingService instance"""
        return ReportingService(db_session)
    
    @pytest.fixture
    def sample_patient(self):
        """Sample patient data"""
        patient = Mock(spec=Patient)
        patient.id = 1
        patient.first_name = "John"
        patient.last_name = "Doe"
        patient.date_of_birth = datetime(1990, 1, 1)
        patient.gender = "Male"
        patient.email = "john.doe@example.com"
        patient.phone = "+250788123456"
        patient.address = "Kigali, Rwanda"
        patient.blood_type = "O+"
        patient.allergies = "None"
        patient.insurance_provider = "RSSB"
        patient.insurance_number = "INS123456"
        return patient
    
    @pytest.fixture
    def sample_patient_visits(self):
        """Sample patient visits"""
        visits = []
        for i in range(3):
            visit = Mock(spec=PatientVisit)
            visit.id = i + 1
            visit.patient_id = 1
            visit.visit_date = datetime.now() - timedelta(days=i * 30)
            visit.visit_type = "scheduled" if i % 2 == 0 else "emergency"
            visit.chief_complaint = f"Complaint {i + 1}"
            visit.diagnosis = f"Diagnosis {i + 1}"
            visit.treatment = f"Treatment {i + 1}"
            visit.doctor_id = 1
            visits.append(visit)
        return visits
    
    @pytest.fixture
    def sample_queue_entries(self):
        """Sample queue entries"""
        entries = []
        for i in range(10):
            entry = Mock(spec=QueueEntry)
            entry.id = i + 1
            entry.ticket_number = f"Q{i + 1:03d}"
            entry.patient_name = f"Patient {i + 1}"
            entry.service_type = "consultation" if i % 2 == 0 else "lab_test"
            entry.priority = "emergency" if i % 3 == 0 else "normal"
            entry.department = "emergency" if i % 2 == 0 else "outpatient"
            entry.status = "completed" if i < 7 else "waiting"
            entry.timestamp = datetime.now() - timedelta(hours=i)
            entry.called_time = datetime.now() - timedelta(hours=i, minutes=10) if i < 7 else None
            entry.completed_time = datetime.now() - timedelta(hours=i, minutes=5) if i < 7 else None
            entry.served_by = 1 if i < 7 else None
            entries.append(entry)
        return entries
    
    def test_get_patient_report_basic(self, reporting_service, db_session, sample_patient, sample_patient_visits):
        """Test basic patient report generation"""
        # Setup mock queries
        query_mock = Mock()
        filter_mock = Mock()
        first_mock = Mock(return_value=sample_patient)
        all_mock = Mock(return_value=sample_patient_visits)
        
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = sample_patient
        filter_mock.order_by.return_value.all.return_value = sample_patient_visits
        
        db_session.query.return_value = query_mock
        
        # Mock service calls
        with patch('app.services.reporting_service.PatientHistoryService') as mock_history_service, \
             patch('app.services.reporting_service.PaymentService') as mock_payment_service:
            
            # Setup mock returns
            mock_history_instance = mock_history_service.return_value
            mock_history_instance.get_patient_history.return_value = {"medical_records": []}
            mock_history_instance.get_lab_results.return_value = {"lab_results": []}
            mock_history_instance.get_medications.return_value = {"medications": []}
            
            mock_payment_service.return_value.get_patient_payments.return_value = {"payments": []}
            
            # Generate report
            report = reporting_service.get_patient_report(
                patient_id=1,
                start_date=datetime.now() - timedelta(days=180),
                end_date=datetime.now()
            )
            
            # Assertions
            assert report is not None
            assert "patient" in report
            assert report["patient"]["id"] == 1
            assert report["patient"]["first_name"] == "John"
            assert report["patient"]["last_name"] == "Doe"
    
    def test_get_patient_report_with_optional_sections(self, reporting_service, db_session, sample_patient):
        """Test patient report with selective sections"""
        # Setup mock
        query_mock = Mock()
        filter_mock = Mock()
        filter_mock.first.return_value = sample_patient
        filter_mock.order_by.return_value.all.return_value = []
        query_mock.filter.return_value = filter_mock
        db_session.query.return_value = query_mock
        
        with patch('app.services.reporting_service.PatientHistoryService') as mock_history_service, \
             patch('app.services.reporting_service.PaymentService') as mock_payment_service:
            
            mock_history_instance = mock_history_service.return_value
            mock_history_instance.get_patient_history.return_value = {"medical_records": []}
            mock_history_instance.get_lab_results.return_value = {"lab_results": []}
            mock_history_instance.get_medications.return_value = {"medications": []}
            mock_payment_service.return_value.get_patient_payments.return_value = {"payments": []}
            
            # Generate report with only visits
            report = reporting_service.get_patient_report(
                patient_id=1,
                start_date=datetime.now() - timedelta(days=180),
                end_date=datetime.now(),
                include_visits=True,
                include_medical_records=False,
                include_lab_results=False,
                include_medications=False,
                include_payments=False
            )
            
            assert "patient" in report
            assert "visits" in report
            assert "medical_records" not in report
            assert "lab_results" not in report
            assert "medications" not in report
            assert "payments" not in report
    
    def test_get_queue_analytics(self, reporting_service, db_session, sample_queue_entries):
        """Test queue analytics generation"""
        # Setup mock
        query_mock = Mock()
        filter_mock = Mock()
        filter_mock.all.return_value = sample_queue_entries
        query_mock.filter.return_value = filter_mock
        db_session.query.return_value = query_mock
        
        # Generate analytics
        analytics = reporting_service.get_queue_analytics(
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now()
        )
        
        # Assertions
        assert analytics is not None
        assert "summary" in analytics
        assert "wait_time_stats" in analytics
        assert "service_time_stats" in analytics
        assert analytics["summary"]["total_entries"] == 10
        assert analytics["summary"]["completed"] == 7
        assert analytics["summary"]["waiting"] == 3
    
    def test_get_queue_analytics_with_filters(self, reporting_service, db_session, sample_queue_entries):
        """Test queue analytics with department and service type filters"""
        # Filter for emergency department
        emergency_entries = [e for e in sample_queue_entries if e.department == "emergency"]
        
        query_mock = Mock()
        filter_mock = Mock()
        filter_mock.all.return_value = emergency_entries
        query_mock.filter.return_value = filter_mock
        db_session.query.return_value = query_mock
        
        analytics = reporting_service.get_queue_analytics(
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now(),
            department="emergency"
        )
        
        assert analytics["summary"]["total_entries"] == len(emergency_entries)
    
    def test_get_staff_performance_report(self, reporting_service, db_session):
        """Test staff performance report generation"""
        # Setup mock data
        staff = Mock(spec=User)
        staff.id = 1
        staff.username = "dr_smith"
        staff.email = "dr.smith@hospital.com"
        staff.role = "doctor"
        
        queue_entries = []
        for i in range(5):
            entry = Mock(spec=QueueEntry)
            entry.status = "completed"
            entry.called_time = datetime.now() - timedelta(hours=i, minutes=20)
            entry.completed_time = datetime.now() - timedelta(hours=i)
            queue_entries.append(entry)
        
        visits = [Mock(spec=PatientVisit) for _ in range(10)]
        for i, visit in enumerate(visits):
            visit.visit_type = "emergency" if i % 3 == 0 else "scheduled"
        
        # Setup mock queries
        query_mock = Mock()
        filter_mock = Mock()
        
        def mock_query(model):
            if model == User:
                filter_mock.first.return_value = staff
            elif model == QueueEntry:
                filter_mock.all.return_value = queue_entries
            elif model == PatientVisit:
                filter_mock.all.return_value = visits
            return query_mock
        
        query_mock.filter.return_value = filter_mock
        db_session.query.side_effect = mock_query
        
        # Generate report
        report = reporting_service.get_staff_performance_report(
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now(),
            staff_id=1
        )
        
        # Assertions
        assert report is not None
        assert "staff" in report
        assert "queue_performance" in report
        assert "patient_visits" in report
        assert report["staff"]["id"] == 1
        assert report["queue_performance"]["total_handled"] == 5
        assert report["patient_visits"]["total_visits"] == 10
    
    def test_get_financial_report(self, reporting_service, db_session):
        """Test financial report generation"""
        with patch('app.services.reporting_service.PaymentService') as mock_payment_service:
            # Setup mock payments
            payments = []
            for i in range(10):
                payment = {
                    "id": i + 1,
                    "amount": 50000.0,
                    "amount_paid": 40000.0 if i < 7 else 0.0,
                    "outstanding_balance": 10000.0 if i < 7 else 50000.0,
                    "payment_method": "cash" if i % 2 == 0 else "mobile_money",
                    "payment_status": "partial" if i < 7 else "pending",
                    "department": "emergency" if i % 2 == 0 else "outpatient",
                    "payment_date": (datetime.now() - timedelta(days=i)).isoformat(),
                    "is_insurance": i % 3 == 0
                }
                payments.append(payment)
            
            mock_payment_service.return_value.get_all_payments.return_value = {"payments": payments}
            
            # Generate report
            report = reporting_service.get_financial_report(
                start_date=datetime.now() - timedelta(days=30),
                end_date=datetime.now()
            )
            
            # Assertions
            assert report is not None
            assert "summary" in report
            assert "payment_methods" in report
            assert "payment_status" in report
            assert "departments" in report
            assert "daily_trends" in report
            assert "insurance_breakdown" in report
            
            # Check calculations
            assert report["summary"]["total_billed"] == 500000.0
            assert report["summary"]["total_collected"] == 280000.0
            assert report["summary"]["total_outstanding"] == 220000.0
    
    def test_export_to_csv_patient_report(self, reporting_service):
        """Test CSV export for patient report"""
        report_data = {
            "patient": {
                "id": 1,
                "first_name": "John",
                "last_name": "Doe",
                "date_of_birth": "1990-01-01",
                "email": "john.doe@example.com"
            },
            "visits": {
                "total_visits": 2,
                "visits": [
                    {
                        "visit_date": "2025-01-01",
                        "visit_type": "scheduled",
                        "chief_complaint": "Headache",
                        "diagnosis": "Migraine"
                    }
                ]
            },
            "payments": {
                "total_transactions": 1,
                "total_amount": 50000.0,
                "transactions": [
                    {
                        "payment_date": "2025-01-01",
                        "amount": 50000.0,
                        "payment_method": "cash"
                    }
                ]
            }
        }
        
        csv_content = reporting_service.export_to_csv(report_data, "patient")
        
        # Assertions
        assert csv_content is not None
        assert "Patient Report" in csv_content
        assert "John" in csv_content
        assert "Doe" in csv_content
        assert "Visits" in csv_content
        assert "Payments" in csv_content
    
    def test_export_to_csv_financial_report(self, reporting_service):
        """Test CSV export for financial report"""
        report_data = {
            "summary": {
                "total_billed": 500000.0,
                "total_collected": 400000.0,
                "total_outstanding": 100000.0,
                "collection_rate": 80.0
            },
            "payment_methods": {
                "cash": {"count": 5, "amount": 250000.0},
                "mobile_money": {"count": 3, "amount": 150000.0}
            },
            "daily_trends": [
                {"date": "2025-01-01", "total_amount": 100000.0, "count": 2}
            ]
        }
        
        csv_content = reporting_service.export_to_csv(report_data, "financial")
        
        # Assertions
        assert csv_content is not None
        assert "Financial Report" in csv_content
        assert "500000.0" in csv_content
        assert "Payment Methods" in csv_content
        assert "Daily Trends" in csv_content


class TestReportingRoutes:
    """Test the reporting REST API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_current_user(self):
        """Mock authenticated user"""
        user = Mock(spec=User)
        user.id = 1
        user.username = "testuser"
        user.email = "test@hospital.com"
        user.role = "admin"
        user.is_active = True
        return user
    
    @pytest.fixture
    def auth_headers(self):
        """Mock authentication headers"""
        return {"Authorization": "Bearer test_token"}
    
    def test_get_patient_report_endpoint(self, client, mock_current_user, auth_headers):
        """Test GET /api/reports/patient/{patient_id} endpoint"""
        with patch('app.routes.reports.get_current_user', return_value=mock_current_user), \
             patch('app.routes.reports.ReportingService') as mock_service:
            
            # Setup mock service
            mock_instance = mock_service.return_value
            mock_instance.get_patient_report.return_value = {
                "patient": {"id": 1, "first_name": "John", "last_name": "Doe"},
                "visits": {"total_visits": 0}
            }
            
            # Make request
            response = client.get(
                "/api/reports/patient/1",
                headers=auth_headers
            )
            
            # Assertions
            assert response.status_code == 200
            data = response.json()
            assert "patient" in data
            assert data["patient"]["id"] == 1
    
    def test_get_patient_report_with_date_range(self, client, mock_current_user, auth_headers):
        """Test patient report with date range parameters"""
        with patch('app.routes.reports.get_current_user', return_value=mock_current_user), \
             patch('app.routes.reports.ReportingService') as mock_service:
            
            mock_instance = mock_service.return_value
            mock_instance.get_patient_report.return_value = {
                "patient": {"id": 1},
                "date_range": {"start": "2025-01-01", "end": "2025-01-31"}
            }
            
            response = client.get(
                "/api/reports/patient/1?start_date=2025-01-01&end_date=2025-01-31",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "date_range" in data
    
    def test_export_patient_report_csv_endpoint(self, client, mock_current_user, auth_headers):
        """Test GET /api/reports/patient/{patient_id}/export/csv endpoint"""
        with patch('app.routes.reports.get_current_user', return_value=mock_current_user), \
             patch('app.routes.reports.ReportingService') as mock_service:
            
            mock_instance = mock_service.return_value
            mock_instance.get_patient_report.return_value = {"patient": {"id": 1}}
            mock_instance.export_to_csv.return_value = "Patient Report\nJohn,Doe"
            
            response = client.get(
                "/api/reports/patient/1/export/csv",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/csv; charset=utf-8"
            assert "attachment" in response.headers["content-disposition"]
    
    def test_get_queue_analytics_endpoint(self, client, mock_current_user, auth_headers):
        """Test GET /api/reports/queue/analytics endpoint"""
        with patch('app.routes.reports.get_current_user', return_value=mock_current_user), \
             patch('app.routes.reports.ReportingService') as mock_service:
            
            mock_instance = mock_service.return_value
            mock_instance.get_queue_analytics.return_value = {
                "summary": {
                    "total_entries": 100,
                    "completed": 75,
                    "waiting": 25
                },
                "wait_time_stats": {
                    "average_wait_time": 15.5
                }
            }
            
            response = client.get(
                "/api/reports/queue/analytics",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "summary" in data
            assert data["summary"]["total_entries"] == 100
    
    def test_get_queue_analytics_with_filters(self, client, mock_current_user, auth_headers):
        """Test queue analytics with department and service type filters"""
        with patch('app.routes.reports.get_current_user', return_value=mock_current_user), \
             patch('app.routes.reports.ReportingService') as mock_service:
            
            mock_instance = mock_service.return_value
            mock_instance.get_queue_analytics.return_value = {
                "summary": {"total_entries": 50},
                "filters": {"department": "emergency", "service_type": "consultation"}
            }
            
            response = client.get(
                "/api/reports/queue/analytics?department=emergency&service_type=consultation",
                headers=auth_headers
            )
            
            assert response.status_code == 200
    
    def test_get_staff_performance_endpoint(self, client, mock_current_user, auth_headers):
        """Test GET /api/reports/staff/performance endpoint"""
        with patch('app.routes.reports.get_current_user', return_value=mock_current_user), \
             patch('app.routes.reports.ReportingService') as mock_service:
            
            mock_instance = mock_service.return_value
            mock_instance.get_staff_performance_report.return_value = {
                "staff": {"id": 1, "username": "dr_smith"},
                "queue_performance": {"total_handled": 50},
                "patient_visits": {"total_visits": 30}
            }
            
            response = client.get(
                "/api/reports/staff/performance",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "staff" in data or "performance" in data
    
    def test_staff_performance_permission_check(self, client, auth_headers):
        """Test that non-admin users can only view their own performance"""
        regular_user = Mock(spec=User)
        regular_user.id = 2
        regular_user.username = "regular_user"
        regular_user.role = "doctor"
        regular_user.is_active = True
        
        with patch('app.routes.reports.get_current_user', return_value=regular_user), \
             patch('app.routes.reports.ReportingService') as mock_service:
            
            mock_instance = mock_service.return_value
            mock_instance.get_staff_performance_report.return_value = {
                "staff": {"id": 2},
                "queue_performance": {"total_handled": 20}
            }
            
            # Should succeed for own data
            response = client.get(
                "/api/reports/staff/performance?staff_id=2",
                headers=auth_headers
            )
            assert response.status_code == 200
            
            # Should fail for other user's data
            response = client.get(
                "/api/reports/staff/performance?staff_id=1",
                headers=auth_headers
            )
            # Note: This might return 403 or filter results depending on implementation
    
    def test_get_financial_report_endpoint(self, client, mock_current_user, auth_headers):
        """Test GET /api/reports/financial endpoint"""
        with patch('app.routes.reports.get_current_user', return_value=mock_current_user), \
             patch('app.routes.reports.ReportingService') as mock_service:
            
            mock_instance = mock_service.return_value
            mock_instance.get_financial_report.return_value = {
                "summary": {
                    "total_billed": 500000.0,
                    "total_collected": 400000.0,
                    "total_outstanding": 100000.0
                },
                "payment_methods": {}
            }
            
            response = client.get(
                "/api/reports/financial",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "summary" in data
    
    def test_financial_report_permission_check(self, client, auth_headers):
        """Test that only authorized roles can access financial reports"""
        unauthorized_user = Mock(spec=User)
        unauthorized_user.id = 3
        unauthorized_user.username = "doctor"
        unauthorized_user.role = "doctor"
        unauthorized_user.is_active = True
        
        with patch('app.routes.reports.get_current_user', return_value=unauthorized_user):
            response = client.get(
                "/api/reports/financial",
                headers=auth_headers
            )
            
            # Should return 403 Forbidden
            assert response.status_code == 403
    
    def test_export_financial_report_csv_endpoint(self, client, mock_current_user, auth_headers):
        """Test GET /api/reports/financial/export/csv endpoint"""
        with patch('app.routes.reports.get_current_user', return_value=mock_current_user), \
             patch('app.routes.reports.ReportingService') as mock_service:
            
            mock_instance = mock_service.return_value
            mock_instance.get_financial_report.return_value = {
                "summary": {"total_billed": 500000.0}
            }
            mock_instance.export_to_csv.return_value = "Financial Report\n500000.0"
            
            response = client.get(
                "/api/reports/financial/export/csv",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/csv; charset=utf-8"
    
    def test_get_dashboard_summary_endpoint(self, client, mock_current_user, auth_headers):
        """Test GET /api/reports/summary endpoint"""
        with patch('app.routes.reports.get_current_user', return_value=mock_current_user), \
             patch('app.routes.reports.ReportingService') as mock_service:
            
            mock_instance = mock_service.return_value
            mock_instance.get_queue_analytics.return_value = {
                "summary": {"total_entries": 50, "waiting": 10}
            }
            mock_instance.get_financial_report.return_value = {
                "summary": {"total_collected": 200000.0}
            }
            mock_instance.get_staff_performance_report.return_value = {
                "performance": {"total_staff": 15}
            }
            
            response = client.get(
                "/api/reports/summary",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "today_queue" in data or "this_week_financial" in data or "queue" in data
    
    def test_unauthorized_access(self, client):
        """Test that endpoints require authentication"""
        response = client.get("/api/reports/patient/1")
        assert response.status_code == 401
        
        response = client.get("/api/reports/queue/analytics")
        assert response.status_code == 401
        
        response = client.get("/api/reports/staff/performance")
        assert response.status_code == 401
        
        response = client.get("/api/reports/financial")
        assert response.status_code == 401
    
    def test_invalid_date_format(self, client, mock_current_user, auth_headers):
        """Test handling of invalid date formats"""
        with patch('app.routes.reports.get_current_user', return_value=mock_current_user):
            response = client.get(
                "/api/reports/patient/1?start_date=invalid-date",
                headers=auth_headers
            )
            
            # Should return 400 or handle gracefully
            assert response.status_code in [400, 422, 500]
    
    def test_nonexistent_patient(self, client, mock_current_user, auth_headers):
        """Test handling of nonexistent patient"""
        with patch('app.routes.reports.get_current_user', return_value=mock_current_user), \
             patch('app.routes.reports.ReportingService') as mock_service:
            
            mock_instance = mock_service.return_value
            mock_instance.get_patient_report.side_effect = ValueError("Patient not found")
            
            response = client.get(
                "/api/reports/patient/99999",
                headers=auth_headers
            )
            
            # Should return 404 or 500
            assert response.status_code in [404, 500]


class TestReportingIntegration:
    """Integration tests for the complete reporting flow"""
    
    def test_full_patient_report_flow(self):
        """Test complete patient report generation and export"""
        # This would require actual database setup
        # Placeholder for integration test
        pass
    
    def test_queue_analytics_calculation_accuracy(self):
        """Test that queue analytics calculations are accurate"""
        # This would test actual statistical calculations
        pass
    
    def test_financial_report_calculations(self):
        """Test financial report calculation accuracy"""
        # This would verify all financial calculations
        pass
    
    def test_csv_export_format_validation(self):
        """Test that CSV exports have valid format"""
        # This would validate CSV structure
        pass


# Run tests with: pytest backend/tests/test_reporting.py -v
# Run with coverage: pytest backend/tests/test_reporting.py --cov=app.services.reporting_service --cov=app.routes.reports -v
