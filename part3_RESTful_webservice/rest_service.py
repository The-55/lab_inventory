from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional
import uvicorn

# Database setup
DATABASE_URL = "postgresql://inventory:inventory@localhost:5432/inventory"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy Product Model
class ProductDB(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

# Pydantic Models for validation
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Product name")
    quantity: int = Field(..., ge=0, description="Quantity in stock")
    price: float = Field(..., ge=0, description="Price per unit")

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    quantity: Optional[int] = Field(None, ge=0)
    price: Optional[float] = Field(None, ge=0)

class ProductResponse(ProductBase):
    id: int
    
    class Config:
        from_attributes = True

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# FastAPI app
app = FastAPI(
    title="Inventory REST API",
    description="A modern REST API for inventory management",
    version="1.0.0"
)

# Health check
@app.get("/", tags=["Health"])
def root():
    return {"message": "Inventory REST API is running!"}

# Get all products
@app.get("/products", response_model=List[ProductResponse], tags=["Products"])
def get_all_products(db: Session = Depends(get_db)):
    """Get all products from inventory"""
    products = db.query(ProductDB).all()
    return products

# Get product by ID
@app.get("/products/{product_id}", response_model=ProductResponse, tags=["Products"])
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product by ID"""
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    return product

# Create new product
@app.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED, tags=["Products"])
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product"""
    # Check if product name already exists
    existing_product = db.query(ProductDB).filter(ProductDB.name == product.name).first()
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this name already exists"
        )
    
    db_product = ProductDB(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# Update product
@app.put("/products/{product_id}", response_model=ProductResponse, tags=["Products"])
def update_product(product_id: int, product_update: ProductUpdate, db: Session = Depends(get_db)):
    """Update an existing product"""
    db_product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    # Update only provided fields
    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

# Delete product
@app.delete("/products/{product_id}", status_code=status.HTTP_200_OK, tags=["Products"])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product"""
    db_product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    db.delete(db_product)
    db.commit()
    return {"message": f"Product with ID {product_id} deleted successfully"}

# Search products by name
@app.get("/products/search/{name}", response_model=List[ProductResponse], tags=["Search"])
def search_products(name: str, db: Session = Depends(get_db)):
    """Search products by name"""
    products = db.query(ProductDB).filter(ProductDB.name.ilike(f"%{name}%")).all()
    return products

if __name__ == "__main__":
    create_tables()
    uvicorn.run(
        "rest_service:app",
        host="localhost",
        port=8000,
        reload=True,
        log_level="info"
    )