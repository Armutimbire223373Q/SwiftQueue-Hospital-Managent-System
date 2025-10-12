from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict
import random
import time

router = APIRouter()


class PaymentRequest(BaseModel):
    method: str  # 'ecocash' | 'innbucks' | 'omari' | 'medical_aid'
    amount: float
    reference: str = None
    membership_number: str = None


@router.post('/initiate')
def initiate_payment(req: PaymentRequest):
    # Create a mock payment id and pretend we redirected to provider or QR
    payment_id = f"pay_{int(time.time())}_{random.randint(1000,9999)}"
    provider_url = f"https://payments.example/mock/{payment_id}?method={req.method}"
    return { 'payment_id': payment_id, 'provider_url': provider_url, 'status': 'pending' }


@router.get('/verify/{payment_id}')
def verify_payment(payment_id: str):
    # Randomly decide success for mock
    succeeded = random.random() > 0.2
    return { 'payment_id': payment_id, 'status': 'succeeded' if succeeded else 'failed' }


@router.post('/verify-medical-aid')
def verify_medical_aid(data: Dict):
    # Accept membership_number and return mock validation
    membership = data.get('membership_number')
    if not membership:
        raise HTTPException(status_code=400, detail='membership_number required')
    # For demo, membership numbers starting with 'A' are valid
    valid = str(membership).upper().startswith('A')
    return { 'membership_number': membership, 'valid': valid, 'plan_name': 'DemoCare' if valid else None }
