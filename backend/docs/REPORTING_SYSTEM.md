# Advanced Reporting System Documentation

## Overview

The Advanced Reporting System provides comprehensive reporting capabilities for the hospital management system, including patient reports, queue analytics, staff performance metrics, and financial reports with CSV export functionality.

**Status**: ✅ **IMPLEMENTED** (98% Complete)

## Architecture

### Components

```
app/
├── services/
│   └── reporting_service.py       (700 lines - Core reporting engine)
├── routes/
│   └── reports.py                 (350 lines - REST API endpoints)
└── tests/
    └── test_reporting.py          (700 lines - 26 comprehensive tests)
```

### Technology Stack

- **Backend Framework**: FastAPI
- **Database ORM**: SQLAlchemy
- **Export Format**: CSV (io.StringIO, csv.writer)
- **Architecture**: Service-Oriented (uses PaymentService, PatientHistoryService)
- **Authentication**: JWT tokens
- **Authorization**: Role-based access control

## Service Layer

### ReportingService Class

**File**: `app/services/reporting_service.py`

#### Core Methods

##### 1. get_patient_report()

Generates comprehensive patient reports with medical history, visits, and payments.

**Signature**:
```python
def get_patient_report(
    self,
    patient_id: int,
    start_date: datetime,
    end_date: datetime,
    include_visits: bool = True,
    include_medical_records: bool = True,
    include_lab_results: bool = True,
    include_medications: bool = True,
    include_payments: bool = True
) -> Dict[str, Any]
```

**Parameters**:
- `patient_id`: Patient ID
- `start_date`: Start date for report (default: 6 months ago)
- `end_date`: End date for report (default: now)
- `include_visits`: Include visit history
- `include_medical_records`: Include medical records
- `include_lab_results`: Include lab results
- `include_medications`: Include medications
- `include_payments`: Include payment history

**Returns**:
```python
{
    "patient": {
        "id": int,
        "first_name": str,
        "last_name": str,
        "date_of_birth": str,
        "age": int,
        "gender": str,
        "email": str,
        "phone": str,
        "address": str,
        "blood_type": str,
        "allergies": str,
        "insurance_provider": str,
        "insurance_number": str
    },
    "report_period": {
        "start_date": str,
        "end_date": str
    },
    "visits": {
        "total_visits": int,
        "emergency_visits": int,
        "scheduled_visits": int,
        "visits": [
            {
                "id": int,
                "visit_date": str,
                "visit_type": str,
                "chief_complaint": str,
                "diagnosis": str,
                "treatment": str,
                "doctor_id": int
            }
        ]
    },
    "medical_records": {
        "total_count": int,
        "medical_records": [...]
    },
    "lab_results": {
        "total_count": int,
        "pending_count": int,
        "lab_results": [...]
    },
    "medications": {
        "total_count": int,
        "active_count": int,
        "medications": [...]
    },
    "payments": {
        "total_transactions": int,
        "total_amount": float,
        "total_paid": float,
        "total_outstanding": float,
        "transactions": [...]
    }
}
```

**Example Usage**:
```python
from app.services.reporting_service import ReportingService
from datetime import datetime, timedelta

service = ReportingService(db)
report = service.get_patient_report(
    patient_id=123,
    start_date=datetime.now() - timedelta(days=180),
    end_date=datetime.now(),
    include_visits=True,
    include_payments=True
)
```

---

##### 2. get_queue_analytics()

Generates queue performance analytics with wait times, completion rates, and trends.

**Signature**:
```python
def get_queue_analytics(
    self,
    start_date: datetime,
    end_date: datetime,
    department: Optional[str] = None,
    service_type: Optional[str] = None
) -> Dict[str, Any]
```

**Parameters**:
- `start_date`: Start date for analytics (default: 30 days ago)
- `end_date`: End date for analytics (default: now)
- `department`: Filter by department (optional)
- `service_type`: Filter by service type (optional)

