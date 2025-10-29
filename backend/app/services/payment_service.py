"""
Payment Service - Handles payment processing, billing, and transactions
"""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid
import random
from decimal import Decimal

from app.models.models import User
from app.database import get_db


class PaymentService:
    """Service for managing payments and transactions"""
    
    @staticmethod
    def create_payment(
        db: Session,
        user_id: int,
        amount: float,
        payment_method: str,
        description: str = None,
        appointment_id: int = None,
        service_id: int = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a new payment transaction"""
        
        payment_id = f"pay_{uuid.uuid4().hex[:12]}"
        transaction_id = f"txn_{uuid.uuid4().hex[:16]}"
        
        # Validate payment method
        valid_methods = ['credit_card', 'debit_card', 'mobile_money', 'ecocash', 
                        'innbucks', 'onemoney', 'medical_aid', 'insurance', 'cash']
        
        if payment_method not in valid_methods:
            raise ValueError(f"Invalid payment method. Must be one of: {', '.join(valid_methods)}")
        
        # Create payment record (in production, this would go to database)
        payment = {
            "payment_id": payment_id,
            "transaction_id": transaction_id,
            "user_id": user_id,
            "amount": Decimal(str(amount)),
            "currency": "USD",
            "payment_method": payment_method,
            "status": "pending",
            "description": description or "Hospital service payment",
            "appointment_id": appointment_id,
            "service_id": service_id,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "provider_url": None,
            "provider_reference": None
        }
        
        # Generate provider-specific URLs for redirects
        if payment_method in ['ecocash', 'innbucks', 'onemoney']:
            payment["provider_url"] = f"https://mobile-payment.example.com/{payment_method}/{payment_id}"
        elif payment_method in ['credit_card', 'debit_card']:
            payment["provider_url"] = f"https://card-gateway.example.com/checkout/{payment_id}"
        
        return payment
    
    @staticmethod
    def process_payment(
        db: Session,
        payment_id: str,
        provider_reference: str = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process a payment (simulate payment gateway response)"""
        
        # Simulate payment processing (80% success rate)
        success = random.random() > 0.2
        
        result = {
            "payment_id": payment_id,
            "status": "succeeded" if success else "failed",
            "provider_reference": provider_reference or f"ref_{uuid.uuid4().hex[:10]}",
            "processed_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        if success:
            result["receipt_number"] = f"RCP-{uuid.uuid4().hex[:8].upper()}"
            result["message"] = "Payment processed successfully"
        else:
            result["receipt_number"] = None
            result["error"] = "PAYMENT_DECLINED"
            result["message"] = "Payment was declined by the provider"
        
        return result
    
    @staticmethod
    def get_payment(db: Session, payment_id: str) -> Dict[str, Any]:
        """Get payment details by ID"""
        
        # In production, fetch from database
        # For now, return mock data
        return {
            "payment_id": payment_id,
            "transaction_id": f"txn_{uuid.uuid4().hex[:16]}",
            "amount": Decimal("50.00"),
            "currency": "USD",
            "status": "succeeded",
            "payment_method": "credit_card",
            "created_at": datetime.utcnow().isoformat(),
            "receipt_number": f"RCP-{uuid.uuid4().hex[:8].upper()}"
        }
    
    @staticmethod
    def get_user_payments(
        db: Session,
        user_id: int,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get all payments for a user"""
        
        # In production, query database with filters
        # Mock data for demonstration
        statuses = ['succeeded', 'pending', 'failed'] if not status else [status]
        
        payments = []
        for i in range(min(10, limit)):  # Return up to 10 mock payments
            payments.append({
                "payment_id": f"pay_{uuid.uuid4().hex[:12]}",
                "transaction_id": f"txn_{uuid.uuid4().hex[:16]}",
                "user_id": user_id,
                "amount": Decimal(str(round(random.uniform(20.0, 200.0), 2))),
                "currency": "USD",
                "payment_method": random.choice(['credit_card', 'mobile_money', 'cash']),
                "status": random.choice(statuses),
                "description": f"Payment for service #{i+1}",
                "created_at": datetime.utcnow().isoformat(),
                "receipt_number": f"RCP-{uuid.uuid4().hex[:8].upper()}" if random.choice(statuses) == 'succeeded' else None
            })
        
        return payments
    
    @staticmethod
    def refund_payment(
        db: Session,
        payment_id: str,
        amount: Optional[float] = None,
        reason: str = None
    ) -> Dict[str, Any]:
        """Refund a payment (full or partial)"""
        
        refund_id = f"ref_{uuid.uuid4().hex[:12]}"
        
        # In production, we'd fetch original payment amount from database
        # For now, if amount is specified, it's partial; otherwise full
        if amount is not None:
            refund_amount = Decimal(str(amount))
            refund_type = "partial"
        else:
            refund_amount = Decimal("50.00")  # Default full refund amount
            refund_type = "full"
        
        # In production, verify payment exists and is refundable
        refund = {
            "refund_id": refund_id,
            "payment_id": payment_id,
            "amount": refund_amount,
            "type": refund_type,
            "currency": "USD",
            "status": "refunded",
            "reason": reason or "Customer requested refund",
            "created_at": datetime.utcnow().isoformat(),
            "expected_arrival": "5-10 business days"
        }
        
        return refund
    
    @staticmethod
    def verify_medical_aid(
        db: Session,
        membership_number: str,
        provider: str = None
    ) -> Dict[str, Any]:
        """Verify medical aid/insurance membership"""
        
        # Simulate verification (membership numbers starting with 'A' or 'M' are valid)
        first_char = membership_number.upper()[0] if membership_number else ''
        valid = first_char in ['A', 'M']
        
        result = {
            "membership_number": membership_number,
            "valid": valid,
            "provider": provider or "DemoCare Medical Aid",
            "verified_at": datetime.utcnow().isoformat()
        }
        
        if valid:
            result["plan"] = "Platinum" if first_char == 'A' else "Gold"
            result["coverage_level"] = "full" if first_char == 'A' else "partial"
            result["copay_required"] = False if first_char == 'A' else True
            result["copay_percentage"] = 0 if first_char == 'A' else 20
        else:
            result["plan"] = None
            result["error"] = "Invalid membership number or expired membership"
        
        return result
    
    @staticmethod
    def calculate_billing(
        db: Session,
        service_id: int = None,
        appointment_id: int = None,
        items: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Calculate total billing for services"""
        
        # Mock pricing calculation
        subtotal = Decimal("0.00")
        line_items = items or []
        
        if not line_items:
            # Return empty billing when no items provided
            return {
                "subtotal": Decimal("0.00"),
                "tax_rate": Decimal("0.15"),
                "tax_amount": Decimal("0.00"),
                "total": Decimal("0.00"),
                "currency": "USD",
                "line_items": [],
                "calculated_at": datetime.utcnow().isoformat()
            }
        
        for item in line_items:
            item_amount = Decimal(str(item.get('amount', 0)))
            item_quantity = item.get('quantity', 1)
            item_total = item_amount * Decimal(str(item_quantity))
            subtotal += item_total
        
        tax_rate = Decimal("0.15")  # 15% tax
        tax_amount = (subtotal * tax_rate).quantize(Decimal("0.01"))
        total = (subtotal + tax_amount).quantize(Decimal("0.01"))
        
        return {
            "subtotal": subtotal,
            "tax_rate": tax_rate,
            "tax_amount": tax_amount,
            "total": total,
            "currency": "USD",
            "line_items": line_items,
            "calculated_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def get_payment_methods(db: Session, user_id: int = None) -> List[Dict[str, Any]]:
        """Get available payment methods"""
        
        methods = [
            {
                "method": "credit_card",
                "name": "Credit Card",
                "type": "card",
                "enabled": True,
                "description": "Visa, Mastercard, American Express",
                "fee_percentage": 2.9
            },
            {
                "method": "debit_card",
                "name": "Debit Card",
                "type": "card",
                "enabled": True,
                "description": "Bank debit card",
                "fee_percentage": 1.5
            },
            {
                "method": "ecocash",
                "name": "EcoCash",
                "type": "mobile_money",
                "enabled": True,
                "description": "EcoCash mobile money",
                "fee_percentage": 0.0
            },
            {
                "method": "innbucks",
                "name": "Innbucks",
                "type": "mobile_money",
                "enabled": True,
                "description": "Innbucks mobile wallet",
                "fee_percentage": 0.0
            },
            {
                "method": "onemoney",
                "name": "OneMoney",
                "type": "mobile_money",
                "enabled": True,
                "description": "NetOne OneMoney",
                "fee_percentage": 0.0
            },
            {
                "method": "medical_aid",
                "name": "Medical Aid",
                "type": "insurance",
                "enabled": True,
                "description": "Use your medical aid coverage",
                "fee_percentage": 0.0,
                "requires_verification": True
            },
            {
                "method": "cash",
                "name": "Cash",
                "type": "cash",
                "enabled": True,
                "description": "Pay at reception",
                "fee_percentage": 0.0
            }
        ]
        
        return methods


# Singleton instance
payment_service = PaymentService()
