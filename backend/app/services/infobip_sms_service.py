import httpx
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)

class InfobipSMSService:
    def __init__(self):
        self.api_key = "d92f154c87f06c75b3ada86050dbfb51-56183188-d210-4428-afed-c001ad8ec63b"
        self.base_url = "https://nmnwd8.api.infobip.com"
        self.from_number = "447491163443"  # Default sender number
        self.headers = {
            'Authorization': f'App {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    async def send_sms(self, to: str, message: str, from_number: Optional[str] = None) -> Dict[str, Any]:
        """Send a single SMS message"""
        try:
            payload = {
                "messages": [
                    {
                        "destinations": [{"to": to}],
                        "from": from_number or self.from_number,
                        "text": message
                    }
                ]
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/sms/2/text/advanced",
                    headers=self.headers,
                    json=payload
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"SMS sent successfully to {to}")
                    return {
                        "success": True,
                        "message_id": result.get("messages", [{}])[0].get("messageId"),
                        "status": result.get("messages", [{}])[0].get("status"),
                        "to": to
                    }
                else:
                    error_data = response.json()
                    logger.error(f"SMS send failed: {error_data}")
                    return {
                        "success": False,
                        "error": error_data.get("requestError", {}).get("serviceException", {}).get("text", "Unknown error"),
                        "status_code": response.status_code
                    }

        except Exception as e:
            logger.error(f"Error sending SMS to {to}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def send_bulk_sms(self, messages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Send multiple SMS messages"""
        results = []

        # Process in batches to avoid rate limits
        batch_size = 10
        for i in range(0, len(messages), batch_size):
            batch = messages[i:i + batch_size]

            # Send batch concurrently
            tasks = []
            for msg in batch:
                task = self.send_sms(msg["to"], msg["text"], msg.get("from"))
                tasks.append(task)

            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in batch_results:
                if isinstance(result, Exception):
                    results.append({
                        "success": False,
                        "error": str(result)
                    })
                else:
                    results.append(result)

            # Small delay between batches
            if i + batch_size < len(messages):
                await asyncio.sleep(0.5)

        return results

    async def send_emergency_eta_notification(
        self,
        patient_phone: str,
        eta_minutes: int,
        ambulance_id: str,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send emergency ETA notification"""
        try:
            message = f"🚨 EMERGENCY RESPONSE: Ambulance {ambulance_id} will arrive in approximately {eta_minutes} minutes."

            if location:
                message += f" Current location: {location}"

            message += " Stay calm and follow first aid instructions if provided."

            return await self.send_sms(patient_phone, message)

        except Exception as e:
            logger.error(f"Error sending emergency ETA notification: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def send_queue_update_notification(
        self,
        patient_phone: str,
        queue_number: str,
        position: int,
        estimated_wait: int,
        department: str
    ) -> Dict[str, Any]:
        """Send queue position update"""
        try:
            message = f"🏥 QUEUE UPDATE: Your queue number {queue_number} in {department}. "
            message += f"Current position: {position}. Estimated wait: {estimated_wait} minutes."

            return await self.send_sms(patient_phone, message)

        except Exception as e:
            logger.error(f"Error sending queue update notification: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def send_appointment_reminder(
        self,
        patient_phone: str,
        appointment_time: str,
        department: str,
        doctor_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send appointment reminder"""
        try:
            message = f"📅 APPOINTMENT REMINDER: You have an appointment on {appointment_time}"

            if doctor_name:
                message += f" with Dr. {doctor_name}"

            message += f" in {department}. Please arrive 15 minutes early."

            return await self.send_sms(patient_phone, message)

        except Exception as e:
            logger.error(f"Error sending appointment reminder: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def send_emergency_dispatch_alert(
        self,
        responders: List[str],
        emergency_location: str,
        emergency_type: str,
        priority: str = "HIGH"
    ) -> List[Dict[str, Any]]:
        """Send emergency dispatch alerts to responders"""
        try:
            message = f"🚨 {priority} PRIORITY EMERGENCY DISPATCH\n"
            message += f"Type: {emergency_type}\n"
            message += f"Location: {emergency_location}\n"
            message += f"Time: {datetime.now().strftime('%H:%M:%S')}\n"
            message += "Respond immediately!"

            messages = [
                {"to": phone, "text": message}
                for phone in responders
            ]

            return await self.send_bulk_sms(messages)

        except Exception as e:
            logger.error(f"Error sending emergency dispatch alerts: {e}")
            return [{
                "success": False,
                "error": str(e)
            }]

    async def check_delivery_status(self, message_id: str) -> Dict[str, Any]:
        """Check delivery status of a message"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/sms/1/reports",
                    headers=self.headers,
                    params={"messageId": message_id}
                )

                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "status": result.get("results", [{}])[0].get("status"),
                        "delivered_at": result.get("results", [{}])[0].get("doneAt")
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Status check failed: {response.status_code}"
                    }

        except Exception as e:
            logger.error(f"Error checking delivery status: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_account_balance(self) -> Dict[str, Any]:
        """Get account balance and SMS credits"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/account/1/balance",
                    headers=self.headers
                )

                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "balance": result.get("balance"),
                        "currency": result.get("currency")
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Balance check failed: {response.status_code}"
                    }

        except Exception as e:
            logger.error(f"Error getting account balance: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Global instance
infobip_sms_service = InfobipSMSService()