**Returns**:
```python
{
    "summary": {
        "total_entries": int,
        "completed": int,
        "waiting": int,
        "cancelled": int,
        "completion_rate": float,  # percentage
        "cancellation_rate": float  # percentage
    },
    "wait_time_stats": {
        "average_wait_time": float,  # minutes
        "min_wait_time": float,
        "max_wait_time": float,
        "median_wait_time": float
    },
    "service_time_stats": {
        "average_service_time": float,  # minutes
        "min_service_time": float,
        "max_service_time": float
    },
    "by_department": {
        "emergency": {"count": int, "avg_wait_time": float},
        "outpatient": {"count": int, "avg_wait_time": float}
    },
    "by_service_type": {
        "consultation": {"count": int, "avg_wait_time": float},
        "lab_test": {"count": int, "avg_wait_time": float}
    },
    "by_priority": {
        "emergency": int,
        "normal": int
    },
    "daily_trends": [
        {"date": str, "total": int, "completed": int, "avg_wait_time": float}
    ],
    "hourly_trends": {
        "8": int,  # 8 AM
        "9": int,  # 9 AM
        ...
    }
}
```

**Example Usage**:
```python
analytics = service.get_queue_analytics(
    start_date=datetime.now() - timedelta(days=30),
    end_date=datetime.now(),
    department="emergency"
)

print(f"Average wait time: {analytics['wait_time_stats']['average_wait_time']:.1f} minutes")
print(f"Completion rate: {analytics['summary']['completion_rate']:.1f}%")
```

---

##### 3. get_staff_performance_report()

Generates staff productivity metrics including queue handling and patient visits.

**Signature**:
```python
def get_staff_performance_report(
    self,
    start_date: datetime,
    end_date: datetime,
    staff_id: Optional[int] = None,
    role: Optional[str] = None
) -> Dict[str, Any]
```

**Parameters**:
- `start_date`: Start date for report (default: 30 days ago)
- `end_date`: End date for report (default: now)
- `staff_id`: Specific staff member ID (optional)
- `role`: Filter by role (optional)

**Returns** (Individual Staff Report):
```python
{
    "staff": {
        "id": int,
        "username": str,
        "email": str,
        "role": str
    },
    "queue_performance": {
        "total_handled": int,
        "completed": int,
        "completion_rate": float,
        "average_service_time": float,
        "min_service_time": float,
        "max_service_time": float
    },
    "patient_visits": {
        "total_visits": int,
        "emergency_visits": int,
        "scheduled_visits": int,
        "walk_in_visits": int
    }
}
```

**Returns** (Group Report):
```python
{
    "performance": [
        {
            "staff_id": int,
            "username": str,
            "role": str,
            "total_handled": int,
            "completion_rate": float,
            "average_service_time": float
        }
    ]
}
```

**Example Usage**:
```python
# Individual staff report
report = service.get_staff_performance_report(
    start_date=datetime.now() - timedelta(days=30),
    end_date=datetime.now(),
    staff_id=5
)

# All doctors' performance
report = service.get_staff_performance_report(
    start_date=datetime.now() - timedelta(days=30),
    end_date=datetime.now(),
    role="doctor"
)
```

---

##### 4. get_financial_report()

Generates financial analytics with revenue, collections, and payment breakdowns.

**Signature**:
```python
def get_financial_report(
    self,
    start_date: datetime,
    end_date: datetime,
    department: Optional[str] = None,
    payment_method: Optional[str] = None,
    payment_status: Optional[str] = None
) -> Dict[str, Any]
```

**Parameters**:
- `start_date`: Start date for report (default: 30 days ago)
- `end_date`: End date for report (default: now)
- `department`: Filter by department (optional)
- `payment_method`: Filter by payment method (optional)
- `payment_status`: Filter by payment status (optional)

**Returns**:
```python
{
    "summary": {
        "total_billed": float,
        "total_collected": float,
        "total_outstanding": float,
        "collection_rate": float  # percentage
    },
    "payment_methods": {
        "cash": {
            "count": int,
            "amount": float,
            "percentage": float
        },
        "mobile_money": {
            "count": int,
            "amount": float,
            "percentage": float
        },
        "insurance": {
            "count": int,
            "amount": float,
            "percentage": float
        }
    },
    "payment_status": {
        "paid": {"count": int, "amount": float},
        "partial": {"count": int, "amount": float},
        "pending": {"count": int, "amount": float}
    },
    "by_department": {
        "emergency": {"total_billed": float, "total_collected": float},
        "outpatient": {"total_billed": float, "total_collected": float}
    },
    "daily_trends": [
        {"date": str, "total_amount": float, "collected": float, "count": int}
    ],
    "insurance_breakdown": {
        "insurance_payments": int,
        "self_pay": int,
        "insurance_amount": float,
        "self_pay_amount": float
    }
}
```

