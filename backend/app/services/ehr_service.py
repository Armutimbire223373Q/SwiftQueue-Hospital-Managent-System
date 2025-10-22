"""
EHR Service for Healthcare Queue Management System

Provides comprehensive integration with Electronic Health Record (EHR) systems
for patient data synchronization, medical record access, and interoperability.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
import aiohttp
from sqlalchemy.orm import Session

from app.models.models import Patient, Appointment, QueueEntry

logger = logging.getLogger(__name__)

class EHRService:
    """EHR integration service"""

    def __init__(self):
        self.ehr_config = {
            "base_url": "https://api.ehr-system.example.com",
            "api_key": None,  # Set via environment variables
            "timeout": 30,
            "retry_attempts": 3,
            "connected_systems": [
                {
                    "id": "epic",
                    "name": "Epic Systems",
                    "status": "disconnected",
                    "last_sync": None
                },
                {
                    "id": "cerner",
                    "name": "Cerner Corporation",
                    "status": "disconnected",
                    "last_sync": None
                },
                {
                    "id": "meditech",
                    "name": "MEDITECH",
                    "status": "disconnected",
                    "last_sync": None
                }
            ]
        }

    async def sync_patient_data(self, patient_id: int, db: Session):
        """
        Synchronize patient data with EHR systems.
        """
        try:
            logger.info(f"Starting patient data sync for patient {patient_id}")

            # Get patient from our database
            patient = db.query(Patient).filter(Patient.id == patient_id).first()
            if not patient:
                logger.error(f"Patient {patient_id} not found in local database")
                return

            # Sync with each connected EHR system
            for system in self.ehr_config["connected_systems"]:
                if system["status"] == "connected":
                    try:
                        await self._sync_patient_with_system(patient, system, db)
                        system["last_sync"] = datetime.utcnow().isoformat()
                        logger.info(f"Successfully synced patient {patient_id} with {system['name']}")
                    except Exception as e:
                        logger.error(f"Failed to sync patient {patient_id} with {system['name']}: {str(e)}")

            # Log sync completion
            await self._log_sync_operation(patient_id, "patient_sync", "completed", db)

        except Exception as e:
            logger.error(f"Error syncing patient data for {patient_id}: {str(e)}")
            await self._log_sync_operation(patient_id, "patient_sync", "error", db, str(e))

    async def sync_appointment_data(self, appointment_id: int, db: Session):
        """
        Synchronize appointment data with EHR systems.
        """
        try:
            logger.info(f"Starting appointment data sync for appointment {appointment_id}")

            appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
            if not appointment:
                logger.error(f"Appointment {appointment_id} not found")
                return

            # Sync with connected systems
            for system in self.ehr_config["connected_systems"]:
                if system["status"] == "connected":
                    try:
                        await self._sync_appointment_with_system(appointment, system, db)
                        logger.info(f"Successfully synced appointment {appointment_id} with {system['name']}")
                    except Exception as e:
                        logger.error(f"Failed to sync appointment {appointment_id} with {system['name']}: {str(e)}")

            await self._log_sync_operation(appointment_id, "appointment_sync", "completed", db)

        except Exception as e:
            logger.error(f"Error syncing appointment data for {appointment_id}: {str(e)}")
            await self._log_sync_operation(appointment_id, "appointment_sync", "error", db, str(e))

    async def get_patient_medical_record(self, patient_id: int, include_history: bool = True,
                                       include_medications: bool = True, include_allergies: bool = True,
                                       db: Session = None) -> Dict[str, Any]:
        """
        Retrieve comprehensive medical record from EHR systems.
        """
        try:
            medical_record = {
                "patient_id": patient_id,
                "demographics": {},
                "medical_history": [],
                "current_medications": [],
                "allergies": [],
                "recent_encounters": [],
                "vital_signs": [],
                "lab_results": [],
                "retrieved_at": datetime.utcnow().isoformat(),
                "sources": []
            }

            # Get patient demographics from local database
            if db:
                patient = db.query(Patient).filter(Patient.id == patient_id).first()
                if patient:
                    medical_record["demographics"] = {
                        "name": patient.name,
                        "date_of_birth": patient.date_of_birth.isoformat() if patient.date_of_birth else None,
                        "gender": getattr(patient, 'gender', None),
                        "address": {
                            "street": patient.street_address,
                            "city": patient.city,
                            "state": patient.state,
                            "zip_code": patient.zip_code,
                            "country": patient.country
                        },
                        "phone": patient.phone,
                        "email": patient.email
                    }

            # Fetch from connected EHR systems
            for system in self.ehr_config["connected_systems"]:
                if system["status"] == "connected":
                    try:
                        system_record = await self._get_medical_record_from_system(
                            patient_id, system, include_history, include_medications, include_allergies
                        )

                        # Merge records
                        if include_history and system_record.get("medical_history"):
                            medical_record["medical_history"].extend(system_record["medical_history"])

                        if include_medications and system_record.get("current_medications"):
                            medical_record["current_medications"].extend(system_record["current_medications"])

                        if include_allergies and system_record.get("allergies"):
                            medical_record["allergies"].extend(system_record["allergies"])

                        if system_record.get("recent_encounters"):
                            medical_record["recent_encounters"].extend(system_record["recent_encounters"])

                        if system_record.get("vital_signs"):
                            medical_record["vital_signs"].extend(system_record["vital_signs"])

                        if system_record.get("lab_results"):
                            medical_record["lab_results"].extend(system_record["lab_results"])

                        medical_record["sources"].append(system["name"])

                    except Exception as e:
                        logger.error(f"Failed to get medical record from {system['name']}: {str(e)}")

            return medical_record

        except Exception as e:
            logger.error(f"Error retrieving medical record for patient {patient_id}: {str(e)}")
            raise

    async def update_patient_record(self, patient_id: int, update_data: Dict[str, Any], db: Session):
        """
        Update patient medical record in EHR systems.
        """
        try:
            logger.info(f"Starting patient record update for patient {patient_id}")

            # Update in connected EHR systems
            for system in self.ehr_config["connected_systems"]:
                if system["status"] == "connected":
                    try:
                        await self._update_patient_record_in_system(patient_id, update_data, system)
                        logger.info(f"Successfully updated patient record in {system['name']}")
                    except Exception as e:
                        logger.error(f"Failed to update patient record in {system['name']}: {str(e)}")

            await self._log_sync_operation(patient_id, "record_update", "completed", db)

        except Exception as e:
            logger.error(f"Error updating patient record for {patient_id}: {str(e)}")
            await self._log_sync_operation(patient_id, "record_update", "error", db, str(e))

    async def bulk_sync_data(self, sync_type: str, db: Session):
        """
        Perform bulk synchronization of data with EHR systems.
        """
        try:
            logger.info(f"Starting bulk sync for type: {sync_type}")

            if sync_type == "patients":
                patients = db.query(Patient).all()
                for patient in patients:
                    await self.sync_patient_data(patient.id, db)

            elif sync_type == "appointments":
                appointments = db.query(Appointment).all()
                for appointment in appointments:
                    await self.sync_appointment_data(appointment.id, db)

            elif sync_type == "all":
                # Sync both patients and appointments
                await self.bulk_sync_data("patients", db)
                await self.bulk_sync_data("appointments", db)

            logger.info(f"Bulk sync completed for type: {sync_type}")

        except Exception as e:
            logger.error(f"Error in bulk sync for {sync_type}: {str(e)}")
            raise

    async def get_sync_status(self, patient_id: Optional[int] = None, limit: int = 50,
                            offset: int = 0, db: Session = None) -> List[Dict[str, Any]]:
        """
        Get synchronization status and history.
        """
        # In a real implementation, this would query a sync log table
        # For now, return mock data
        return [
            {
                "id": 1,
                "patient_id": patient_id or 1,
                "operation_type": "patient_sync",
                "status": "completed",
                "started_at": datetime.utcnow().isoformat(),
                "completed_at": datetime.utcnow().isoformat(),
                "system": "Epic Systems"
            }
        ]

    async def get_connected_systems(self) -> List[Dict[str, Any]]:
        """
        Get information about connected EHR systems.
        """
        return self.ehr_config["connected_systems"].copy()

    async def test_connection(self, system_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Test connection to EHR systems.
        """
        systems_to_test = self.ehr_config["connected_systems"]
        if system_id:
            systems_to_test = [s for s in systems_to_test if s["id"] == system_id]

        results = []
        for system in systems_to_test:
            try:
                # Simulate connection test
                success = await self._test_system_connection(system)
                results.append({
                    "system_id": system["id"],
                    "system_name": system["name"],
                    "success": success,
                    "response_time_ms": 150 if success else None,
                    "error": None if success else "Connection timeout"
                })
            except Exception as e:
                results.append({
                    "system_id": system["id"],
                    "system_name": system["name"],
                    "success": False,
                    "response_time_ms": None,
                    "error": str(e)
                })

        return results

    def get_configuration(self) -> Dict[str, Any]:
        """Get EHR configuration"""
        return {
            "base_url": self.ehr_config["base_url"],
            "timeout": self.ehr_config["timeout"],
            "retry_attempts": self.ehr_config["retry_attempts"],
            "connected_systems": len([s for s in self.ehr_config["connected_systems"] if s["status"] == "connected"])
        }

    def update_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update EHR configuration"""
        for key, value in config.items():
            if key in self.ehr_config:
                self.ehr_config[key] = value

        return self.get_configuration()

    async def process_webhook(self, system_id: str, webhook_data: Dict[str, Any], db: Session):
        """
        Process webhook from EHR system.
        """
        try:
            logger.info(f"Processing webhook from {system_id}")

            # Process based on webhook type
            webhook_type = webhook_data.get("type", "")

            if webhook_type == "patient_update":
                await self._process_patient_update_webhook(webhook_data, db)
            elif webhook_type == "appointment_update":
                await self._process_appointment_update_webhook(webhook_data, db)
            elif webhook_type == "medical_record_update":
                await self._process_medical_record_update_webhook(webhook_data, db)

            logger.info(f"Successfully processed {webhook_type} webhook from {system_id}")

        except Exception as e:
            logger.error(f"Error processing webhook from {system_id}: {str(e)}")
            raise

    async def get_audit_log(self, start_date: Optional[str] = None, end_date: Optional[str] = None,
                          action_type: Optional[str] = None, limit: int = 100, offset: int = 0,
                          db: Session = None) -> List[Dict[str, Any]]:
        """
        Get audit log for EHR integration activities.
        """
        # In a real implementation, this would query an audit log table
        # For now, return mock data
        return [
            {
                "id": 1,
                "timestamp": datetime.utcnow().isoformat(),
                "action": "patient_sync",
                "patient_id": 1,
                "system": "Epic Systems",
                "status": "success",
                "details": "Patient demographics synchronized"
            }
        ]

    # Private helper methods

    async def _sync_patient_with_system(self, patient: Patient, system: Dict[str, Any], db: Session):
        """Sync patient data with a specific EHR system"""
        # This would make actual API calls to the EHR system
        # For now, simulate the sync
        await asyncio.sleep(0.1)  # Simulate network delay

    async def _sync_appointment_with_system(self, appointment: Appointment, system: Dict[str, Any], db: Session):
        """Sync appointment data with a specific EHR system"""
        await asyncio.sleep(0.1)  # Simulate network delay

    async def _get_medical_record_from_system(self, patient_id: int, system: Dict[str, Any],
                                            include_history: bool, include_medications: bool,
                                            include_allergies: bool) -> Dict[str, Any]:
        """Get medical record from a specific EHR system"""
        # This would make actual API calls to retrieve medical data
        # For now, return mock data
        return {
            "medical_history": [
                {
                    "date": "2023-01-15",
                    "condition": "Hypertension",
                    "status": "Active",
                    "source": system["name"]
                }
            ] if include_history else [],
            "current_medications": [
                {
                    "name": "Lisinopril",
                    "dosage": "10mg",
                    "frequency": "Once daily",
                    "source": system["name"]
                }
            ] if include_medications else [],
            "allergies": [
                {
                    "allergen": "Penicillin",
                    "reaction": "Rash",
                    "severity": "Moderate",
                    "source": system["name"]
                }
            ] if include_allergies else [],
            "recent_encounters": [],
            "vital_signs": [],
            "lab_results": []
        }

    async def _update_patient_record_in_system(self, patient_id: int, update_data: Dict[str, Any],
                                             system: Dict[str, Any]):
        """Update patient record in a specific EHR system"""
        await asyncio.sleep(0.1)  # Simulate network delay

    async def _test_system_connection(self, system: Dict[str, Any]) -> bool:
        """Test connection to a specific EHR system"""
        await asyncio.sleep(0.1)  # Simulate network delay
        return True  # Simulate successful connection

    async def _process_patient_update_webhook(self, webhook_data: Dict[str, Any], db: Session):
        """Process patient update webhook"""
        patient_data = webhook_data.get("patient", {})
        patient_id = patient_data.get("id")

        if patient_id:
            # Update local patient data
            patient = db.query(Patient).filter(Patient.external_id == str(patient_id)).first()
            if patient:
                # Update patient fields from webhook data
                pass  # Implementation would update patient fields

    async def _process_appointment_update_webhook(self, webhook_data: Dict[str, Any], db: Session):
        """Process appointment update webhook"""
        appointment_data = webhook_data.get("appointment", {})
        # Process appointment updates
        pass

    async def _process_medical_record_update_webhook(self, webhook_data: Dict[str, Any], db: Session):
        """Process medical record update webhook"""
        # Process medical record updates
        pass

    async def _log_sync_operation(self, entity_id: int, operation_type: str, status: str,
                                db: Session, error: Optional[str] = None):
        """Log synchronization operation"""
        # In a real implementation, this would insert into a sync log table
        logger.info(f"Sync operation {operation_type} for entity {entity_id}: {status}")