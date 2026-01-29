#!/usr/bin/env python3
"""Generate Purchase Order test data in SQLite database - EXACT HANA SCHEMA"""

import sqlite3
from datetime import datetime, timedelta
import random

# Connect to database
conn = sqlite3.connect('app/database/p2p_data_products.db')
cursor = conn.cursor()

print("=" * 60)
print("Generating Purchase Order Test Data")
print("=" * 60)

# Check existing data
cursor.execute("SELECT COUNT(*) FROM PurchaseOrder")
existing_po = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM PurchaseOrderItem")
existing_items = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM PurchaseOrderScheduleLine")
existing_schedule = cursor.fetchone()[0]

if existing_po > 0:
    print(f"\nPurchase Order data already exists:")
    print(f"  - {existing_po} Purchase Orders")
    print(f"  - {existing_items} Purchase Order Items")
    print(f"  - {existing_schedule} Schedule Lines")
    print("\n[SUCCESS] Purchase Order data is ready!")
else:
    print("\nNo data found - generating with EXACT HANA schema...")
    
    # Generate 50 Purchase Orders
    print("\nGenerating Purchase Orders...")
    purchase_orders = []
    for i in range(1, 51):
        po_number = f"4500{str(i).zfill(6)}"
        supplier = f"SUPPLIER{100 + (i % 20)}"
        company_code = f"CC{1000 + (i % 5)}"
        purch_org = f"PO{1000 + (i % 3)}"
        
        po_date = datetime.now() - timedelta(days=random.randint(1, 365))
        
        cursor.execute("""
            INSERT INTO PurchaseOrder (
                PurchaseOrder, Supplier, CompanyCode, PurchasingOrganization,
                PurchaseOrderType, PurchaseOrderDate, CreatedByUser,
                DocumentCurrency, ExchangeRate, PurchasingDocumentDeletionCode
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            po_number, supplier, company_code, purch_org,
            "NB", po_date.strftime("%Y-%m-%d"), f"USER{i % 10}",
            "USD", 1.0, ""
        ))
        purchase_orders.append(po_number)

    print(f"  [OK] Created {len(purchase_orders)} Purchase Orders")

    # Generate Purchase Order Items (2-5 items per PO)
    print("\nGenerating Purchase Order Items...")
    item_count = 0
    po_items = []
    for po_number in purchase_orders:
        num_items = random.randint(2, 5)
        for item_num in range(1, num_items + 1):
            material = f"MAT{10000 + random.randint(1, 100)}"
            plant = f"PLANT{1000 + random.randint(1, 5)}"
            item_id = str(item_num * 10)
            
            cursor.execute("""
                INSERT INTO PurchaseOrderItem (
                    PurchaseOrder, PurchaseOrderItem, Material, Plant,
                    OrderQuantity, PurchaseOrderQuantityUnit, NetPriceAmount,
                    DocumentCurrency, PurchaseOrderItemCategory, AccountAssignmentCategory
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                po_number, item_id, material, plant,
                random.randint(1, 100), "EA", round(random.uniform(10, 1000), 2),
                "USD", "0", "K"
            ))
            po_items.append((po_number, item_id))
            item_count += 1

    print(f"  [OK] Created {item_count} Purchase Order Items")

    # Generate Schedule Lines (1-3 per item)
    print("\nGenerating Schedule Lines...")
    schedule_count = 0
    for po_number, item_id in po_items:
        num_schedules = random.randint(1, 3)
        for schedule_num in range(1, num_schedules + 1):
            schedule_line = str(schedule_num).zfill(4)
            delivery_date = datetime.now() + timedelta(days=random.randint(7, 90))
            
            # EXACT HANA SCHEMA: Use PurchaseOrderScheduleLine as column name
            cursor.execute("""
                INSERT INTO PurchaseOrderScheduleLine (
                    PurchaseOrder, PurchaseOrderItem, PurchaseOrderScheduleLine,
                    ScheduleLineDeliveryDate, ScheduleLineOrderQuantity,
                    PurchaseOrderQuantityUnit, DelivDateCategory
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                po_number, item_id, schedule_line,
                delivery_date.strftime("%Y-%m-%d"), random.randint(1, 50),
                "EA", "1"
            ))
            schedule_count += 1

    print(f"  [OK] Created {schedule_count} Schedule Lines")

    # Commit all changes
    conn.commit()
    print("\n[SUCCESS] Purchase Order test data generated!")

# Final verification
print("\n" + "=" * 60)
print("Final Data Count")
print("=" * 60)

cursor.execute("SELECT COUNT(*) FROM PurchaseOrder")
po_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM PurchaseOrderItem")
item_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM PurchaseOrderScheduleLine")
schedule_count = cursor.fetchone()[0]

print(f"  PurchaseOrder: {po_count} records")
print(f"  PurchaseOrderItem: {item_count} records")
print(f"  PurchaseOrderScheduleLine: {schedule_count} records")

conn.close()

print("\nNext steps:")
print("1. Refresh the browser page")
print("2. Purchase Order should now appear in Data Products!")