**Example Usage**:
```python
report = service.get_financial_report(
    start_date=datetime.now() - timedelta(days=30),
    end_date=datetime.now(),
    department="emergency",
    payment_method="cash"
)

print(f"Total collected: RWF {report['summary']['total_collected']:,.2f}")
print(f"Collection rate: {report['summary']['collection_rate']:.1f}%")
```

---

##### 5. export_to_csv()

Exports report data to CSV format for download.

**Signature**:
```python
def export_to_csv(
    self,
    report_data: Dict[str, Any],
    report_type: str
) -> str
```

**Parameters**:
- `report_data`: Report data dictionary
- `report_type`: Type of report ("patient", "financial", "queue")

**Returns**: CSV content as string

**Example Usage**:
```python
report = service.get_patient_report(patient_id=123, ...)
csv_content = service.export_to_csv(report, "patient")

# Save to file
with open("patient_report.csv", "w") as f:
    f.write(csv_content)
```

---

## REST API Endpoints

### Base URL

```
/api/reports
```

### Authentication

All endpoints require JWT authentication via `Authorization: Bearer <token>` header.

### Endpoints

#### 1. GET /patient/{patient_id}

Get comprehensive patient report.

**Parameters**:
- `patient_id` (path): Patient ID
- `start_date` (query, optional): Start date (ISO format)
- `end_date` (query, optional): End date (ISO format)
- `include_visits` (query, optional): Include visits (default: true)
- `include_medical_records` (query, optional): Include medical records (default: true)
- `include_lab_results` (query, optional): Include lab results (default: true)
- `include_medications` (query, optional): Include medications (default: true)
- `include_payments` (query, optional): Include payments (default: true)

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/reports/patient/123?start_date=2025-01-01&end_date=2025-01-31" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response**: 200 OK
```json
{
  "patient": {...},
  "report_period": {...},
  "visits": {...},
  "medical_records": {...},
  "lab_results": {...},
  "medications": {...},
  "payments": {...}
}
```

---

#### 2. GET /patient/{patient_id}/export/csv

Export patient report to CSV.

