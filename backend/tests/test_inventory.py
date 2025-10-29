"""
Comprehensive tests for Inventory Management API endpoints.

Tests cover:
- Inventory item CRUD operations
- Stock movement tracking
- Low stock alerts
- Expiring items monitoring
- Supplier management
- Purchase order workflow
- Automatic stock updates
- Role-based access control
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.main import app
from app.models.models import (
    User, InventoryItem, Supplier, StockMovement,
    PurchaseOrder, PurchaseOrderItem
)

client = TestClient(app)


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def admin_token(client):
    """Create a admin user and return auth token."""
    # Register admin user
    user_data = {
        "name": "Admin User",
        "email": "admin@test.com",
        "phone": "1234567890",
        "password": "Test123!@#",
        "role": "admin",
        "date_of_birth": "1990-01-01"
    }
    client.post("/api/auth/register", json=user_data)
    
    # Login to get token
    response = client.post("/api/auth/login", data={
        "username": "admin@test.com",
        "password": "Test123!@#"
    })
    return response.json()["access_token"]
@pytest.fixture
def inventory_manager_token(client):
    """Create a inventory_manager user and return auth token."""
    # Register inventory_manager user
    user_data = {
        "name": "Inventory Manager",
        "email": "inventory@test.com",
        "phone": "9876543210",
        "password": "Test123!@#",
        "role": "inventory_manager",
        "date_of_birth": "1990-01-01"
    }
    client.post("/api/auth/register", json=user_data)
    
    # Login to get token
    response = client.post("/api/auth/login", data={
        "username": "inventory@test.com",
        "password": "Test123!@#"
    })
    return response.json()["access_token"]
@pytest.fixture
def doctor_token(client):
    """Create a staff user (doctor) and return auth token."""
    # Register staff user (doctor role)
    user_data = {
        "name": "Dr. Test",
        "email": "doctor.inv@test.com",
        "phone": "5555555555",
        "password": "Test123!@#",
        "role": "staff",
        "date_of_birth": "1990-01-01"
    }
    client.post("/api/auth/register", json=user_data)
    
    # Login to get token
    response = client.post("/api/auth/login", data={
        "username": "doctor.inv@test.com",
        "password": "Test123!@#"
    })
    return response.json()["access_token"]
@pytest.fixture
def sample_supplier(db_session):
    """Create sample supplier."""
    supplier = Supplier(
        name="MedSupply Inc",
        contact_person="John Supplier",
        email="contact@medsupply.com",
        phone="1234567890",
        address="123 Supply St",
        is_active=True
    )
    db_session.add(supplier)
    db_session.commit()
    db_session.refresh(supplier)
    return supplier


@pytest.fixture
def sample_items(db_session, sample_supplier):
    """Create sample inventory items."""
    items = [
        InventoryItem(
            item_code="MED-001",
            name="Paracetamol 500mg",
            category="Medication",
            description="Pain reliever",
            unit="Tablet",
            quantity_in_stock=100,
            minimum_stock_level=50,
            unit_price=0.50,
            supplier_id=sample_supplier.id,
            expiry_date=datetime.now() + timedelta(days=365)
        ),
        InventoryItem(
            item_code="MED-002",
            name="Bandage Roll",
            category="Medical Supplies",
            description="Sterile bandage",
            unit="Roll",
            quantity_in_stock=20,
            minimum_stock_level=30,  # Below minimum
            unit_price=2.00,
            supplier_id=sample_supplier.id,
            expiry_date=datetime.now() + timedelta(days=30)  # Expiring soon
        ),
        InventoryItem(
            item_code="MED-003",
            name="Surgical Gloves",
            category="Medical Supplies",
            description="Latex gloves",
            unit="Box",
            quantity_in_stock=150,
            minimum_stock_level=50,
            unit_price=10.00,
            supplier_id=sample_supplier.id,
            expiry_date=datetime.now() + timedelta(days=180)
        )
    ]
    for item in items:
        db_session.add(item)
    db_session.commit()
    return items


# ============================================================================
# INVENTORY ITEM TESTS
# ============================================================================

def test_create_inventory_item(client, inventory_manager_token, sample_supplier):
    """Test creating new inventory item."""
    item_data = {
        "item_code": "MED-NEW-001",
        "name": "Test Medicine",
        "category": "Medication",
        "description": "Test description",
        "unit": "Tablet",
        "quantity_in_stock": 100,
        "minimum_stock_level": 20,
        "unit_price": 5.00,
        "supplier_id": sample_supplier.id,
        "expiry_date": (datetime.now() + timedelta(days=365)).isoformat()
    }
    
    response = client.post(
        "/api/inventory/items",
        json=item_data,
        headers={"Authorization": f"Bearer {inventory_manager_token}"}
    )
    
    assert response.status_code == 201  # 201 Created for POST
    data = response.json()
    assert data["item_code"] == "MED-NEW-001"
    assert data["name"] == "Test Medicine"
    assert data["quantity_in_stock"] == 100


def test_list_inventory_items(client, inventory_manager_token, sample_items):
    """Test listing all inventory items."""
    response = client.get(
        "/api/inventory/items",
        headers={"Authorization": f"Bearer {inventory_manager_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3


def test_get_inventory_item(client, inventory_manager_token, sample_items):
    """Test getting specific inventory item."""
    item = sample_items[0]
    
    response = client.get(
        f"/api/inventory/items/{item.id}",
        headers={"Authorization": f"Bearer {inventory_manager_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["item_code"] == "MED-001"
    assert data["name"] == "Paracetamol 500mg"


def test_update_inventory_item(client, inventory_manager_token, sample_items):
    """Test updating inventory item."""
    item = sample_items[0]
    
    update_data = {
        "unit_price": 0.75,
        "minimum_stock_level": 60
    }
    
    response = client.put(
        f"/api/inventory/items/{item.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {inventory_manager_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["unit_price"] == 0.75
    assert data["minimum_stock_level"] == 60


def test_search_inventory_items(client, inventory_manager_token, sample_items):
    """Test searching inventory items."""
    response = client.get(
        "/api/inventory/items?search=Paracetamol",
        headers={"Authorization": f"Bearer {inventory_manager_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert "Paracetamol" in data[0]["name"]


def test_filter_by_category(client, inventory_manager_token, sample_items):
    """Test filtering items by category."""
    response = client.get(
        "/api/inventory/items?category=Medication",
        headers={"Authorization": f"Bearer {inventory_manager_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    for item in data:
        assert item["category"] == "Medication"


# ============================================================================
# STOCK ALERT TESTS
# ============================================================================

def test_get_low_stock_alerts(client, inventory_manager_token, sample_items):
    """Test getting items below minimum stock level."""
    response = client.get(
        "/api/inventory/items/low-stock/alerts",
        headers={"Authorization": f"Bearer {inventory_manager_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # MED-002 should be in alerts (20 < 30)
    low_stock_items = [item for item in data if item["item_code"] == "MED-002"]
    assert len(low_stock_items) > 0


def test_get_expiring_items(client, inventory_manager_token, sample_items):
    """Test getting items expiring within threshold."""
    response = client.get(
        "/api/inventory/items/expiring-soon?days=60",
        headers={"Authorization": f"Bearer {inventory_manager_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # MED-002 expires in 30 days, should be included
    expiring_items = [item for item in data if item["item_code"] == "MED-002"]
    assert len(expiring_items) > 0


# ============================================================================
# STOCK MOVEMENT TESTS
# ============================================================================

def test_record_stock_in(client, inventory_manager_token, sample_items):
    """Test recording stock addition."""
    item = sample_items[0]
    initial_stock = item.quantity_in_stock
    
    movement_data = {
        "item_id": item.id,
        "movement_type": "in",
        "quantity": 50,
        "reason": "New stock delivery",
        "reference_number": "PO-123"
    }
    
    response = client.post(
        "/api/inventory/stock/movement",
        json=movement_data,
        headers={"Authorization": f"Bearer {inventory_manager_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["movement_type"] == "in"
    assert data["quantity"] == 50
    
    # Verify stock was updated
    db_session.refresh(item)
    assert item.quantity_in_stock == initial_stock + 50


def test_record_stock_out(client, inventory_manager_token, sample_items):
    """Test recording stock removal."""
    item = sample_items[0]
    initial_stock = item.quantity_in_stock
    
    movement_data = {
        "item_id": item.id,
        "movement_type": "out",
        "quantity": 10,
        "reason": "Dispensed to patient"
    }
    
    response = client.post(
        "/api/inventory/stock/movement",
        json=movement_data,
        headers={"Authorization": f"Bearer {inventory_manager_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["movement_type"] == "out"
    
    # Verify stock was updated
    db_session.refresh(item)
    assert item.quantity_in_stock == initial_stock - 10


def test_record_stock_adjustment(client, inventory_manager_token, sample_items):
    """Test recording stock adjustment."""
    item = sample_items[0]
    
    movement_data = {
        "item_id": item.id,
        "movement_type": "adjustment",
        "quantity": 5,
        "reason": "Damaged items removed"
    }
    
    response = client.post(
        "/api/inventory/stock/movement",
        json=movement_data,
        headers={"Authorization": f"Bearer {inventory_manager_token}"}
    )
    
    assert response.status_code == 200


def test_list_stock_movements(client, inventory_manager_token, sample_items):
    """Test listing stock movement history."""
    response = client.get(
        "/api/inventory/stock/movements",
        headers={"Authorization": f"Bearer {inventory_manager_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_filter_movements_by_item(client, inventory_manager_token, sample_items):
    """Test filtering movements by item."""
    item = sample_items[0]
    
    response = client.get(
        f"/api/inventory/stock/movements?item_id={item.id}",
        headers={"Authorization": f"Bearer {inventory_manager_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    for movement in data:
        assert movement["item_id"] == item.id


# ============================================================================
# SUPPLIER TESTS
# ============================================================================

def test_create_supplier(client, inventory_manager_token):
    """Test creating new supplier."""
    supplier_data = {
        "name": "New Supplier Co",
        "contact_person": "Jane Doe",
        "email": "jane@newsupplier.com",
        "phone": "9998887777",
        "address": "456 Supplier Ave",
        "notes": "Reliable supplier"
    }
    
    response = client.post(
        "/api/inventory/suppliers",
        json=supplier_data,
        headers={"Authorization": f"Bearer {inventory_manager_token}"}
    )
    
    assert response.status_code == 201  # 201 Created for POST
    data = response.json()
    assert data["name"] == "New Supplier Co"
    assert data["is_active"] == True


def test_list_suppliers(client, inventory_manager_token, sample_supplier):
    """Test listing all suppliers."""
    response = client.get(
        "/api/inventory/suppliers",
        headers={"Authorization": f"Bearer {inventory_manager_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_supplier_details(client, inventory_manager_token, sample_supplier):
    """Test getting supplier with items."""
    response = client.get(
        f"/api/inventory/suppliers/{sample_supplier.id}",
        headers={"Authorization": f"Bearer {inventory_manager_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "MedSupply Inc"
    assert "items" in data


def test_filter_active_suppliers(client, inventory_manager_token, sample_supplier):
    """Test filtering active suppliers."""
    response = client.get(
        "/api/inventory/suppliers?active_only=true",
        headers={"Authorization": f"Bearer {inventory_manager_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    for supplier in data:
        assert supplier["is_active"] == True


# ============================================================================
# PURCHASE ORDER TESTS
# ============================================================================

def test_create_purchase_order(client, inventory_manager_token, sample_supplier, sample_items):
    """Test creating purchase order."""
    po_data = {
        "supplier_id": sample_supplier.id,
        "expected_delivery_date": (datetime.now() + timedelta(days=7)).isoformat(),
        "notes": "Urgent order",
        "items": [
            {
                "item_id": sample_items[0].id,
                "quantity_ordered": 100,
                "unit_price": 0.50
            },
            {
                "item_id": sample_items[1].id,
                "quantity_ordered": 50,
                "unit_price": 2.00
            }
        ]
    }
    
    response = client.post(
        "/api/inventory/purchase-orders",
        json=po_data,
        headers={"Authorization": f"Bearer {inventory_manager_token}"}
    )
    
    assert response.status_code == 201  # 201 Created for POST
    data = response.json()
    assert "po_number" in data
    assert data["status"] == "active"  # API creates as active by default
    assert data["supplier_id"] == sample_supplier.id
    assert len(data["items"]) == 2
    assert data["total_amount"] == 150.00  # (100 * 0.50) + (50 * 2.00)


def test_list_purchase_orders(client, inventory_manager_token):
    """Test listing purchase orders."""
    response = client.get(
        "/api/inventory/purchase-orders",
        headers={"Authorization": f"Bearer {inventory_manager_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_purchase_order(client, inventory_manager_token, sample_supplier, sample_items):
    """Test getting purchase order details."""
    # Create PO
    po = PurchaseOrder(
        po_number="PO-TEST-001",
        supplier_id=sample_supplier.id,
        status="pending",
        total_amount=100.00,
        expected_delivery_date=datetime.now() + timedelta(days=7)
    )
    db_session.add(po)
    db_session.commit()
    
    response = client.get(
        f"/api/inventory/purchase-orders/{po.id}",
        headers={"Authorization": f"Bearer {inventory_manager_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["po_number"] == "PO-TEST-001"


def test_receive_purchase_order(client, inventory_manager_token, sample_supplier, sample_items):
    """Test receiving purchase order items."""
    # Create PO
    item = sample_items[0]
    po = PurchaseOrder(
        po_number="PO-TEST-002",
        supplier_id=sample_supplier.id,
        status="approved",
        total_amount=50.00,
        expected_delivery_date=datetime.now()
    )
    db_session.add(po)
    db_session.commit()
    
    po_item = PurchaseOrderItem(
        purchase_order_id=po.id,
        item_id=item.id,
        quantity_ordered=100,
        quantity_received=0,
        unit_price=0.50
    )
    db_session.add(po_item)
    db_session.commit()
    
    initial_stock = item.quantity_in_stock
    
    receive_data = {
        "items": [
            {
                "item_id": item.id,
                "quantity_received": 100
            }
        ],
        "notes": "All items received in good condition"
    }
    
    response = client.put(
        f"/api/inventory/purchase-orders/{po.id}/receive",
        json=receive_data,
        headers={"Authorization": f"Bearer {inventory_manager_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "received"
    
    # Verify stock was updated
    db_session.refresh(item)
    assert item.quantity_in_stock == initial_stock + 100


def test_approve_purchase_order(client, admin_token, sample_supplier):
    """Test admin approving purchase order."""
    po = PurchaseOrder(
        po_number="PO-TEST-003",
        supplier_id=sample_supplier.id,
        status="pending",
        total_amount=200.00,
        expected_delivery_date=datetime.now() + timedelta(days=7)
    )
    db_session.add(po)
    db_session.commit()
    
    approval_data = {
        "approved": True,
        "approval_notes": "Approved for ordering"
    }
    
    response = client.put(
        f"/api/inventory/purchase-orders/{po.id}/approve",
        json=approval_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"


def test_filter_pos_by_status(client, inventory_manager_token, sample_supplier):
    """Test filtering purchase orders by status."""
    # Create POs with different statuses
    statuses = ["pending", "approved", "received"]
    for status in statuses:
        po = PurchaseOrder(
            po_number=f"PO-{status.upper()}-001",
            supplier_id=sample_supplier.id,
            status=status,
            total_amount=100.00,
            expected_delivery_date=datetime.now() + timedelta(days=7)
        )
        db_session.add(po)
    db_session.commit()
    
    response = client.get(
        "/api/inventory/purchase-orders?status=pending",
        headers={"Authorization": f"Bearer {inventory_manager_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    for po in data:
        assert po["status"] == "pending"


# ============================================================================
# PERMISSION TESTS
# ============================================================================

def test_doctor_cannot_create_items(client, doctor_token, sample_supplier):
    """Test that doctors cannot create inventory items."""
    item_data = {
        "item_code": "UNAUTHORIZED",
        "name": "Test",
        "category": "Test",
        "unit": "Test",
        "quantity_in_stock": 10,
        "minimum_stock_level": 5,
        "unit_price": 1.00,
        "supplier_id": sample_supplier.id
    }
    
    response = client.post(
        "/api/inventory/items",
        json=item_data,
        headers={"Authorization": f"Bearer {doctor_token}"}
    )
    
    assert response.status_code == 403


def test_doctor_can_view_items(client, doctor_token, sample_items):
    """Test that doctors can view inventory items."""
    response = client.get(
        "/api/inventory/items",
        headers={"Authorization": f"Bearer {doctor_token}"}
    )
    
    assert response.status_code == 200


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

def test_insufficient_stock_removal(client, inventory_manager_token, sample_items):
    """Test attempting to remove more stock than available."""
    item = sample_items[1]  # Has 20 in stock
    
    movement_data = {
        "item_id": item.id,
        "movement_type": "out",
        "quantity": 100,  # More than available
        "reason": "Test"
    }
    
    response = client.post(
        "/api/inventory/stock/movement",
        json=movement_data,
        headers={"Authorization": f"Bearer {inventory_manager_token}"}
    )
    
    # Should fail or warn
    assert response.status_code in [400, 422]


def test_partial_po_receive(client, inventory_manager_token, sample_supplier, sample_items):
    """Test receiving partial quantity of purchase order."""
    item = sample_items[0]
    po = PurchaseOrder(
        po_number="PO-PARTIAL-001",
        supplier_id=sample_supplier.id,
        status="approved",
        total_amount=100.00,
        expected_delivery_date=datetime.now()
    )
    db_session.add(po)
    db_session.commit()
    
    po_item = PurchaseOrderItem(
        purchase_order_id=po.id,
        item_id=item.id,
        quantity_ordered=100,
        quantity_received=0,
        unit_price=1.00
    )
    db_session.add(po_item)
    db_session.commit()
    
    receive_data = {
        "items": [
            {
                "item_id": item.id,
                "quantity_received": 50  # Only half
            }
        ]
    }
    
    response = client.put(
        f"/api/inventory/purchase-orders/{po.id}/receive",
        json=receive_data,
        headers={"Authorization": f"Bearer {inventory_manager_token}"}
    )
    
    assert response.status_code == 200
    # PO should be partially received
    data = response.json()
    assert data["status"] in ["partially_received", "received"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
