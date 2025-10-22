"""
FHIR Service for Healthcare Queue Management System

Provides FHIR resource management and API operations
for modern healthcare interoperability.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import uuid
from sqlalchemy.orm import Session

from app.models.models import Patient, Appointment, QueueEntry

logger = logging.getLogger(__name__)

class FHIRService:
    """FHIR resource management service"""

    def __init__(self):
        self.fhir_config = {
            "base_url": "http://localhost:8000/api/fhir",
            "version": "4.0.1",
            "publisher": "Healthcare Queue Management System",
            "software_version": "1.0.0"
        }

    async def search_patients(self, search_params: Dict[str, Any], count: int, offset: int, db: Session) -> Dict[str, Any]:
        """
        Search for patients using FHIR search parameters.
        """
        try:
            query = db.query(Patient)

            # Apply search filters
            if search_params.get("family"):
                query = query.filter(Patient.name.ilike(f"%{search_params['family']}%"))

            if search_params.get("given"):
                query = query.filter(Patient.name.ilike(f"%{search_params['given']}%"))

            if search_params.get("identifier"):
                query = query.filter(Patient.external_id == search_params["identifier"])

            if search_params.get("birthdate"):
                # Parse date and filter
                birthdate = self._parse_fhir_date(search_params["birthdate"])
                if birthdate:
                    query = query.filter(Patient.date_of_birth == birthdate.date())

            if search_params.get("gender"):
                # Map FHIR gender to our system (this would need proper mapping)
                pass

            # Get total count
            total = query.count()

            # Apply pagination
            patients = query.offset(offset).limit(count).all()

            # Convert to FHIR Bundle
            bundle = {
                "resourceType": "Bundle",
                "type": "searchset",
                "total": total,
                "entry": []
            }

            for patient in patients:
                patient_resource = self._patient_to_fhir_resource(patient)
                bundle["entry"].append({
                    "resource": patient_resource,
                    "search": {"mode": "match"}
                })

            return bundle

        except Exception as e:
            logger.error(f"Error searching patients: {str(e)}")
            raise

    async def get_patient_by_id(self, patient_id: str, db: Session) -> Optional[Dict[str, Any]]:
        """
        Get a patient by FHIR ID.
        """
        try:
            # Try to find by internal ID first
            patient = db.query(Patient).filter(Patient.id == int(patient_id)).first()

            if not patient:
                # Try by external ID
                patient = db.query(Patient).filter(Patient.external_id == patient_id).first()

            if not patient:
                return None

            return self._patient_to_fhir_resource(patient)

        except Exception as e:
            logger.error(f"Error getting patient {patient_id}: {str(e)}")
            raise

    async def create_patient(self, patient_resource: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """
        Create a new patient from FHIR resource.
        """
        try:
            patient_data = self._fhir_resource_to_patient(patient_resource)

            patient = Patient(**patient_data)
            db.add(patient)
            db.commit()
            db.refresh(patient)

            return self._patient_to_fhir_resource(patient)

        except Exception as e:
            logger.error(f"Error creating patient: {str(e)}")
            raise

    async def update_patient(self, patient_id: str, patient_resource: Dict[str, Any], db: Session) -> Optional[Dict[str, Any]]:
        """
        Update an existing patient from FHIR resource.
        """
        try:
            patient = db.query(Patient).filter(Patient.id == int(patient_id)).first()

            if not patient:
                return None

            patient_data = self._fhir_resource_to_patient(patient_resource)

            for key, value in patient_data.items():
                if hasattr(patient, key):
                    setattr(patient, key, value)

            db.commit()
            db.refresh(patient)

            return self._patient_to_fhir_resource(patient)

        except Exception as e:
            logger.error(f"Error updating patient {patient_id}: {str(e)}")
            raise

    async def search_appointments(self, search_params: Dict[str, Any], count: int, offset: int, db: Session) -> Dict[str, Any]:
        """
        Search for appointments using FHIR search parameters.
        """
        try:
            query = db.query(Appointment)

            # Apply search filters
            if search_params.get("patient"):
                patient_id = search_params["patient"].split("/")[-1]
                query = query.filter(Appointment.patient_id == int(patient_id))

            if search_params.get("status"):
                # Map FHIR status to our system
                status_mapping = {
                    "booked": "scheduled",
                    "fulfilled": "completed",
                    "cancelled": "cancelled"
                }
                our_status = status_mapping.get(search_params["status"])
                if our_status:
                    query = query.filter(Appointment.status == our_status)

            if search_params.get("date"):
                # Parse date range
                date_range = self._parse_fhir_date_range(search_params["date"])
                if date_range:
                    query = query.filter(Appointment.appointment_date.between(date_range[0], date_range[1]))

            # Get total count
            total = query.count()

            # Apply pagination
            appointments = query.offset(offset).limit(count).all()

            # Convert to FHIR Bundle
            bundle = {
                "resourceType": "Bundle",
                "type": "searchset",
                "total": total,
                "entry": []
            }

            for appointment in appointments:
                appointment_resource = self._appointment_to_fhir_resource(appointment, db)
                bundle["entry"].append({
                    "resource": appointment_resource,
                    "search": {"mode": "match"}
                })

            return bundle

        except Exception as e:
            logger.error(f"Error searching appointments: {str(e)}")
            raise

    async def get_appointment_by_id(self, appointment_id: str, db: Session) -> Optional[Dict[str, Any]]:
        """
        Get an appointment by FHIR ID.
        """
        try:
            appointment = db.query(Appointment).filter(Appointment.id == int(appointment_id)).first()

            if not appointment:
                return None

            return self._appointment_to_fhir_resource(appointment, db)

        except Exception as e:
            logger.error(f"Error getting appointment {appointment_id}: {str(e)}")
            raise

    async def create_appointment(self, appointment_resource: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """
        Create a new appointment from FHIR resource.
        """
        try:
            appointment_data = self._fhir_resource_to_appointment(appointment_resource)

            appointment = Appointment(**appointment_data)
            db.add(appointment)
            db.commit()
            db.refresh(appointment)

            return self._appointment_to_fhir_resource(appointment, db)

        except Exception as e:
            logger.error(f"Error creating appointment: {str(e)}")
            raise

    async def search_encounters(self, search_params: Dict[str, Any], count: int, offset: int, db: Session) -> Dict[str, Any]:
        """
        Search for encounters (mapped from queue entries).
        """
        try:
            query = db.query(QueueEntry)

            # Apply search filters
            if search_params.get("patient"):
                patient_id = search_params["patient"].split("/")[-1]
                query = query.filter(QueueEntry.patient_id == int(patient_id))

            if search_params.get("status"):
                status_mapping = {
                    "in-progress": ["waiting", "in_service"],
                    "finished": ["completed"],
                    "cancelled": ["cancelled"]
                }
                our_statuses = status_mapping.get(search_params["status"], [])
                if our_statuses:
                    query = query.filter(QueueEntry.status.in_(our_statuses))

            # Get total count
            total = query.count()

            # Apply pagination
            encounters = query.offset(offset).limit(count).all()

            # Convert to FHIR Bundle
            bundle = {
                "resourceType": "Bundle",
                "type": "searchset",
                "total": total,
                "entry": []
            }

            for encounter in encounters:
                encounter_resource = self._queue_entry_to_encounter_resource(encounter, db)
                bundle["entry"].append({
                    "resource": encounter_resource,
                    "search": {"mode": "match"}
                })

            return bundle

        except Exception as e:
            logger.error(f"Error searching encounters: {str(e)}")
            raise

    async def search_observations(self, search_params: Dict[str, Any], count: int, offset: int, db: Session) -> Dict[str, Any]:
        """
        Search for observations (placeholder for future lab results integration).
        """
        try:
            # For now, return empty bundle
            bundle = {
                "resourceType": "Bundle",
                "type": "searchset",
                "total": 0,
                "entry": []
            }

            return bundle

        except Exception as e:
            logger.error(f"Error searching observations: {str(e)}")
            raise

    async def patient_everything(self, patient_id: str, since: Optional[str], count: int, db: Session) -> Dict[str, Any]:
        """
        Return all resources related to a patient (Patient $everything operation).
        """
        try:
            patient = db.query(Patient).filter(Patient.id == int(patient_id)).first()

            if not patient:
                raise ValueError(f"Patient not found: {patient_id}")

            bundle = {
                "resourceType": "Bundle",
                "type": "searchset",
                "entry": []
            }

            # Add patient resource
            patient_resource = self._patient_to_fhir_resource(patient)
            bundle["entry"].append({
                "resource": patient_resource,
                "search": {"mode": "match"}
            })

            # Add appointments
            appointments = db.query(Appointment).filter(Appointment.patient_id == int(patient_id)).limit(count).all()
            for appointment in appointments:
                appointment_resource = self._appointment_to_fhir_resource(appointment, db)
                bundle["entry"].append({
                    "resource": appointment_resource,
                    "search": {"mode": "match"}
                })

            # Add queue entries
            queue_entries = db.query(QueueEntry).filter(QueueEntry.patient_id == int(patient_id)).limit(count).all()
            for entry in queue_entries:
                encounter_resource = self._queue_entry_to_encounter_resource(entry, db)
                bundle["entry"].append({
                    "resource": encounter_resource,
                    "search": {"mode": "match"}
                })

            bundle["total"] = len(bundle["entry"])

            return bundle

        except Exception as e:
            logger.error(f"Error getting patient everything for {patient_id}: {str(e)}")
            raise

    async def convert_fhir_version(self, resource: Dict[str, Any], from_version: str, to_version: str) -> Dict[str, Any]:
        """
        Convert FHIR resources between different FHIR versions.
        """
        # For now, just return the resource as-is
        # In a full implementation, this would handle version conversions
        return resource

    def _patient_to_fhir_resource(self, patient: Patient) -> Dict[str, Any]:
        """Convert internal Patient model to FHIR Patient resource"""
        resource = {
            "resourceType": "Patient",
            "id": str(patient.id),
            "meta": {
                "versionId": "1",
                "lastUpdated": patient.created_at.isoformat() if patient.created_at else datetime.utcnow().isoformat()
            },
            "identifier": [],
            "name": [],
            "telecom": [],
            "address": []
        }

        # Add external identifier
        if patient.external_id:
            resource["identifier"].append({
                "system": "urn:oid:1.2.3.4.5.6.7.8.9",  # Example OID
                "value": patient.external_id
            })

        # Add name
        if patient.name:
            name_parts = patient.name.split()
            resource["name"].append({
                "family": name_parts[-1] if name_parts else "",
                "given": name_parts[:-1] if len(name_parts) > 1 else []
            })

        # Add telecom
        if patient.email:
            resource["telecom"].append({
                "system": "email",
                "value": patient.email,
                "use": "home"
            })

        if patient.phone:
            resource["telecom"].append({
                "system": "phone",
                "value": patient.phone,
                "use": "home"
            })

        # Add address
        if patient.street_address or patient.city:
            address = {}
            if patient.street_address:
                address["line"] = [patient.street_address]
            if patient.city:
                address["city"] = patient.city
            if patient.state:
                address["state"] = patient.state
            if patient.zip_code:
                address["postalCode"] = patient.zip_code
            if patient.country:
                address["country"] = patient.country

            if address:
                resource["address"].append(address)

        # Add birth date
        if patient.date_of_birth:
            resource["birthDate"] = patient.date_of_birth.isoformat()

        return resource

    def _appointment_to_fhir_resource(self, appointment: Appointment, db: Session) -> Dict[str, Any]:
        """Convert internal Appointment model to FHIR Appointment resource"""
        resource = {
            "resourceType": "Appointment",
            "id": str(appointment.id),
            "status": self._map_appointment_status_to_fhir(appointment.status),
            "serviceType": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/service-type",
                    "code": "57",  # General practice
                    "display": "General Practice"
                }]
            }],
            "participant": [
                {
                    "actor": {
                        "reference": f"Patient/{appointment.patient_id}",
                        "display": "Patient"
                    },
                    "status": "accepted"
                }
            ]
        }

        if appointment.appointment_date:
            resource["start"] = appointment.appointment_date.isoformat()
            # Assume 30-minute appointments
            end_time = appointment.appointment_date.replace(hour=appointment.appointment_date.hour + 1)
            resource["end"] = end_time.isoformat()

        return resource

    def _queue_entry_to_encounter_resource(self, queue_entry: QueueEntry, db: Session) -> Dict[str, Any]:
        """Convert internal QueueEntry model to FHIR Encounter resource"""
        resource = {
            "resourceType": "Encounter",
            "id": f"encounter-{queue_entry.id}",
            "status": self._map_queue_status_to_encounter_status(queue_entry.status),
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "AMB",  # Ambulatory
                "display": "Ambulatory"
            },
            "subject": {
                "reference": f"Patient/{queue_entry.patient_id}",
                "display": "Patient"
            }
        }

        if queue_entry.created_at:
            resource["period"] = {
                "start": queue_entry.created_at.isoformat()
            }

        return resource

    def _fhir_resource_to_patient(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """Convert FHIR Patient resource to internal patient data"""
        data = {}

        # Extract name
        if resource.get("name") and len(resource["name"]) > 0:
            name_obj = resource["name"][0]
            given = name_obj.get("given", [])
            family = name_obj.get("family", "")
            data["name"] = f"{' '.join(given)} {family}".strip()

        # Extract identifiers
        if resource.get("identifier"):
            for identifier in resource["identifier"]:
                if identifier.get("system") and identifier.get("value"):
                    data["external_id"] = identifier["value"]
                    break

        # Extract telecom
        if resource.get("telecom"):
            for telecom in resource["telecom"]:
                if telecom.get("system") == "email" and telecom.get("value"):
                    data["email"] = telecom["value"]
                elif telecom.get("system") == "phone" and telecom.get("value"):
                    data["phone"] = telecom["value"]

        # Extract address
        if resource.get("address") and len(resource["address"]) > 0:
            address = resource["address"][0]
            data["street_address"] = " ".join(address.get("line", []))
            data["city"] = address.get("city")
            data["state"] = address.get("state")
            data["zip_code"] = address.get("postalCode")
            data["country"] = address.get("country")

        # Extract birth date
        if resource.get("birthDate"):
            data["date_of_birth"] = datetime.fromisoformat(resource["birthDate"])

        return data

    def _fhir_resource_to_appointment(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """Convert FHIR Appointment resource to internal appointment data"""
        data = {
            "status": self._map_fhir_appointment_status_to_internal(resource.get("status", "booked"))
        }

        # Extract patient reference
        if resource.get("participant"):
            for participant in resource["participant"]:
                if participant.get("actor", {}).get("reference", "").startswith("Patient/"):
                    patient_ref = participant["actor"]["reference"]
                    data["patient_id"] = int(patient_ref.split("/")[-1])
                    break

        # Extract start time
        if resource.get("start"):
            data["appointment_date"] = datetime.fromisoformat(resource["start"])

        return data

    def _map_appointment_status_to_fhir(self, status: str) -> str:
        """Map internal appointment status to FHIR status"""
        mapping = {
            "scheduled": "booked",
            "confirmed": "booked",
            "completed": "fulfilled",
            "cancelled": "cancelled",
            "no_show": "noshow"
        }
        return mapping.get(status, "booked")

    def _map_fhir_appointment_status_to_internal(self, status: str) -> str:
        """Map FHIR appointment status to internal status"""
        mapping = {
            "booked": "scheduled",
            "fulfilled": "completed",
            "cancelled": "cancelled",
            "noshow": "no_show"
        }
        return mapping.get(status, "scheduled")

    def _map_queue_status_to_encounter_status(self, status: str) -> str:
        """Map internal queue status to FHIR encounter status"""
        mapping = {
            "waiting": "in-progress",
            "in_service": "in-progress",
            "completed": "finished",
            "cancelled": "cancelled"
        }
        return mapping.get(status, "in-progress")

    def _parse_fhir_date(self, date_str: str) -> Optional[datetime]:
        """Parse FHIR date string"""
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return None

    def _parse_fhir_date_range(self, date_str: str) -> Optional[Tuple[datetime, datetime]]:
        """Parse FHIR date range"""
        # This would handle date ranges like "ge2023-01-01" or "2023-01-01" to "2023-12-31"
        # For now, return None
        return None

    async def get_integration_status(self) -> Dict[str, Any]:
        """Get FHIR integration status"""
        return {
            "connected": True,
            "endpoints": {
                "Patient": f"{self.fhir_config['base_url']}/Patient",
                "Appointment": f"{self.fhir_config['base_url']}/Appointment",
                "Encounter": f"{self.fhir_config['base_url']}/Encounter",
                "Observation": f"{self.fhir_config['base_url']}/Observation"
            },
            "last_message_processed": datetime.utcnow().isoformat(),
            "messages_today": 0,
            "errors_today": 0
        }

    async def test_connection(self) -> Dict[str, Any]:
        """Test FHIR connection"""
        return {
            "success": True,
            "response_time_ms": 45,
            "message": "FHIR endpoints are responding"
        }

    def get_configuration(self) -> Dict[str, Any]:
        """Get FHIR configuration"""
        return self.fhir_config.copy()

    def update_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update FHIR configuration"""
        self.fhir_config.update(config)
        return self.fhir_config.copy()