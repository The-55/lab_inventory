# test_monolithic.py
from monolithic_inventory import create_tables, SessionLocal, create_product, get_all_products

def test_system():
    try:
        create_tables()
        session = SessionLocal()
        
        # Add test products
        test_products = [
            ("Laptop", 5, 999.99),
            ("Mouse", 20, 29.99),
            ("Keyboard", 15, 79.99)
        ]
        
        for name, qty, price in test_products:
            success, msg = create_product(session, name, qty, price)
            print(f"{'✓' if success else '✗'} {msg}")
        
        # Show all products
        products = get_all_products(session)
        print("\nAll products in database:")
        for p in products:
            print(f"  {p.id}: {p.name} - {p.quantity} pcs - ${p.price:.2f}")
        
        session.close()
        print("\n✓ System test completed successfully!")
        
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    test_system()