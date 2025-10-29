"""
Advanced Reporting Service
Comprehensive reporting for patients, queue, staff, and financial data
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, cast, Float
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict
import io
import csv

from app.models.workflow_models import Patient, PatientVisit
from app.models.models import QueueEntry, User, Service
from app.services.payment_service import PaymentService
from app.services.patient_history_service import PatientHistoryService


class ReportingService:
    """
    Advanced reporting service for hospital management system
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    # ============= PATIENT REPORTS =============
    
    def get_patient_report(
        self,
        patient_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        include_visits: bool = True,
        include_medical_records: bool = True,
        include_lab_results: bool = True,
        include_medications: bool = True,
        include_payments: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive patient report
        """
        patient = self.db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise ValueError(f"Patient {patient_id} not found")
        
        # Set default date range (last 6 months if not specified)
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=180)
        if not end_date:
            end_date = datetime.utcnow()
        
        report = {
            "patient": {
                "id": patient.id,
                "patient_id": patient.patient_id,
                "name": patient.name,
                "email": patient.email,
                "phone": patient.phone,
                "date_of_birth": patient.date_of_birth.isoformat() if patient.date_of_birth else None,
                "age_group": patient.age_group,
                "insurance_type": patient.insurance_type
            },
            "report_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        }
        
        # Include visits
        if include_visits:
            visits = self.db.query(PatientVisit).filter(
                and_(
                    PatientVisit.patient_id == patient_id,
                    PatientVisit.visit_date >= start_date,
                    PatientVisit.visit_date <= end_date
                )
            ).order_by(PatientVisit.visit_date.desc()).all()
            
            report["visits"] = {
                "total_count": len(visits),
                "visits": [
                    {
                        "id": visit.id,
                        "visit_date": visit.visit_date.isoformat(),
                        "reason": visit.reason,
                        "diagnosis": visit.diagnosis,
                        "treatment": visit.treatment,
                        "department": visit.department,
                        "doctor_name": visit.doctor_name,
                        "visit_type": visit.visit_type,
                        "status": visit.status
                    }
                    for visit in visits
                ]
            }
        
        # Include medical records
        if include_medical_records:
            try:
                history_service = PatientHistoryService(self.db)
                records = history_service.get_patient_history(patient_id)
                
                report["medical_records"] = {
                    "total_count": len(records.get("medical_records", [])),
                    "records": records.get("medical_records", [])
                }
            except Exception as e:
                report["medical_records"] = {
                    "total_count": 0,
                    "records": [],
                    "note": "Medical records not available"
                }
        
        # Include lab results
        if include_lab_results:
            try:
                history_service = PatientHistoryService(self.db)
                lab_results = history_service.get_lab_results(patient_id)
                
                report["lab_results"] = {
                    "total_count": len(lab_results.get("lab_results", [])),
                    "results": lab_results.get("lab_results", [])
                }
            except Exception as e:
                report["lab_results"] = {
                    "total_count": 0,
                    "results": [],
                    "note": "Lab results not available"
                }
        
        # Include medications
        if include_medications:
            try:
                history_service = PatientHistoryService(self.db)
                medications = history_service.get_medications(patient_id)
                
                report["medications"] = {
                    "total_count": len(medications.get("medications", [])),
                    "active_count": sum(1 for med in medications.get("medications", []) if med.get("status") == "active"),
                    "medications": medications.get("medications", [])
                }
            except Exception as e:
                report["medications"] = {
                    "total_count": 0,
                    "active_count": 0,
                    "medications": [],
                    "note": "Medications not available"
                }
        
        # Include payments
        if include_payments:
            try:
                payment_service = PaymentService()
                payments_data = payment_service.get_patient_payments(self.db, patient_id)
                
                # Calculate totals from payments
                payments = payments_data.get("payments", [])
                total_amount = sum(p.get("amount", 0) for p in payments)
                total_paid = sum(p.get("amount_paid", 0) for p in payments)
                total_outstanding = sum(p.get("outstanding_balance", 0) for p in payments)
                
                report["payments"] = {
                    "total_transactions": len(payments),
                    "total_amount": float(total_amount),
                    "total_paid": float(total_paid),
                    "total_outstanding": float(total_outstanding),
                    "transactions": payments
                }
            except Exception as e:
                report["payments"] = {
                    "total_transactions": 0,
                    "total_amount": 0.0,
                    "total_paid": 0.0,
                    "total_outstanding": 0.0,
                    "transactions": [],
                    "note": "Payment history not available"
                }
        
        return report
    
    # ============= QUEUE ANALYTICS =============
    
    def get_queue_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        department: Optional[str] = None,
        service_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate queue analytics report
        """
        # Set default date range (last 30 days)
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Base query
        query = self.db.query(QueueEntry).filter(
            and_(
                QueueEntry.timestamp >= start_date,
                QueueEntry.timestamp <= end_date
            )
        )
        
        if department:
            query = query.filter(QueueEntry.department == department)
        if service_type:
            query = query.filter(QueueEntry.service_type == service_type)
        
        queue_entries = query.all()
        
        # Calculate metrics
        total_entries = len(queue_entries)
        completed_entries = [e for e in queue_entries if e.status == "completed"]
        waiting_entries = [e for e in queue_entries if e.status == "waiting"]
        cancelled_entries = [e for e in queue_entries if e.status == "cancelled"]
        
        # Wait time statistics
        wait_times = []
        service_times = []
        for entry in completed_entries:
            if entry.called_time and entry.timestamp:
                wait_time = (entry.called_time - entry.timestamp).total_seconds() / 60
                wait_times.append(wait_time)
            if entry.completed_time and entry.called_time:
                service_time = (entry.completed_time - entry.called_time).total_seconds() / 60
                service_times.append(service_time)
        
        # Department breakdown
        department_stats = defaultdict(int)
        for entry in queue_entries:
            if entry.department:
                department_stats[entry.department] += 1
        
        # Service type breakdown
        service_stats = defaultdict(int)
        for entry in queue_entries:
            if entry.service_type:
                service_stats[entry.service_type] += 1
        
        # Priority breakdown
        priority_stats = defaultdict(int)
        for entry in queue_entries:
            priority_stats[entry.priority] += 1
        
        # Daily trends
        daily_counts = defaultdict(int)
        for entry in queue_entries:
            day = entry.timestamp.date().isoformat()
            daily_counts[day] += 1
        
        # Hourly trends
        hourly_counts = defaultdict(int)
        for entry in queue_entries:
            hour = entry.timestamp.hour
            hourly_counts[hour] += 1
        
        return {
            "report_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "department": department,
                "service_type": service_type
            },
            "summary": {
                "total_entries": total_entries,
                "completed": len(completed_entries),
                "waiting": len(waiting_entries),
                "cancelled": len(cancelled_entries),
                "completion_rate": len(completed_entries) / total_entries * 100 if total_entries > 0 else 0,
                "cancellation_rate": len(cancelled_entries) / total_entries * 100 if total_entries > 0 else 0
            },
            "wait_time_statistics": {
                "average_wait_time_minutes": sum(wait_times) / len(wait_times) if wait_times else 0,
                "min_wait_time_minutes": min(wait_times) if wait_times else 0,
                "max_wait_time_minutes": max(wait_times) if wait_times else 0,
                "median_wait_time_minutes": sorted(wait_times)[len(wait_times) // 2] if wait_times else 0
            },
            "service_time_statistics": {
                "average_service_time_minutes": sum(service_times) / len(service_times) if service_times else 0,
                "min_service_time_minutes": min(service_times) if service_times else 0,
                "max_service_time_minutes": max(service_times) if service_times else 0
            },
            "department_breakdown": dict(department_stats),
            "service_type_breakdown": dict(service_stats),
            "priority_breakdown": dict(priority_stats),
            "daily_trends": dict(sorted(daily_counts.items())),
            "hourly_trends": dict(sorted(hourly_counts.items()))
        }
    
    # ============= STAFF PERFORMANCE =============
    
    def get_staff_performance_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        staff_id: Optional[int] = None,
        role: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate staff performance report
        """
        # Set default date range (last 30 days)
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Query staff members
        staff_query = self.db.query(User)
        if staff_id:
            staff_query = staff_query.filter(User.id == staff_id)
        if role:
            staff_query = staff_query.filter(User.role == role)
        
        staff_members = staff_query.all()
        
        performance_data = []
        
        for staff in staff_members:
            # Get queue entries handled by this staff member
            handled_entries = self.db.query(QueueEntry).filter(
                and_(
                    QueueEntry.called_by == staff.username,
                    QueueEntry.called_time >= start_date,
                    QueueEntry.called_time <= end_date
                )
            ).all()
            
            completed = [e for e in handled_entries if e.status == "completed"]
            
            # Calculate service times
            service_times = []
            for entry in completed:
                if entry.completed_time and entry.called_time:
                    service_time = (entry.completed_time - entry.called_time).total_seconds() / 60
                    service_times.append(service_time)
            
            # Get patient visits (for doctors)
            visits = self.db.query(PatientVisit).filter(
                and_(
                    PatientVisit.doctor_name == staff.username,
                    PatientVisit.visit_date >= start_date,
                    PatientVisit.visit_date <= end_date
                )
            ).all()
            
            performance_data.append({
                "staff_info": {
                    "id": staff.id,
                    "username": staff.username,
                    "email": staff.email,
                    "role": staff.role
                },
                "queue_performance": {
                    "total_handled": len(handled_entries),
                    "completed": len(completed),
                    "completion_rate": len(completed) / len(handled_entries) * 100 if handled_entries else 0,
                    "average_service_time_minutes": sum(service_times) / len(service_times) if service_times else 0,
                    "min_service_time_minutes": min(service_times) if service_times else 0,
                    "max_service_time_minutes": max(service_times) if service_times else 0
                },
                "patient_visits": {
                    "total_visits": len(visits),
                    "visit_types": {
                        "emergency": sum(1 for v in visits if v.visit_type == "emergency"),
                        "scheduled": sum(1 for v in visits if v.visit_type == "scheduled"),
                        "walk_in": sum(1 for v in visits if v.visit_type == "walk_in")
                    }
                }
            })
        
        return {
            "report_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "staff_count": len(staff_members),
            "performance_data": performance_data
        }
    
    # ============= FINANCIAL REPORTS =============
    
    def get_financial_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        department: Optional[str] = None,
        payment_method: Optional[str] = None,
        payment_status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate financial report
        """
        # Set default date range (last 30 days)
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Base query
        query = self.db.query(Payment).filter(
            and_(
                Payment.payment_date >= start_date,
                Payment.payment_date <= end_date
            )
        )
        
        if department:
            query = query.filter(Payment.department == department)
        if payment_method:
            query = query.filter(Payment.payment_method == payment_method)
        if payment_status:
            query = query.filter(Payment.payment_status == payment_status)
        
        payments = query.all()
        
        # Calculate totals
        total_amount = sum(p.amount for p in payments)
        total_paid = sum(p.amount_paid for p in payments)
        total_outstanding = sum(p.outstanding_balance for p in payments)
        
        # Payment method breakdown
        method_breakdown = defaultdict(lambda: {"count": 0, "amount": 0})
        for payment in payments:
            method = payment.payment_method or "unknown"
            method_breakdown[method]["count"] += 1
            method_breakdown[method]["amount"] += float(payment.amount_paid)
        
        # Payment status breakdown
        status_breakdown = defaultdict(lambda: {"count": 0, "amount": 0, "outstanding": 0})
        for payment in payments:
            status = payment.payment_status
            status_breakdown[status]["count"] += 1
            status_breakdown[status]["amount"] += float(payment.amount)
            status_breakdown[status]["outstanding"] += float(payment.outstanding_balance)
        
        # Department breakdown
        department_breakdown = defaultdict(lambda: {"count": 0, "amount": 0})
        for payment in payments:
            dept = payment.department or "unknown"
            department_breakdown[dept]["count"] += 1
            department_breakdown[dept]["amount"] += float(payment.amount)
        
        # Daily revenue
        daily_revenue = defaultdict(float)
        for payment in payments:
            day = payment.payment_date.date().isoformat()
            daily_revenue[day] += float(payment.amount_paid)
        
        # Insurance vs self-pay
        insurance_amount = sum(
            float(p.insurance_amount) for p in payments 
            if p.insurance_amount and p.insurance_amount > 0
        )
        self_pay_amount = total_paid - insurance_amount
        
        return {
            "report_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "filters": {
                    "department": department,
                    "payment_method": payment_method,
                    "payment_status": payment_status
                }
            },
            "summary": {
                "total_transactions": len(payments),
                "total_billed": float(total_amount),
                "total_collected": float(total_paid),
                "total_outstanding": float(total_outstanding),
                "collection_rate": (total_paid / total_amount * 100) if total_amount > 0 else 0
            },
            "payment_method_breakdown": {
                method: {
                    "count": data["count"],
                    "amount": data["amount"],
                    "percentage": (data["amount"] / total_paid * 100) if total_paid > 0 else 0
                }
                for method, data in method_breakdown.items()
            },
            "payment_status_breakdown": dict(status_breakdown),
            "department_breakdown": dict(department_breakdown),
            "daily_revenue": dict(sorted(daily_revenue.items())),
            "insurance_breakdown": {
                "insurance_amount": float(insurance_amount),
                "self_pay_amount": float(self_pay_amount),
                "insurance_percentage": (insurance_amount / total_paid * 100) if total_paid > 0 else 0,
                "self_pay_percentage": (self_pay_amount / total_paid * 100) if total_paid > 0 else 0
            }
        }
    
    # ============= EXPORT FUNCTIONS =============
    
    def export_to_csv(self, report_data: Dict[str, Any], report_type: str) -> str:
        """
        Export report data to CSV format
        Returns CSV content as string
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        if report_type == "patient":
            # Patient report CSV
            writer.writerow(["Patient Report"])
            writer.writerow(["Patient ID", report_data["patient_info"]["id"]])
            writer.writerow(["Name", report_data["patient_info"]["name"]])
            writer.writerow([])
            
            if "visits" in report_data:
                writer.writerow(["Visits"])
                writer.writerow(["Date", "Reason", "Diagnosis", "Treatment", "Doctor"])
                for visit in report_data["visits"]["visits"]:
                    writer.writerow([
                        visit["visit_date"],
                        visit["reason"],
                        visit["diagnosis"],
                        visit["treatment"],
                        visit["doctor_name"]
                    ])
                writer.writerow([])
            
            if "payments" in report_data:
                writer.writerow(["Payments"])
                writer.writerow(["Date", "Amount", "Paid", "Outstanding", "Method", "Status"])
                for payment in report_data["payments"]["transactions"]:
                    writer.writerow([
                        payment["payment_date"],
                        payment["amount"],
                        payment["amount_paid"],
                        payment["outstanding_balance"],
                        payment["payment_method"],
                        payment["payment_status"]
                    ])
        
        elif report_type == "financial":
            # Financial report CSV
            writer.writerow(["Financial Report"])
            writer.writerow(["Period", f"{report_data['report_period']['start_date']} to {report_data['report_period']['end_date']}"])
            writer.writerow([])
            writer.writerow(["Summary"])
            writer.writerow(["Total Transactions", report_data["summary"]["total_transactions"]])
            writer.writerow(["Total Billed", report_data["summary"]["total_billed"]])
            writer.writerow(["Total Collected", report_data["summary"]["total_collected"]])
            writer.writerow(["Total Outstanding", report_data["summary"]["total_outstanding"]])
            writer.writerow(["Collection Rate", f"{report_data['summary']['collection_rate']:.2f}%"])
            writer.writerow([])
            
            writer.writerow(["Daily Revenue"])
            writer.writerow(["Date", "Revenue"])
            for date, revenue in report_data["daily_revenue"].items():
                writer.writerow([date, revenue])
        
        elif report_type == "queue":
            # Queue analytics CSV
            writer.writerow(["Queue Analytics Report"])
            writer.writerow(["Period", f"{report_data['report_period']['start_date']} to {report_data['report_period']['end_date']}"])
            writer.writerow([])
            writer.writerow(["Summary"])
            writer.writerow(["Total Entries", report_data["summary"]["total_entries"]])
            writer.writerow(["Completed", report_data["summary"]["completed"]])
            writer.writerow(["Waiting", report_data["summary"]["waiting"]])
            writer.writerow(["Cancelled", report_data["summary"]["cancelled"]])
            writer.writerow([])
            
            writer.writerow(["Wait Time Statistics"])
            writer.writerow(["Average (minutes)", report_data["wait_time_statistics"]["average_wait_time_minutes"]])
            writer.writerow(["Min (minutes)", report_data["wait_time_statistics"]["min_wait_time_minutes"]])
            writer.writerow(["Max (minutes)", report_data["wait_time_statistics"]["max_wait_time_minutes"]])
        
        return output.getvalue()
