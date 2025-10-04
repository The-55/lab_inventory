# monolithic_inventory.py
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database setup
DATABASE_URL = "postgresql://inventory:inventory@localhost:5432/inventory"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Product model
class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Validation
def validate_product(name, quantity, price):
    if quantity < 0:
        return "Quantity cannot be negative"
    if price < 0:
        return "Price cannot be negative"
    if not name.strip():
        return "Name cannot be empty"
    return None

# CRUD operations
def create_product(session, name, quantity, price):
    error = validate_product(name, quantity, price)
    if error:
        return False, error
    
    product = Product(name=name, quantity=quantity, price=price)
    session.add(product)
    session.commit()
    return True, f"Product created with ID: {product.id}"

def get_all_products(session):
    return session.query(Product).all()

def get_product_by_id(session, product_id):
    return session.query(Product).filter(Product.id == product_id).first()

def update_product(session, product_id, name=None, quantity=None, price=None):
    product = get_product_by_id(session, product_id)
    if not product:
        return False, "Product not found"
    
    if name is not None:
        product.name = name
    if quantity is not None:
        if quantity < 0:
            return False, "Quantity cannot be negative"
        product.quantity = quantity
    if price is not None:
        if price < 0:
            return False, "Price cannot be negative"
        product.price = price
    
    session.commit()
    return True, "Product updated"

def delete_product(session, product_id):
    product = get_product_by_id(session, product_id)
    if not product:
        return False, "Product not found"
    
    session.delete(product)
    session.commit()
    return True, "Product deleted"

# Display products
def show_products(products):
    if not products:
        print("No products found")
        return
    
    print("\n" + "="*50)
    print(f"{'ID':<5} {'Name':<15} {'Qty':<10} {'Price':<10}")
    print("="*50)
    for p in products:
        print(f"{p.id:<5} {p.name:<15} {p.quantity:<10} {p.price:<10.2f}")
    print("="*50)

# User interface
def main():
    create_tables()
    session = SessionLocal()
    
    while True:
        print("\n=== INVENTORY MANAGEMENT ===")
        print("1. Show all products")
        print("2. Add product")
        print("3. Update product")
        print("4. Delete product")
        print("5. Find product by ID")
        print("6. Exit")
        
        choice = input("Choose option (1-6): ")
        
        if choice == '1':
            products = get_all_products(session)
            show_products(products)
            
        elif choice == '2':
            print("\n--- ADD PRODUCT ---")
            name = input("Product name: ")
            try:
                quantity = int(input("Quantity: "))
                price = float(input("Price: "))
            except:
                print("Error: Quantity and price must be numbers")
                continue
            
            success, message = create_product(session, name, quantity, price)
            print(f"{'✓' if success else '✗'} {message}")
            
        elif choice == '3':
            print("\n--- UPDATE PRODUCT ---")
            try:
                product_id = int(input("Product ID to update: "))
            except:
                print("Error: ID must be a number")
                continue
            
            name = input("New name (leave empty to keep current): ").strip()
            name = name if name else None
            
            quantity_input = input("New quantity (leave empty to keep current): ").strip()
            quantity = int(quantity_input) if quantity_input else None
            
            price_input = input("New price (leave empty to keep current): ").strip()
            price = float(price_input) if price_input else None
            
            success, message = update_product(session, product_id, name, quantity, price)
            print(f"{'✓' if success else '✗'} {message}")
            
        elif choice == '4':
            print("\n--- DELETE PRODUCT ---")
            try:
                product_id = int(input("Product ID to delete: "))
            except:
                print("Error: ID must be a number")
                continue
            
            success, message = delete_product(session, product_id)
            print(f"{'✓' if success else '✗'} {message}")
            
        elif choice == '5':
            print("\n--- FIND PRODUCT ---")
            try:
                product_id = int(input("Product ID: "))
            except:
                print("Error: ID must be a number")
                continue
            
            product = get_product_by_id(session, product_id)
            if product:
                show_products([product])
            else:
                print("Product not found")
                
        elif choice == '6':
            print("Goodbye!")
            break
            
        else:
            print("Invalid option")
    
    session.close()

if __name__ == "__main__":
    main()