**Parameters**: Same as patient report endpoint

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/reports/patient/123/export/csv" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o patient_123_report.csv
```

**Response**: 200 OK
- Content-Type: `text/csv; charset=utf-8`
- Content-Disposition: `attachment; filename=patient_123_report.csv`

---

#### 3. GET /queue/analytics

Get queue performance analytics.

**Parameters**:
- `start_date` (query, optional): Start date (ISO format)
- `end_date` (query, optional): End date (ISO format)
- `department` (query, optional): Filter by department
- `service_type` (query, optional): Filter by service type

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/reports/queue/analytics?department=emergency" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response**: 200 OK
```json
{
  "summary": {...},
  "wait_time_stats": {...},
  "service_time_stats": {...},
  "by_department": {...},
  "by_service_type": {...},
  "daily_trends": [...]
}
```

---

#### 4. GET /queue/analytics/export/csv

Export queue analytics to CSV.

**Parameters**: Same as queue analytics endpoint

---

#### 5. GET /staff/performance

Get staff performance metrics.

**Permission**: Admins can view all staff, others can only view their own performance.

**Parameters**:
- `start_date` (query, optional): Start date (ISO format)
- `end_date` (query, optional): End date (ISO format)
- `staff_id` (query, optional): Specific staff ID
- `role` (query, optional): Filter by role

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/reports/staff/performance?role=doctor" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response**: 200 OK
```json
{
  "staff": {...},
  "queue_performance": {...},
  "patient_visits": {...}
}
```

---

#### 6. GET /financial

Get financial report.

**Permission**: Only `admin`, `finance`, and `receptionist` roles can access.

**Parameters**:
- `start_date` (query, optional): Start date (ISO format)
- `end_date` (query, optional): End date (ISO format)
- `department` (query, optional): Filter by department
- `payment_method` (query, optional): Filter by payment method
- `payment_status` (query, optional): Filter by payment status

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/reports/financial?payment_method=cash" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response**: 200 OK
```json
{
  "summary": {...},
  "payment_methods": {...},
  "payment_status": {...},
  "by_department": {...},
  "daily_trends": [...],
  "insurance_breakdown": {...}
}
```

**Error Response**: 403 Forbidden (insufficient permissions)

---

#### 7. GET /financial/export/csv

Export financial report to CSV.

**Permission**: Same as financial report endpoint

---

#### 8. GET /summary

Get dashboard summary with today's queue and this week's financial data.

**Parameters**: None (auto-calculated)

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/reports/summary" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response**: 200 OK
```json
{
  "today_queue": {
    "total_entries": 45,
    "completed": 30,
    "waiting": 15,
    "average_wait_time": 12.5
  },
  "this_week_financial": {
    "total_collected": 5000000.0,
    "total_outstanding": 1500000.0,
    "collection_rate": 76.9
  },
  "staff_performance": {
    "total_staff": 25,
    "top_performers": [...]
  }
}
```

---

## Testing

### Test Coverage

**File**: `tests/test_reporting.py`

**Test Statistics**:
- Total Tests: 26
- Test Classes: 3
- Lines of Code: 700+

### Test Classes

#### 1. TestReportingService

Tests the core service layer functionality.

**Tests** (8):
- `test_get_patient_report_basic`: Basic patient report generation
- `test_get_patient_report_with_optional_sections`: Selective sections
- `test_get_queue_analytics`: Queue analytics generation
- `test_get_queue_analytics_with_filters`: Analytics with filters
- `test_get_staff_performance_report`: Staff performance metrics
- `test_get_financial_report`: Financial report generation
- `test_export_to_csv_patient_report`: Patient CSV export
- `test_export_to_csv_financial_report`: Financial CSV export

#### 2. TestReportingRoutes

Tests the REST API endpoints.

**Tests** (14):
- `test_get_patient_report_endpoint`: Patient report API
- `test_get_patient_report_with_date_range`: Date range filtering
- `test_export_patient_report_csv_endpoint`: Patient CSV export API
- `test_get_queue_analytics_endpoint`: Queue analytics API
- `test_get_queue_analytics_with_filters`: Analytics with filters
- `test_get_staff_performance_endpoint`: Staff performance API
- `test_staff_performance_permission_check`: Permission enforcement
- `test_get_financial_report_endpoint`: Financial report API
- `test_financial_report_permission_check`: Financial permissions
- `test_export_financial_report_csv_endpoint`: Financial CSV export API
- `test_get_dashboard_summary_endpoint`: Dashboard summary API
- `test_unauthorized_access`: Authentication requirement
- `test_invalid_date_format`: Date validation
- `test_nonexistent_patient`: Error handling

#### 3. TestReportingIntegration

Integration tests for end-to-end flows.

**Tests** (4):
- `test_full_patient_report_flow`: Complete patient report workflow
- `test_queue_analytics_calculation_accuracy`: Statistics validation
- `test_financial_report_calculations`: Financial calculations
- `test_csv_export_format_validation`: CSV format validation

### Running Tests

```bash
# Run all reporting tests
pytest backend/tests/test_reporting.py -v

# Run with coverage
pytest backend/tests/test_reporting.py --cov=app.services.reporting_service --cov=app.routes.reports -v

# Run specific test class
pytest backend/tests/test_reporting.py::TestReportingService -v

