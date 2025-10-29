"""
Analytics Service
Provides comprehensive analytics, KPIs, and insights for the hospital management system.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case, extract
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import statistics

from app.models.models import (
    QueueEntry, Service, ServiceCounter, User, Appointment,
    Notification, Analytics
)


class AnalyticsService:
    """
    Comprehensive analytics service for hospital queue management.
    
    Features:
    - KPI calculations (wait times, throughput, utilization)
    - Trend analysis (daily, weekly, monthly)
    - Predictive insights (peak times, bottlenecks)
    - Performance metrics (service efficiency, staff productivity)
    - Comparative analysis (period-over-period)
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== KPI CALCULATIONS ====================
    
    def get_overview_kpis(self, period_days: int = 7) -> Dict:
        """
        Get high-level KPIs for dashboard overview.
        
        Returns:
        - total_patients: Total patients served
        - avg_wait_time: Average wait time in minutes
        - active_services: Number of active services
        - efficiency_score: Overall system efficiency (0-1)
        - patient_satisfaction: Average satisfaction score
        - revenue: Total revenue generated
        """
        start_date = datetime.utcnow() - timedelta(days=period_days)
        
        # Total patients
        total_patients = self.db.query(func.count(QueueEntry.id)).filter(
            QueueEntry.created_at >= start_date
        ).scalar() or 0
        
        # Average wait time
        avg_wait = self.db.query(func.avg(QueueEntry.ai_predicted_wait)).filter(
            and_(
                QueueEntry.created_at >= start_date,
                QueueEntry.ai_predicted_wait.isnot(None)
            )
        ).scalar() or 0
        
        # Active services (count all services)
        active_services = self.db.query(func.count(Service.id)).scalar() or 0
        
        # Efficiency score (based on wait time vs target)
        target_wait_time = 15  # minutes
        efficiency_score = max(0, min(1, 1 - (avg_wait - target_wait_time) / 60)) if avg_wait else 1.0
        
        # Patient satisfaction (estimated based on wait time - lower wait = higher satisfaction)
        # Scale: 5.0 (0 min wait) to 1.0 (60+ min wait)
        satisfaction = max(1.0, 5.0 - (avg_wait / 15.0)) if avg_wait else 5.0
        
        # Total appointments count (Appointment model has no fee field)
        total_appointments = self.db.query(func.count(Appointment.id)).filter(
            and_(
                Appointment.created_at >= start_date,
                Appointment.status == "completed"
            )
        ).scalar() or 0
        
        return {
            "total_patients": total_patients,
            "avg_wait_time": round(float(avg_wait), 2),
            "active_services": active_services,
            "efficiency_score": round(efficiency_score, 3),
            "patient_satisfaction": round(float(satisfaction), 2),
            "total_appointments": total_appointments,
            "period_days": period_days
        }
    
    def get_service_kpis(self, service_id: Optional[int] = None, period_days: int = 7) -> List[Dict]:
        """
        Get KPIs for each service or a specific service.
        
        Returns list of:
        - service_id, service_name
        - total_patients
        - avg_wait_time
        - throughput (patients/hour)
        - utilization (0-1)
        - active_counters
        """
        start_date = datetime.utcnow() - timedelta(days=period_days)
        
        # Query services
        services_query = self.db.query(Service)
        if service_id:
            services_query = services_query.filter(Service.id == service_id)
        services = services_query.all()
        
        results = []
        for service in services:
            # Total patients
            total_patients = self.db.query(func.count(QueueEntry.id)).filter(
                and_(
                    QueueEntry.service_id == service.id,
                    QueueEntry.created_at >= start_date
                )
            ).scalar() or 0
            
            # Average wait time
            avg_wait = self.db.query(func.avg(QueueEntry.ai_predicted_wait)).filter(
                and_(
                    QueueEntry.service_id == service.id,
                    QueueEntry.created_at >= start_date,
                    QueueEntry.ai_predicted_wait.isnot(None)
                )
            ).scalar() or 0
            
            # Throughput (patients per hour)
            hours = period_days * 24
            throughput = total_patients / hours if hours > 0 else 0
            
            # Active counters
            active_counters = self.db.query(func.count(ServiceCounter.id)).filter(
                ServiceCounter.service_id == service.id
            ).scalar() or 0
            
            # Utilization (based on queue length vs capacity)
            current_queue = service.queue_length or 0
            capacity = active_counters * 10  # Assume 10 patients per counter capacity
            utilization = min(1.0, current_queue / capacity) if capacity > 0 else 0
            
            results.append({
                "service_id": service.id,
                "service_name": service.name,
                "total_patients": total_patients,
                "avg_wait_time": round(float(avg_wait), 2),
                "throughput": round(throughput, 2),
                "utilization": round(utilization, 3),
                "active_counters": active_counters,
                "current_queue_length": current_queue
            })
        
        return results
    
    def get_staff_performance(self, period_days: int = 7) -> List[Dict]:
        """
        Get staff performance metrics.
        
        Returns list of:
        - user_id, name
        - patients_served
        - avg_service_time
        - active_hours
        - efficiency_rating
        """
        start_date = datetime.utcnow() - timedelta(days=period_days)
        
        # Get staff users (doctors, nurses, receptionists)
        staff = self.db.query(User).filter(
            User.role.in_(['doctor', 'nurse', 'receptionist'])
        ).all()
        
        results = []
        for user in staff:
            # Patients served (via service counters)
            counters = self.db.query(ServiceCounter).filter(
                ServiceCounter.staff_member == user.name
            ).all()
            
            patients_served = 0
            total_service_time = 0
            
            for counter in counters:
                # Count patients served at this counter
                served = self.db.query(func.count(QueueEntry.id)).filter(
                    and_(
                        QueueEntry.service_id == counter.service_id,
                        QueueEntry.status == "completed",
                        QueueEntry.created_at >= start_date
                    )
                ).scalar() or 0
                
                patients_served += served
                
                # Calculate average service time
                avg_time = self.db.query(func.avg(QueueEntry.ai_predicted_wait)).filter(
                    and_(
                        QueueEntry.service_id == counter.service_id,
                        QueueEntry.created_at >= start_date
                    )
                ).scalar() or 0
                
                total_service_time += float(avg_time) * served
            
            avg_service_time = total_service_time / patients_served if patients_served > 0 else 0
            
            # Active hours (assume 8 hours per day for active counters)
            active_hours = len([c for c in counters if c.is_active]) * period_days * 8
            
            # Efficiency rating (patients per hour)
            efficiency = patients_served / active_hours if active_hours > 0 else 0
            
            results.append({
                "user_id": user.id,
                "name": user.name,
                "role": user.role,
                "patients_served": patients_served,
                "avg_service_time": round(avg_service_time, 2),
                "active_hours": active_hours,
                "efficiency_rating": round(efficiency, 3)
            })
        
        # Sort by patients served (descending)
        results.sort(key=lambda x: x["patients_served"], reverse=True)
        
        return results
    
    # ==================== TREND ANALYSIS ====================
    
    def get_wait_time_trends(self, period_days: int = 30) -> List[Dict]:
        """
        Get wait time trends over time (daily granularity).
        
        Returns list of:
        - date
        - avg_wait_time
        - min_wait_time
        - max_wait_time
        - patient_count
        """
        start_date = datetime.utcnow() - timedelta(days=period_days)
        
        trends = self.db.query(
            func.date(QueueEntry.created_at).label('date'),
            func.avg(QueueEntry.ai_predicted_wait).label('avg_wait'),
            func.min(QueueEntry.ai_predicted_wait).label('min_wait'),
            func.max(QueueEntry.ai_predicted_wait).label('max_wait'),
            func.count(QueueEntry.id).label('patient_count')
        ).filter(
            and_(
                QueueEntry.created_at >= start_date,
                QueueEntry.ai_predicted_wait.isnot(None)
            )
        ).group_by(
            func.date(QueueEntry.created_at)
        ).order_by(
            func.date(QueueEntry.created_at)
        ).all()
        
        return [
            {
                "date": str(trend.date),
                "avg_wait_time": round(float(trend.avg_wait), 2),
                "min_wait_time": round(float(trend.min_wait), 2),
                "max_wait_time": round(float(trend.max_wait), 2),
                "patient_count": trend.patient_count
            }
            for trend in trends
        ]
    
    def get_hourly_traffic(self, period_days: int = 7) -> List[Dict]:
        """
        Get hourly traffic patterns.
        
        Returns list of:
        - hour (0-23)
        - avg_patients
        - avg_wait_time
        """
        start_date = datetime.utcnow() - timedelta(days=period_days)
        
        # Group by hour
        hourly_data = self.db.query(
            extract('hour', QueueEntry.created_at).label('hour'),
            func.count(QueueEntry.id).label('patient_count'),
            func.avg(QueueEntry.ai_predicted_wait).label('avg_wait')
        ).filter(
            QueueEntry.created_at >= start_date
        ).group_by(
            extract('hour', QueueEntry.created_at)
        ).order_by(
            extract('hour', QueueEntry.created_at)
        ).all()
        
        # Calculate average per day
        results = []
        for data in hourly_data:
            results.append({
                "hour": int(data.hour),
                "avg_patients": round(data.patient_count / period_days, 2),
                "avg_wait_time": round(float(data.avg_wait or 0), 2)
            })
        
        return results
    
    def get_service_trends(self, period_days: int = 30) -> List[Dict]:
        """
        Get service usage trends over time.
        
        Returns list of:
        - service_id, service_name
        - daily_trends: [{date, patient_count, avg_wait}]
        """
        start_date = datetime.utcnow() - timedelta(days=period_days)
        
        services = self.db.query(Service).all()
        results = []
        
        for service in services:
            # Get daily data for this service
            daily_data = self.db.query(
                func.date(QueueEntry.created_at).label('date'),
                func.count(QueueEntry.id).label('patient_count'),
                func.avg(QueueEntry.ai_predicted_wait).label('avg_wait')
            ).filter(
                and_(
                    QueueEntry.service_id == service.id,
                    QueueEntry.created_at >= start_date
                )
            ).group_by(
                func.date(QueueEntry.created_at)
            ).order_by(
                func.date(QueueEntry.created_at)
            ).all()
            
            trends = [
                {
                    "date": str(data.date),
                    "patient_count": data.patient_count,
                    "avg_wait": round(float(data.avg_wait or 0), 2)
                }
                for data in daily_data
            ]
            
            results.append({
                "service_id": service.id,
                "service_name": service.name,
                "daily_trends": trends
            })
        
        return results
    
    # ==================== PREDICTIVE INSIGHTS ====================
    
    def predict_peak_times(self, look_ahead_days: int = 7) -> List[Dict]:
        """
        Predict peak times based on historical data.
        
        Returns list of:
        - day_of_week
        - hour
        - expected_patients
        - confidence_level
        """
        # Analyze last 30 days
        start_date = datetime.utcnow() - timedelta(days=30)
        
        # Get historical data grouped by day of week and hour
        historical = self.db.query(
            extract('dow', QueueEntry.created_at).label('day_of_week'),
            extract('hour', QueueEntry.created_at).label('hour'),
            func.count(QueueEntry.id).label('patient_count')
        ).filter(
            QueueEntry.created_at >= start_date
        ).group_by(
            extract('dow', QueueEntry.created_at),
            extract('hour', QueueEntry.created_at)
        ).all()
        
        # Calculate averages and confidence
        predictions = defaultdict(lambda: {"counts": [], "hours": []})
        for record in historical:
            key = (int(record.day_of_week), int(record.hour))
            predictions[key]["counts"].append(record.patient_count)
        
        results = []
        for (dow, hour), data in predictions.items():
            counts = data["counts"]
            avg_patients = statistics.mean(counts)
            
            # Confidence based on standard deviation
            if len(counts) > 1:
                std_dev = statistics.stdev(counts)
                confidence = max(0, min(1, 1 - (std_dev / avg_patients))) if avg_patients > 0 else 0
            else:
                confidence = 0.5
            
            results.append({
                "day_of_week": dow,
                "hour": hour,
                "expected_patients": round(avg_patients, 1),
                "confidence_level": round(confidence, 3)
            })
        
        # Sort by expected patients (descending)
        results.sort(key=lambda x: x["expected_patients"], reverse=True)
        
        return results[:24]  # Return top 24 peak periods
    
    def identify_bottlenecks(self) -> List[Dict]:
        """
        Identify system bottlenecks and congestion points.
        
        Returns list of:
        - bottleneck_type (service, staff, time)
        - description
        - severity (critical, high, medium, low)
        - affected_entity
        - recommended_action
        """
        bottlenecks = []
        
        # Check service bottlenecks (high wait times)
        services = self.db.query(Service).all()
        for service in services:
            avg_wait = self.db.query(func.avg(QueueEntry.ai_predicted_wait)).filter(
                and_(
                    QueueEntry.service_id == service.id,
                    QueueEntry.status == "waiting",
                    QueueEntry.ai_predicted_wait.isnot(None)
                )
            ).scalar() or 0
            
            if avg_wait > 45:
                bottlenecks.append({
                    "bottleneck_type": "service",
                    "description": f"High wait times in {service.name}",
                    "severity": "critical" if avg_wait > 60 else "high",
                    "affected_entity": service.name,
                    "metric_value": round(float(avg_wait), 2),
                    "recommended_action": "Increase counter capacity or optimize service flow"
                })
        
        # Check staff bottlenecks (overutilization)
        staff_metrics = self.get_staff_performance(period_days=1)
        for staff in staff_metrics:
            if staff["efficiency_rating"] > 10:  # More than 10 patients per hour
                bottlenecks.append({
                    "bottleneck_type": "staff",
                    "description": f"High workload for {staff['name']}",
                    "severity": "high",
                    "affected_entity": staff["name"],
                    "metric_value": staff["efficiency_rating"],
                    "recommended_action": "Consider redistributing workload or adding support staff"
                })
        
        # Check time-based bottlenecks (peak hour congestion)
        current_hour = datetime.utcnow().hour
        hourly_traffic = self.get_hourly_traffic(period_days=7)
        
        for traffic in hourly_traffic:
            if traffic["avg_patients"] > 20 and traffic["avg_wait_time"] > 30:
                bottlenecks.append({
                    "bottleneck_type": "time",
                    "description": f"Peak hour congestion at {traffic['hour']}:00",
                    "severity": "medium",
                    "affected_entity": f"Hour {traffic['hour']}",
                    "metric_value": traffic["avg_patients"],
                    "recommended_action": "Increase staffing during peak hours"
                })
        
        return bottlenecks
    
    # ==================== COMPARATIVE ANALYSIS ====================
    
    def compare_periods(
        self, 
        current_days: int = 7, 
        previous_days: int = 7
    ) -> Dict:
        """
        Compare current period with previous period.
        
        Returns:
        - current_period: KPIs for current period
        - previous_period: KPIs for previous period
        - changes: Percentage changes for each KPI
        """
        # Get current period KPIs
        current_kpis = self.get_overview_kpis(period_days=current_days)
        
        # Get previous period KPIs
        # Temporarily adjust database query to look at earlier period
        offset_start = datetime.utcnow() - timedelta(days=current_days + previous_days)
        offset_end = datetime.utcnow() - timedelta(days=current_days)
        
        # Total patients (previous)
        prev_total_patients = self.db.query(func.count(QueueEntry.id)).filter(
            and_(
                QueueEntry.created_at >= offset_start,
                QueueEntry.created_at < offset_end
            )
        ).scalar() or 0
        
        # Average wait time (previous)
        prev_avg_wait = self.db.query(func.avg(QueueEntry.ai_predicted_wait)).filter(
            and_(
                QueueEntry.created_at >= offset_start,
                QueueEntry.created_at < offset_end,
                QueueEntry.ai_predicted_wait.isnot(None)
            )
        ).scalar() or 0
        
        # Total appointments (previous)
        prev_appointments = self.db.query(func.count(Appointment.id)).filter(
            and_(
                Appointment.created_at >= offset_start,
                Appointment.created_at < offset_end,
                Appointment.status == "completed"
            )
        ).scalar() or 0
        
        # Satisfaction (previous) - estimated based on wait time
        prev_satisfaction = max(1.0, 5.0 - (float(prev_avg_wait) / 15.0)) if prev_avg_wait else 5.0
        
        previous_kpis = {
            "total_patients": prev_total_patients,
            "avg_wait_time": round(float(prev_avg_wait), 2),
            "total_appointments": prev_appointments,
            "patient_satisfaction": round(float(prev_satisfaction), 2)
        }
        
        # Calculate changes
        def calc_change(current, previous):
            if previous == 0:
                return 100.0 if current > 0 else 0.0
            return round(((current - previous) / previous) * 100, 2)
        
        changes = {
            "total_patients": calc_change(
                current_kpis["total_patients"], 
                previous_kpis["total_patients"]
            ),
            "avg_wait_time": calc_change(
                current_kpis["avg_wait_time"], 
                previous_kpis["avg_wait_time"]
            ),
            "total_appointments": calc_change(
                current_kpis["total_appointments"], 
                previous_kpis["total_appointments"]
            ),
            "patient_satisfaction": calc_change(
                current_kpis["patient_satisfaction"], 
                previous_kpis["patient_satisfaction"]
            )
        }
        
        return {
            "current_period": current_kpis,
            "previous_period": previous_kpis,
            "changes": changes,
            "comparison_note": f"Comparing last {current_days} days vs previous {previous_days} days"
        }
    
    # ==================== FINANCIAL ANALYTICS ====================
    
    def get_revenue_analytics(self, period_days: int = 30) -> Dict:
        """
        Get appointment analytics (note: Appointment model has no fee field).
        
        Returns:
        - total_appointments: Count of completed appointments
        - appointments_by_service: Breakdown by service
        - appointment_trend: Daily appointment counts
        - appointment_status_breakdown: Status distribution
        - scheduled_appointments: Upcoming appointments
        """
        start_date = datetime.utcnow() - timedelta(days=period_days)
        
        # Total completed appointments
        total_appointments = self.db.query(func.count(Appointment.id)).filter(
            and_(
                Appointment.created_at >= start_date,
                Appointment.status == "completed"
            )
        ).scalar() or 0
        
        # Appointments by service
        appointments_by_service = self.db.query(
            Service.name,
            func.count(Appointment.id).label('appointment_count')
        ).join(
            Appointment, Appointment.service_id == Service.id
        ).filter(
            and_(
                Appointment.created_at >= start_date,
                Appointment.status == "completed"
            )
        ).group_by(
            Service.name
        ).all()
        
        # Appointment trend (daily)
        appointment_trend = self.db.query(
            func.date(Appointment.appointment_date).label('date'),
            func.count(Appointment.id).label('appointments')
        ).filter(
            and_(
                Appointment.created_at >= start_date,
                Appointment.status == "completed"
            )
        ).group_by(
            func.date(Appointment.appointment_date)
        ).order_by(
            func.date(Appointment.appointment_date)
        ).all()
        
        # Appointment status breakdown
        status_breakdown = self.db.query(
            Appointment.status,
            func.count(Appointment.id).label('count')
        ).filter(
            Appointment.created_at >= start_date
        ).group_by(
            Appointment.status
        ).all()
        
        # Scheduled appointments (upcoming)
        scheduled_count = self.db.query(func.count(Appointment.id)).filter(
            and_(
                Appointment.created_at >= start_date,
                Appointment.status == "scheduled"
            )
        ).scalar() or 0
        
        return {
            "total_appointments": total_appointments,
            "appointments_by_service": [
                {
                    "service_name": row.name,
                    "appointment_count": row.appointment_count
                }
                for row in appointments_by_service
            ],
            "appointment_trend": [
                {
                    "date": str(row.date),
                    "appointments": row.appointments
                }
                for row in appointment_trend
            ],
            "status_breakdown": [
                {
                    "status": row.status,
                    "count": row.count
                }
                for row in status_breakdown
            ],
            "scheduled_appointments": scheduled_count,
            "period_days": period_days,
            "note": "Revenue tracking not available (Appointment model has no fee field)"
        }
        
        # Outstanding revenue (scheduled appointments)
        outstanding = self.db.query(func.sum(Appointment.fee)).filter(
            and_(
                Appointment.date >= start_date,
                Appointment.status == "scheduled"
            )
        ).scalar() or 0
        
        return {
            "total_revenue": round(float(total_revenue), 2),
            "revenue_by_service": [
                {
                    "service": r.name, 
                    "patient_count": r.patient_count,
                    "estimated_revenue": round(r.patient_count * 50.0, 2)  # Estimate
                }
                for r in revenue_by_service
            ],
            "revenue_trend": [
                {
                    "date": str(r.date), 
                    "revenue": round(float(r.revenue or 0), 2),
                    "appointments": r.appointments
                }
                for r in revenue_trend
            ],
            "status_breakdown": [
                {
                    "status": r.status,
                    "count": r.count,
                    "total_fees": round(float(r.total_fees or 0), 2)
                }
                for r in status_breakdown
            ],
            "outstanding_revenue": round(float(outstanding), 2),
            "period_days": period_days
        }
