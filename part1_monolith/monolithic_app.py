# monolithic_inventory.py
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sys

# Configuration de la base de données
DATABASE_URL = "postgresql://inventory:inventory@localhost:5432/inventory"

# Initialisation SQLAlchemy
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Modèle de données
class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

# Création des tables
def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Tables créées avec succès!")

# Validation des données
def validate_product_data(name, quantity, price):
    errors = []
    
    if not name or len(name.strip()) == 0:
        errors.append("Le nom du produit ne peut pas être vide")
    
    if quantity < 0:
        errors.append("La quantité ne peut pas être négative")
    
    if price < 0:
        errors.append("Le prix ne peut pas être négatif")
    
    return errors

# Opérations CRUD
def create_product(session, name, quantity, price):
    # Validation
    errors = validate_product_data(name, quantity, price)
    if errors:
        return False, errors
    
    # Création du produit
    product = Product(name=name, quantity=quantity, price=price)
    session.add(product)
    session.commit()
    return True, f"Produit '{name}' créé avec ID: {product.id}"

def get_all_products(session):
    return session.query(Product).all()

def get_product_by_id(session, product_id):
    return session.query(Product).filter(Product.id == product_id).first()

def update_product(session, product_id, name=None, quantity=None, price=None):
    product = get_product_by_id(session, product_id)
    if not product:
        return False, "Produit non trouvé"
    
    # Validation des nouvelles valeurs
    if name is not None:
        if len(name.strip()) == 0:
            return False, ["Le nom ne peut pas être vide"]
        product.name = name
    
    if quantity is not None:
        if quantity < 0:
            return False, ["La quantité ne peut pas être négative"]
        product.quantity = quantity
    
    if price is not None:
        if price < 0:
            return False, ["Le prix ne peut pas être négative"]
        product.price = price
    
    session.commit()
    return True, "Produit mis à jour avec succès"

def delete_product(session, product_id):
    product = get_product_by_id(session, product_id)
    if not product:
        return False, "Produit non trouvé"
    
    session.delete(product)
    session.commit()
    return True, "Produit supprimé avec succès"

# Affichage des produits
def display_products(products):
    if not products:
        print("Aucun produit trouvé")
        return
    
    print("\n" + "="*60)
    print(f"{'ID':<5} {'Nom':<20} {'Quantité':<10} {'Prix':<10}")
    print("="*60)
    for product in products:
        print(f"{product.id:<5} {product.name:<20} {product.quantity:<10} {product.price:<10.2f}")
    print("="*60)

# Interface utilisateur
def main_menu():
    print("\n=== GESTIONNAIRE D'INVENTAIRE MONOLITHIQUE ===")
    print("1. Afficher tous les produits")
    print("2. Ajouter un produit")
    print("3. Modifier un produit")
    print("4. Supprimer un produit")
    print("5. Rechercher un produit par ID")
    print("6. Quitter")
    
    return input("Choisissez une option (1-6): ")

def main():
    # Création des tables
    try:
        create_tables()
    except Exception as e:
        print(f"Erreur de connexion à la base de données: {e}")
        print("Vérifiez que PostgreSQL est démarré et que la base 'inventory' existe")
        return
    
    session = SessionLocal()
    
    while True:
        choice = main_menu()
        
        if choice == '1':
            # Afficher tous les produits
            products = get_all_products(session)
            display_products(products)
            
        elif choice == '2':
            # Ajouter un produit
            print("\n--- AJOUTER UN PRODUIT ---")
            name = input("Nom du produit: ")
            try:
                quantity = int(input("Quantité: "))
                price = float(input("Prix: "))
            except ValueError:
                print("Erreur: La quantité et le prix doivent être des nombres")
                continue
            
            success, result = create_product(session, name, quantity, price)
            if success:
                print(f"✓ {result}")
            else:
                print("✗ Erreurs:")
                for error in result:
                    print(f"  - {error}")
                    
        elif choice == '3':
            # Modifier un produit
            print("\n--- MODIFIER UN PRODUIT ---")
            try:
                product_id = int(input("ID du produit à modifier: "))
            except ValueError:
                print("Erreur: L'ID doit être un nombre")
                continue
            
            product = get_product_by_id(session, product_id)
            if not product:
                print("✗ Produit non trouvé")
                continue
            
            print(f"Produit actuel: {product.name}, Quantité: {product.quantity}, Prix: {product.price}")
            
            name = input("Nouveau nom (laisser vide pour ne pas changer): ")
            name = name if name.strip() else None
            
            quantity_str = input("Nouvelle quantité (laisser vide pour ne pas changer): ")
            quantity = int(quantity_str) if quantity_str.strip() else None
            
            price_str = input("Nouveau prix (laisser vide pour ne pas changer): ")
            price = float(price_str) if price_str.strip() else None
            
            success, result = update_product(session, product_id, name, quantity, price)
            if success:
                print(f"✓ {result}")
            else:
                print("✗ Erreurs:")
                for error in result:
                    print(f"  - {error}")
                    
        elif choice == '4':
            # Supprimer un produit
            print("\n--- SUPPRIMER UN PRODUIT ---")
            try:
                product_id = int(input("ID du produit à supprimer: "))
            except ValueError:
                print("Erreur: L'ID doit être un nombre")
                continue
            
            success, result = delete_product(session, product_id)
            if success:
                print(f"✓ {result}")
            else:
                print(f"✗ {result}")
                
        elif choice == '5':
            # Rechercher par ID
            print("\n--- RECHERCHER UN PRODUIT ---")
            try:
                product_id = int(input("ID du produit: "))
            except ValueError:
                print("Erreur: L'ID doit être un nombre")
                continue
            
            product = get_product_by_id(session, product_id)
            if product:
                display_products([product])
            else:
                print("✗ Produit non trouvé")
                
        elif choice == '6':
            print("Au revoir!")
            break
            
        else:
            print("Option invalide. Veuillez choisir entre 1 et 6.")
    
    session.close()

if __name__ == "__main__":
    main()