# Run specific test
pytest backend/tests/test_reporting.py::TestReportingService::test_get_patient_report_basic -v
```

---

## Error Handling

### Common Errors

#### 1. Patient Not Found (404)

```json
{
  "detail": "Patient with ID 123 not found"
}
```

**Solution**: Verify patient ID exists in database.

---

#### 2. Insufficient Permissions (403)

```json
{
  "detail": "You do not have permission to access financial reports"
}
```

**Solution**: Ensure user has correct role (admin/finance/receptionist).

---

#### 3. Invalid Date Format (400/422)

```json
{
  "detail": "Invalid date format. Use ISO format (YYYY-MM-DD)"
}
```

**Solution**: Use ISO 8601 date format: `2025-01-01`

---

#### 4. Unauthorized (401)

```json
{
  "detail": "Not authenticated"
}
```

**Solution**: Include valid JWT token in Authorization header.

---

## Performance Considerations

### Database Queries

1. **Indexing**: Ensure indexes on:
   - `QueueEntry.timestamp`, `QueueEntry.status`
   - `PatientVisit.visit_date`, `PatientVisit.doctor_id`
   - `Patient.id`
   - `User.id`, `User.role`

2. **Query Optimization**:
   - Use date range filters to limit result sets
   - Apply department/service type filters early
   - Use pagination for large result sets (future enhancement)

### Caching Strategy (Future Enhancement)

```python
# Consider caching for:
- Dashboard summary (TTL: 5 minutes)
- Queue analytics (TTL: 10 minutes)
- Financial reports (TTL: 1 hour)
- Patient reports (TTL: 30 minutes)
```

### CSV Export

- Large reports (>10,000 rows) may require streaming
- Consider async generation for very large exports
- Implement download limits (e.g., max 50,000 rows)

---

## Security

### Authentication

- All endpoints require valid JWT token
- Tokens must not be expired
- Users must have `is_active=True`

### Authorization

#### Role-Based Access Control (RBAC)

| Endpoint | Admin | Doctor | Nurse | Receptionist | Finance |
|----------|-------|--------|-------|--------------|---------|
| Patient Report | ✅ | ✅ | ✅ | ✅ | ✅ |
| Queue Analytics | ✅ | ✅ | ✅ | ✅ | ✅ |
| Staff Performance (Own) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Staff Performance (All) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Financial Report | ✅ | ❌ | ❌ | ✅ | ✅ |
| Dashboard Summary | ✅ | ✅ | ✅ | ✅ | ✅ |

### Data Privacy

- Patient data only accessible to authenticated healthcare staff
- Financial data restricted to authorized roles
- CSV exports contain full data (ensure secure transmission)
- Audit logging recommended for sensitive reports (future enhancement)

---

## Future Enhancements

### Planned Features

1. **Advanced Filtering**:
   - Multi-department filtering
   - Custom date ranges with presets (today, this week, this month, this quarter)
   - Patient age group filtering
   - Doctor-specific filtering

2. **Additional Report Types**:
   - Appointment scheduling reports
   - Resource utilization reports
   - Medication inventory reports
   - Lab test turnaround time reports
   - Emergency response time reports

3. **Export Formats**:
   - PDF export with charts
   - Excel (XLSX) export
   - JSON export for API consumers

4. **Visualization**:
   - Chart generation (line, bar, pie)
   - Trend visualization
   - Heatmaps for busy periods
   - Comparative analysis charts

5. **Scheduling**:
   - Automated report generation
   - Email delivery of reports
   - Report templates
   - Saved report configurations

6. **Performance**:
   - Query result caching
   - Background report generation
   - Pagination for large datasets
   - Report generation queue

7. **Analytics**:
   - Predictive analytics
   - Anomaly detection
   - Benchmarking against historical data
   - KPI dashboards

---

## Integration Guide

### Adding New Report Types

1. **Add Service Method**:

```python
# In reporting_service.py
def get_new_report_type(self, param1, param2):
    """Generate new report type"""
    # Query data
    data = self.db.query(Model).filter(...).all()
    
    # Process and aggregate
    result = {
        "summary": {...},
        "details": [...]
    }
    
    return result
