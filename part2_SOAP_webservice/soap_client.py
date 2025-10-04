# soap_client.py
from zeep import Client
import sys

def main():
    # Connect to SOAP service
    client = Client('http://localhost:8000/?wsdl')
    
    while True:
        print("\n=== SOAP CLIENT ===")
        print("1. Get all products")
        print("2. Get product by ID")
        print("3. Create product")
        print("4. Update product")
        print("5. Delete product")
        print("6. Exit")
        
        choice = input("Choose option (1-6): ")
        
        if choice == '1':
            try:
                result = client.service.GetAllProducts()
                print("\nAll Products:")
                for product in result:
                    print(f"  - {product}")
            except Exception as e:
                print(f"Error: {e}")
                
        elif choice == '2':
            try:
                product_id = int(input("Enter product ID: "))
                result = client.service.GetProduct(product_id)
                print(f"Result: {result}")
            except Exception as e:
                print(f"Error: {e}")
                
        elif choice == '3':
            try:
                name = input("Product name: ")
                quantity = int(input("Quantity: "))
                price = float(input("Price: "))
                
                result = client.service.CreateProduct(name, quantity, price)
                print(f"Result: {result}")
            except Exception as e:
                print(f"Error: {e}")
                
        elif choice == '4':
            try:
                product_id = int(input("Product ID to update: "))
                name = input("New name: ")
                quantity = int(input("New quantity: "))
                price = float(input("New price: "))
                
                result = client.service.UpdateProduct(product_id, name, quantity, price)
                print(f"Result: {result}")
            except Exception as e:
                print(f"Error: {e}")
                
        elif choice == '5':
            try:
                product_id = int(input("Product ID to delete: "))
                result = client.service.DeleteProduct(product_id)
                print(f"Result: {result}")
            except Exception as e:
                print(f"Error: {e}")
                
        elif choice == '6':
            print("Goodbye!")
            break
            
        else:
            print("Invalid option")

if __name__ == '__main__':
    main()