# soap_service.py
from spyne import Application, ServiceBase, rpc, Integer, Unicode, Float, Array
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from sqlalchemy import create_engine, Column, Integer as SqlInteger, String, Float as SqlFloat
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

# Database setup (same as Part 1)
DATABASE_URL = "postgresql://inventory:inventory@localhost:5432/inventory"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Product model
class Product(Base):
    __tablename__ = "products"
    
    id = Column(SqlInteger, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    quantity = Column(SqlInteger, nullable=False)
    price = Column(SqlFloat, nullable=False)

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# SOAP Service
class InventorySOAPService(ServiceBase):
    
    @rpc(Integer, _returns=Unicode)
    def GetProduct(ctx, product_id):
        """Get a product by ID"""
        session = SessionLocal()
        try:
            product = session.query(Product).filter(Product.id == product_id).first()
            if product:
                return f"Product {product.id}: {product.name}, Quantity: {product.quantity}, Price: ${product.price:.2f}"
            else:
                return "Product not found"
        finally:
            session.close()
    
    @rpc(Unicode, Integer, Float, _returns=Unicode)
    def CreateProduct(ctx, name, quantity, price):
        """Create a new product"""
        # Validation
        if quantity < 0:
            return "Error: Quantity cannot be negative"
        if price < 0:
            return "Error: Price cannot be negative"
        if not name or not name.strip():
            return "Error: Name cannot be empty"
        
        session = SessionLocal()
        try:
            product = Product(name=name, quantity=quantity, price=price)
            session.add(product)
            session.commit()
            return f"Product created successfully with ID: {product.id}"
        except Exception as e:
            session.rollback()
            return f"Error creating product: {str(e)}"
        finally:
            session.close()
    
    @rpc(Integer, Unicode, Integer, Float, _returns=Unicode)
    def UpdateProduct(ctx, product_id, name, quantity, price):
        """Update an existing product"""
        # Validation
        if quantity < 0:
            return "Error: Quantity cannot be negative"
        if price < 0:
            return "Error: Price cannot be negative"
        if not name or not name.strip():
            return "Error: Name cannot be empty"
        
        session = SessionLocal()
        try:
            product = session.query(Product).filter(Product.id == product_id).first()
            if not product:
                return "Error: Product not found"
            
            product.name = name
            product.quantity = quantity
            product.price = price
            
            session.commit()
            return f"Product {product_id} updated successfully"
        except Exception as e:
            session.rollback()
            return f"Error updating product: {str(e)}"
        finally:
            session.close()
    
    @rpc(Integer, _returns=Unicode)
    def DeleteProduct(ctx, product_id):
        """Delete a product"""
        session = SessionLocal()
        try:
            product = session.query(Product).filter(Product.id == product_id).first()
            if not product:
                return "Error: Product not found"
            
            session.delete(product)
            session.commit()
            return f"Product {product_id} deleted successfully"
        except Exception as e:
            session.rollback()
            return f"Error deleting product: {str(e)}"
        finally:
            session.close()
    
    @rpc(_returns=Array(Unicode))
    def GetAllProducts(ctx):
        """Get all products"""
        session = SessionLocal()
        try:
            products = session.query(Product).all()
            result = []
            for product in products:
                result.append(f"ID: {product.id}, Name: {product.name}, Quantity: {product.quantity}, Price: ${product.price:.2f}")
            return result
        finally:
            session.close()

# Create SOAP application
application = Application(
    [InventorySOAPService],
    'inventory.soap',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

# WSGI application for web servers
wsgi_application = WsgiApplication(application)

if __name__ == '__main__':
    # Create tables
    create_tables()
    
    # Start the development server
    from wsgiref.simple_server import make_server
    
    print("Starting SOAP service on http://localhost:8000")
    print("WSDL available at: http://localhost:8000/?wsdl")
    
    server = make_server('localhost', 8000, wsgi_application)
    server.serve_forever()