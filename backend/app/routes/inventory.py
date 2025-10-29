"""
Inventory Management API Routes
Handles inventory items, stock movements, suppliers, and purchase orders
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import secrets

from app.database import get_db
from app.models.models import (
    InventoryItem, Supplier, StockMovement, 
    PurchaseOrder, PurchaseOrderItem, User
)
from app.routes.auth import get_current_user

router = APIRouter(prefix="/inventory", tags=["Inventory Management"])


# ==================== Pydantic Models ====================

class InventoryItemCreate(BaseModel):
    item_name: str
    item_code: str
    category: str
    description: Optional[str] = None
    unit_of_measure: str
    minimum_stock: int = 10
    maximum_stock: Optional[int] = None
    reorder_point: int = 20
    unit_cost: Optional[float] = None
    supplier_id: Optional[int] = None
    location: Optional[str] = None
    expiry_date: Optional[datetime] = None
    batch_number: Optional[str] = None


class InventoryItemUpdate(BaseModel):
    item_name: Optional[str] = None
    description: Optional[str] = None
    minimum_stock: Optional[int] = None
    reorder_point: Optional[int] = None
    unit_cost: Optional[float] = None
    is_active: Optional[bool] = None


class StockMovementCreate(BaseModel):
    item_id: int
    movement_type: str  # "in", "out", "adjustment", "expired", "damaged"
    quantity: int
    reference_number: Optional[str] = None
    reason: Optional[str] = None
    notes: Optional[str] = None


class SupplierCreate(BaseModel):
    name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = None


class PurchaseOrderItemCreate(BaseModel):
    item_id: int
    quantity_ordered: int
    unit_price: float


class PurchaseOrderCreate(BaseModel):
    supplier_id: int
    expected_delivery: Optional[datetime] = None
    items: List[PurchaseOrderItemCreate]
    notes: Optional[str] = None


# ==================== Helper Functions ====================

def generate_po_number() -> str:
    """Generate unique purchase order number"""
    timestamp = datetime.utcnow().strftime("%Y%m%d")
    random_suffix = secrets.token_hex(3).upper()
    return f"PO-{timestamp}-{random_suffix}"


def update_stock_level(db: Session, item_id: int, movement_type: str, quantity: int):
    """Update inventory item stock level based on movement"""
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        return
    
    if movement_type == "in":
        item.current_stock += quantity
        item.last_restocked = datetime.utcnow()
    elif movement_type in ["out", "expired", "damaged"]:
        item.current_stock = max(0, item.current_stock - quantity)
    elif movement_type == "adjustment":
        item.current_stock = quantity  # Direct adjustment
    
    db.commit()


# ==================== Inventory Items ====================

@router.post("/items", status_code=status.HTTP_201_CREATED)
async def create_inventory_item(
    item_data: InventoryItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new inventory item (admin/inventory_manager only)"""
    if current_user.role not in ["admin", "inventory_manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    # Check if item code already exists
    existing = db.query(InventoryItem).filter(InventoryItem.item_code == item_data.item_code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Item with code {item_data.item_code} already exists"
        )
    
    item = InventoryItem(**item_data.dict())
    db.add(item)
    db.commit()
    db.refresh(item)
    
    return item


@router.get("/items")
async def list_inventory_items(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    low_stock_only: bool = Query(False),
    active_only: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List inventory items with filters"""
    query = db.query(InventoryItem)
    
    if active_only:
        query = query.filter(InventoryItem.is_active == True)
    
    if category:
        query = query.filter(InventoryItem.category == category)
    
    if search:
        query = query.filter(
            or_(
                InventoryItem.item_name.ilike(f"%{search}%"),
                InventoryItem.item_code.ilike(f"%{search}%"),
                InventoryItem.description.ilike(f"%{search}%")
            )
        )
    
    if low_stock_only:
        query = query.filter(InventoryItem.current_stock <= InventoryItem.minimum_stock)
    
    items = query.offset(skip).limit(limit).all()
    
    return {
        "total": query.count(),
        "items": items
    }


@router.get("/items/{item_id}")
async def get_inventory_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed inventory item information"""
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    # Get recent stock movements
    movements = db.query(StockMovement).filter(
        StockMovement.item_id == item_id
    ).order_by(StockMovement.movement_date.desc()).limit(20).all()
    
    return {
        "item": item,
        "recent_movements": movements,
        "stock_status": "low" if item.current_stock <= item.minimum_stock else "adequate"
    }


@router.put("/items/{item_id}")
async def update_inventory_item(
    item_id: int,
    update_data: InventoryItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update inventory item details"""
    if current_user.role not in ["admin", "inventory_manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    return item


@router.get("/items/low-stock/alerts")
async def get_low_stock_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of items below minimum stock level"""
    low_stock_items = db.query(InventoryItem).filter(
        InventoryItem.current_stock <= InventoryItem.minimum_stock,
        InventoryItem.is_active == True
    ).all()
    
    critical_items = [item for item in low_stock_items if item.current_stock == 0]
    warning_items = [item for item in low_stock_items if item.current_stock > 0]
    
    return {
        "critical_count": len(critical_items),
        "warning_count": len(warning_items),
        "critical_items": critical_items,
        "warning_items": warning_items
    }


@router.get("/items/expiring-soon")
async def get_expiring_items(
    days: int = Query(30, ge=1, le=180),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get items expiring within specified days"""
    expiry_threshold = datetime.utcnow() + timedelta(days=days)
    
    expiring_items = db.query(InventoryItem).filter(
        InventoryItem.expiry_date.isnot(None),
        InventoryItem.expiry_date <= expiry_threshold,
        InventoryItem.is_active == True
    ).all()
    
    return {
        "days": days,
        "expiring_items_count": len(expiring_items),
        "items": expiring_items
    }


# ==================== Stock Movements ====================

@router.post("/stock/movement", status_code=status.HTTP_201_CREATED)
async def record_stock_movement(
    movement_data: StockMovementCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record a stock movement (in/out/adjustment)"""
    if current_user.role not in ["admin", "inventory_manager", "pharmacist"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    # Verify item exists
    item = db.query(InventoryItem).filter(InventoryItem.id == movement_data.item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    # Create movement record
    movement = StockMovement(
        **movement_data.dict(),
        performed_by=current_user.id
    )
    db.add(movement)
    
    # Update stock level
    update_stock_level(db, movement_data.item_id, movement_data.movement_type, movement_data.quantity)
    
    db.commit()
    db.refresh(movement)
    
    return {
        "message": "Stock movement recorded successfully",
        "movement": movement,
        "new_stock_level": item.current_stock
    }


@router.get("/stock/movements")
async def list_stock_movements(
    item_id: Optional[int] = Query(None),
    movement_type: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List stock movements with filters"""
    query = db.query(StockMovement)
    
    if item_id:
        query = query.filter(StockMovement.item_id == item_id)
    
    if movement_type:
        query = query.filter(StockMovement.movement_type == movement_type)
    
    if start_date:
        query = query.filter(StockMovement.movement_date >= start_date)
    
    if end_date:
        query = query.filter(StockMovement.movement_date <= end_date)
    
    movements = query.order_by(StockMovement.movement_date.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": query.count(),
        "movements": movements
    }


# ==================== Suppliers ====================

@router.post("/suppliers", status_code=status.HTTP_201_CREATED)
async def create_supplier(
    supplier_data: SupplierCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new supplier"""
    if current_user.role not in ["admin", "inventory_manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    supplier = Supplier(**supplier_data.dict())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    
    return supplier


@router.get("/suppliers")
async def list_suppliers(
    active_only: bool = Query(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all suppliers"""
    query = db.query(Supplier)
    
    if active_only:
        query = query.filter(Supplier.is_active == True)
    
    return query.all()


@router.get("/suppliers/{supplier_id}")
async def get_supplier(
    supplier_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get supplier details with related items and purchase orders"""
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    items = db.query(InventoryItem).filter(InventoryItem.supplier_id == supplier_id).all()
    purchase_orders = db.query(PurchaseOrder).filter(PurchaseOrder.supplier_id == supplier_id).all()
    
    return {
        "supplier": supplier,
        "items_count": len(items),
        "purchase_orders_count": len(purchase_orders),
        "items": items,
        "recent_purchase_orders": purchase_orders[:10]
    }


# ==================== Purchase Orders ====================

@router.post("/purchase-orders", status_code=status.HTTP_201_CREATED)
async def create_purchase_order(
    po_data: PurchaseOrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new purchase order"""
    if current_user.role not in ["admin", "inventory_manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    # Verify supplier exists
    supplier = db.query(Supplier).filter(Supplier.id == po_data.supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    
    # Calculate totals
    total_amount = sum(item.quantity_ordered * item.unit_price for item in po_data.items)
    
    # Create purchase order
    po = PurchaseOrder(
        po_number=generate_po_number(),
        supplier_id=po_data.supplier_id,
        expected_delivery=po_data.expected_delivery,
        notes=po_data.notes,
        total_amount=total_amount,
        grand_total=total_amount,  # Can add tax/shipping later
        ordered_by=current_user.id
    )
    
    db.add(po)
    db.flush()  # Get PO ID
    
    # Add PO items
    for item_data in po_data.items:
        po_item = PurchaseOrderItem(
            purchase_order_id=po.id,
            item_id=item_data.item_id,
            quantity_ordered=item_data.quantity_ordered,
            unit_price=item_data.unit_price,
            total_price=item_data.quantity_ordered * item_data.unit_price
        )
        db.add(po_item)
    
    db.commit()
    db.refresh(po)
    
    return po


@router.get("/purchase-orders")
async def list_purchase_orders(
    status_filter: Optional[str] = Query(None, alias="status"),
    supplier_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List purchase orders with filters"""
    query = db.query(PurchaseOrder)
    
    if status_filter:
        query = query.filter(PurchaseOrder.status == status_filter)
    
    if supplier_id:
        query = query.filter(PurchaseOrder.supplier_id == supplier_id)
    
    pos = query.order_by(PurchaseOrder.order_date.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": query.count(),
        "purchase_orders": pos
    }


@router.get("/purchase-orders/{po_id}")
async def get_purchase_order(
    po_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get purchase order details with items"""
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    items = db.query(PurchaseOrderItem).filter(PurchaseOrderItem.purchase_order_id == po_id).all()
    
    return {
        "purchase_order": po,
        "items": items,
        "supplier": db.query(Supplier).filter(Supplier.id == po.supplier_id).first()
    }


@router.put("/purchase-orders/{po_id}/receive")
async def receive_purchase_order(
    po_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark purchase order as received and update stock levels"""
    if current_user.role not in ["admin", "inventory_manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    if po.status == "received":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="PO already received")
    
    # Get PO items
    po_items = db.query(PurchaseOrderItem).filter(PurchaseOrderItem.purchase_order_id == po_id).all()
    
    # Update stock for each item
    for po_item in po_items:
        # Record stock movement
        movement = StockMovement(
            item_id=po_item.item_id,
            movement_type="in",
            quantity=po_item.quantity_ordered,
            reference_number=po.po_number,
            reason="Purchase order received",
            performed_by=current_user.id
        )
        db.add(movement)
        
        # Update stock level
        update_stock_level(db, po_item.item_id, "in", po_item.quantity_ordered)
        
        # Mark as received
        po_item.quantity_received = po_item.quantity_ordered
    
    # Update PO status
    po.status = "received"
    po.actual_delivery = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": "Purchase order received successfully",
        "po_number": po.po_number,
        "items_received": len(po_items)
    }


@router.put("/purchase-orders/{po_id}/approve")
async def approve_purchase_order(
    po_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve a purchase order (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    if po.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve PO in {po.status} status"
        )
    
    po.status = "approved"
    po.approved_by = current_user.id
    
    db.commit()
    
    return {"message": "Purchase order approved", "po_number": po.po_number}
