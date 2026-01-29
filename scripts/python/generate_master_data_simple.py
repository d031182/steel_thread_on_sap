#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Simple Master Data for Cost Center, Company Code, and Product

Generates realistic sample data WITHOUT external dependencies.
Master data matches realistic SAP patterns for easy HANA substitution.

Usage: python scripts/python/generate_master_data_simple.py
"""

import sqlite3
import sys

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SQLITE_DB = "app/database/p2p_data_products.db"

def generate_cost_center_data(conn):
    """Generate Cost Center master data (20 cost centers)"""
    print("\n[1/3] Generating Cost Center data...")
    cursor = conn.cursor()
    
    cost_centers = [
        ('CC1000', 'Production Planning'),
        ('CC1010', 'Manufacturing'),
        ('CC1020', 'Quality Control'),
        ('CC2000', 'Sales Management'),
        ('CC2010', 'Customer Service'),
        ('CC3000', 'IT Services'),
        ('CC3010', 'IT Infrastructure'),
        ('CC4000', 'Human Resources'),
        ('CC4010', 'Training & Development'),
        ('CC5000', 'Finance & Accounting'),
        ('CC5010', 'Controlling'),
        ('CC6000', 'Procurement'),
        ('CC6010', 'Supplier Management'),
        ('CC7000', 'Logistics'),
        ('CC7010', 'Warehouse Management'),
        ('CC8000', 'Research & Development'),
        ('CC8010', 'Innovation Lab'),
        ('CC9000', 'Marketing'),
        ('CC9010', 'Brand Management'),
        ('CC9020', 'Digital Marketing')
    ]
    
    for cc_id, name in cost_centers:
        # Insert into CostCenter table (just key fields)
        cursor.execute("""
            INSERT OR REPLACE INTO CostCenter 
            (CostCenter, ControllingArea, CompanyCode, ValidityStartDate, ValidityEndDate)
            VALUES (?, '1000', '1000', '2024-01-01', '9999-12-31')
        """, (cc_id,))
        
        # Insert text description
        cursor.execute("""
            INSERT OR REPLACE INTO CostCenterText
            (CostCenter, Language, CostCenterName, CostCenterDescription)
            VALUES (?, 'EN', ?, ?)
        """, (cc_id, name, f"Description for {name}"))
    
    conn.commit()
    print(f"  ✓ Created {len(cost_centers)} cost centers with texts")

def generate_company_code_data(conn):
    """Generate Company Code master data (5 companies)"""
    print("\n[2/3] Generating Company Code data...")
    cursor = conn.cursor()
    
    companies = [
        ('1000', 'SAP AG', 'Walldorf', 'DE', 'EUR'),
        ('1010', 'SAP America', 'Newtown Square', 'US', 'USD'),
        ('1020', 'SAP UK', 'London', 'GB', 'GBP'),
        ('1030', 'SAP France', 'Paris', 'FR', 'EUR'),
        ('1040', 'SAP Asia Pacific', 'Singapore', 'SG', 'SGD')
    ]
    
    for code, name, city, country, currency in companies:
        cursor.execute("""
            INSERT OR REPLACE INTO CompanyCode
            (CompanyCode, CompanyCodeName, CityName, Country, Currency)
            VALUES (?, ?, ?, ?, ?)
        """, (code, name, city, country, currency))
    
    conn.commit()
    print(f"  ✓ Created {len(companies)} company codes")

def generate_product_data(conn):
    """Generate Product master data (50 products)"""
    print("\n[3/3] Generating Product data...")
    cursor = conn.cursor()
    
    categories = ['RAW', 'FERT', 'HALB', 'HAWA', 'DIEN']
    units = ['PC', 'KG', 'L', 'M', 'EA']
    
    for i in range(1, 51):
        cat_code = categories[i % len(categories)]
        unit = units[i % len(units)]
        product_id = f"P{1000 + i}"
        
        # Product table has NO ProductName column!
        # Only insert key fields that exist
        cursor.execute("""
            INSERT OR REPLACE INTO Product
            (Product, ProductType, BaseUnit, NetWeight, GrossWeight)
            VALUES (?, ?, ?, ?, ?)
        """, (product_id, cat_code, unit, 
              round(10.0 + (i * 0.5), 2), round(12.0 + (i * 0.6), 2)))
    
    conn.commit()
    print(f"  ✓ Created 50 products")

def verify_data(conn):
    """Verify all data was created"""
    print("\n" + "="*80)
    print("DATA VERIFICATION")
    print("="*80)
    
    cursor = conn.cursor()
    
    tables_to_check = [
        ('CostCenter', 'Cost Center'),
        ('CostCenterText', 'Cost Center'),
        ('CompanyCode', 'Company Code'),
        ('Product', 'Product')
    ]
    
    print("\nRecord Counts:")
    all_good = True
    
    for table, product in tables_to_check:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            status = "✓" if count > 0 else "✗"
            print(f"  {status} {table}: {count} records")
            if count == 0:
                all_good = False
        except Exception as e:
            print(f"  ✗ {table}: [ERROR] {e}")
            all_good = False
    
    return all_good

def main():
    """Main data generation process"""
    print("="*80)
    print("Generate Master Data (Cost Center, Company Code, Product)")
    print("="*80)
    print(f"\nTarget Database: {SQLITE_DB}")
    print("Strategy: Simple sample data WITHOUT external dependencies")
    print()
    
    try:
        conn = sqlite3.connect(SQLITE_DB)
        
        # Generate master data
        generate_cost_center_data(conn)
        generate_company_code_data(conn)
        generate_product_data(conn)
        
        # Verify
        success = verify_data(conn)
        
        conn.close()
        
        if success:
            print("\n✓ ALL MASTER DATA GENERATED!")
            print("\nNext steps:")
            print("  1. Refresh UI: Click browser refresh")
            print("  2. Click on Cost Center / Company Code / Product")
            print("  3. All tables should now show data!")
            return 0
        else:
            print("\n⚠ Some tables still empty - check errors above")
            return 1
        
    except Exception as e:
        print(f"\n[ERROR] Data generation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())