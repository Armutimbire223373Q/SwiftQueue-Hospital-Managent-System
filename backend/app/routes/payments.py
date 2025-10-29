from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session

from app.database import get_db
from app.routes.auth import get_current_user
from app.services.payment_service import payment_service
from app.models.models import User

router = APIRouter()


# Request Models
class CreatePaymentRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Payment amount (must be positive)")
    payment_method: str = Field(..., description="Payment method: credit_card, debit_card, mobile_money, ecocash, innbucks, onemoney, medical_aid, insurance, cash")
    description: Optional[str] = Field(None, description="Payment description")
    appointment_id: Optional[int] = Field(None, description="Related appointment ID")
    service_id: Optional[int] = Field(None, description="Related service ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional payment metadata")


class ProcessPaymentRequest(BaseModel):
    payment_id: str
    provider_reference: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class RefundRequest(BaseModel):
    payment_id: str
    amount: Optional[float] = Field(None, description="Refund amount (null for full refund)")
    reason: Optional[str] = Field(None, description="Reason for refund")


class MedicalAidVerificationRequest(BaseModel):
    membership_number: str = Field(..., min_length=1)
    provider: Optional[str] = None


class BillingCalculationRequest(BaseModel):
    service_id: Optional[int] = None
    appointment_id: Optional[int] = None
    items: Optional[List[Dict[str, Any]]] = None


# Response Models
class PaymentResponse(BaseModel):
    id: str
    transaction_id: str
    user_id: int
    amount: float
    currency: str
    payment_method: str
    status: str
    description: str
    created_at: str
    provider_url: Optional[str] = None
    receipt_number: Optional[str] = None


# Endpoints
@router.post('/create')
async def create_payment(
    request: CreatePaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new payment transaction
    
    - **amount**: Payment amount (must be positive)
    - **payment_method**: Payment method (credit_card, debit_card, mobile_money, etc.)
    - **description**: Optional payment description
    - **appointment_id**: Optional related appointment
    - **service_id**: Optional related service
    """
    try:
        payment = payment_service.create_payment(
            db=db,
            user_id=current_user.id,
            amount=request.amount,
            payment_method=request.payment_method,
            description=request.description,
            appointment_id=request.appointment_id,
            service_id=request.service_id,
            metadata=request.metadata
        )
        return payment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create payment: {str(e)}")


@router.post('/process')
async def process_payment(
    request: ProcessPaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Process a payment (simulate payment gateway callback)
    
    - **payment_id**: Payment ID to process
    - **provider_reference**: Optional provider reference number
    """
    try:
        result = payment_service.process_payment(
            db=db,
            payment_id=request.payment_id,
            provider_reference=request.provider_reference,
            metadata=request.metadata
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process payment: {str(e)}")


@router.get('/{payment_id}')
async def get_payment(
    payment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get payment details by ID"""
    try:
        payment = payment_service.get_payment(db=db, payment_id=payment_id)
        return payment
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Payment not found: {str(e)}")


@router.get('/history/my-payments')
async def get_my_payments(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get payment history for current user
    
    - **status**: Optional filter by status (succeeded, pending, failed)
    - **limit**: Maximum number of results (default: 50)
    - **offset**: Pagination offset (default: 0)
    """
    try:
        payments = payment_service.get_user_payments(
            db=db,
            user_id=current_user.id,
            status=status,
            limit=limit,
            offset=offset
        )
        return payments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve payments: {str(e)}")


@router.post('/refund')
async def refund_payment(
    request: RefundRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Refund a payment (full or partial)
    
    - **payment_id**: Payment ID to refund
    - **amount**: Optional partial refund amount (null for full refund)
    - **reason**: Optional reason for refund
    """
    try:
        refund = payment_service.refund_payment(
            db=db,
            payment_id=request.payment_id,
            amount=request.amount,
            reason=request.reason
        )
        return refund
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process refund: {str(e)}")


@router.post('/verify-medical-aid')
async def verify_medical_aid(
    request: MedicalAidVerificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Verify medical aid/insurance membership
    
    - **membership_number**: Medical aid membership number
    - **provider**: Optional provider name
    """
    try:
        verification = payment_service.verify_medical_aid(
            db=db,
            membership_number=request.membership_number,
            provider=request.provider
        )
        return verification
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify medical aid: {str(e)}")


@router.post('/calculate-billing')
async def calculate_billing(
    request: BillingCalculationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Calculate total billing for services
    
    - **service_id**: Optional service ID
    - **appointment_id**: Optional appointment ID
    - **items**: Optional list of line items with amount and quantity
    """
    try:
        billing = payment_service.calculate_billing(
            db=db,
            service_id=request.service_id,
            appointment_id=request.appointment_id,
            items=request.items
        )
        return billing
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate billing: {str(e)}")


@router.get('/methods/available')
async def get_payment_methods(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of available payment methods with details"""
    try:
        methods = payment_service.get_payment_methods(db=db, user_id=current_user.id)
        return methods
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve payment methods: {str(e)}")


# Legacy endpoints for backward compatibility
@router.post('/initiate')
async def initiate_payment_legacy(
    request: CreatePaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Legacy endpoint - redirects to /create"""
    return await create_payment(request, db, current_user)


@router.get('/verify/{payment_id}')
async def verify_payment_legacy(
    payment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Legacy endpoint - redirects to /{payment_id}"""
    return await get_payment(payment_id, db, current_user)