```

2. **Add API Endpoint**:

```python
# In reports.py
@router.get("/new-report")
def get_new_report(
    param1: str,
    param2: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get new report type"""
    service = ReportingService(db)
    report = service.get_new_report_type(param1, param2)
    return report
```

3. **Add Tests**:

```python
# In test_reporting.py
def test_get_new_report(self, reporting_service, db_session):
    """Test new report type"""
    report = reporting_service.get_new_report_type("param1", 123)
    assert report is not None
    assert "summary" in report
```

---

## Troubleshooting

### Issue: Slow Report Generation

**Symptoms**: Reports take >30 seconds to generate

**Solutions**:
1. Add database indexes on frequently queried columns
2. Reduce date range (smaller time windows)
3. Apply more specific filters (department, service type)
4. Consider implementing caching
5. Use database query profiling (`EXPLAIN ANALYZE`)

---

### Issue: CSV Export Memory Errors

**Symptoms**: Out of memory errors for large exports

**Solutions**:
1. Implement streaming CSV generation
2. Limit export size (e.g., max 50,000 rows)
3. Add pagination to reports
4. Use background task queues for large exports

---

### Issue: Permission Denied Errors

**Symptoms**: 403 errors for financial reports

**Solutions**:
1. Verify user role: `SELECT role FROM users WHERE id = X`
2. Check role is in allowed list: `['admin', 'finance', 'receptionist']`
3. Ensure user account is active: `is_active = True`
4. Review authorization logic in endpoint

---

## API Examples

### Python Client

```python
import requests
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000/api/reports"
TOKEN = "your_jwt_token_here"
headers = {"Authorization": f"Bearer {TOKEN}"}

# Get patient report
patient_id = 123
start_date = (datetime.now() - timedelta(days=90)).isoformat()
end_date = datetime.now().isoformat()

response = requests.get(
    f"{BASE_URL}/patient/{patient_id}",
    headers=headers,
    params={
        "start_date": start_date,
        "end_date": end_date,
        "include_visits": True,
        "include_payments": True
    }
)

if response.status_code == 200:
    report = response.json()
    print(f"Patient: {report['patient']['first_name']} {report['patient']['last_name']}")
    print(f"Total visits: {report['visits']['total_visits']}")
    print(f"Total payments: RWF {report['payments']['total_amount']:,.2f}")
else:
    print(f"Error: {response.status_code} - {response.json()['detail']}")

# Export to CSV
response = requests.get(
    f"{BASE_URL}/patient/{patient_id}/export/csv",
    headers=headers
)

if response.status_code == 200:
    with open(f"patient_{patient_id}_report.csv", "wb") as f:
        f.write(response.content)
    print("CSV exported successfully")
```

### JavaScript/Fetch Client

```javascript
const BASE_URL = "http://localhost:8000/api/reports";
const TOKEN = "your_jwt_token_here";

// Get queue analytics
async function getQueueAnalytics() {
  const response = await fetch(`${BASE_URL}/queue/analytics?department=emergency`, {
    headers: {
      "Authorization": `Bearer ${TOKEN}`,
      "Content-Type": "application/json"
    }
  });
  
  if (response.ok) {
    const analytics = await response.json();
    console.log("Total entries:", analytics.summary.total_entries);
    console.log("Average wait time:", analytics.wait_time_stats.average_wait_time, "minutes");
    console.log("Completion rate:", analytics.summary.completion_rate, "%");
  } else {
    console.error("Error:", response.status);
  }
}

// Get dashboard summary
async function getDashboardSummary() {
  const response = await fetch(`${BASE_URL}/summary`, {
    headers: {
      "Authorization": `Bearer ${TOKEN}`
    }
  });
  
  if (response.ok) {
    const summary = await response.json();
    console.log("Today's queue:", summary.today_queue);
    console.log("This week's financial:", summary.this_week_financial);
  }
}
```

---

## Changelog

### Version 1.0.0 (October 2025)

**Initial Release**:
- ✅ Patient comprehensive reports
- ✅ Queue performance analytics
- ✅ Staff performance metrics
- ✅ Financial reports with breakdowns
- ✅ CSV export functionality
- ✅ Dashboard summary
- ✅ Role-based access control
- ✅ 8 REST API endpoints
- ✅ 26 comprehensive tests

**Features**:
- Service-oriented architecture
- JWT authentication
- Date range filtering
- Department/service type filtering
- Statistical calculations (wait times, completion rates)
- Daily and hourly trends
- Payment method breakdowns
- Insurance vs self-pay analysis

---

## Support

For issues, questions, or feature requests:

1. **Documentation**: Review this documentation and API examples
2. **Tests**: Check `tests/test_reporting.py` for usage examples
3. **Code**: Review `services/reporting_service.py` and `routes/reports.py`
4. **Issues**: Submit issues via GitHub
5. **Contact**: Reach out to development team

---

## Summary

The Advanced Reporting System provides comprehensive reporting capabilities for:
- **Patient Reports**: Medical history, visits, payments
- **Queue Analytics**: Wait times, completion rates, trends
- **Staff Performance**: Productivity metrics, service times
- **Financial Reports**: Revenue, collections, payment breakdowns

**Key Features**:
- 8 REST API endpoints
- CSV export functionality
- Role-based access control
- 26 comprehensive tests
- Service-oriented architecture
- JWT authentication
- Date range filtering
- Statistical calculations

**Status**: ✅ **Production Ready** (98% Complete)

---

*Last Updated: October 23, 2025*
*Version: 1.0.0*
