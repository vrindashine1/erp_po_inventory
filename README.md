
# ERP Purchase Order & Inventory Management System

## Objective: 
Develop a simple Purchase Order (PO) Management System integrated with Inventory Management for an ERP. The system should allow tracking of inventory levels, supplier orders, and approval workflows.
 # Problem Statement: 
Your company is building an ERP Accounting Software that includes an inventory and purchasing module. Your task is to develop a Purchase Order system that integrates with inventory management.
A Purchase Order (PO) is a document issued by a buyer to a supplier indicating the products, quantity, and agreed price. 


## Features
o	Supplier: Stores supplier details. 
o	Product: Stores information about products that can be ordered. 
o	Purchase Order Creation: Create new orders for products from suppliers. 
o	InventoryTransaction: Logs stock changes when POs are received. 
o Role-Based Approval Workflow:
       Employees: can create Purchase Orders.
       Managers: can approve Purchase Orders.
o PO Status Tracking: Purchase Orders automatically update their status (Pending, Approved, Partially Delivered, Completed).
o User Management: Basic user roles (Employee, Manager, Admin) to control access.



## Technologies Used

* **Backend:**
    * Python 3.13.5
    * Django (Web Framework)
    * Django REST Framework (for API endpoints)
    * PostgreSQL (Database)

* **Frontend:**
    * HTML, CSS
    * Bootstrap 5 (for styling and responsive design)
    * JavaScript (for dynamic interactions)

## Getting Started

# Prerequisites

Before you begin, ensure you have:
  * Python 3.13. installed.
  * PostgreSQL installed and running.

### 1. Database Setup

1.  Open your system's terminal/command prompt.
2.  Access PostgreSQL interactive terminal (psql):
     >> psql -U postgres 
    (Enter your PostgreSQL superuser password when prompted)

3.  **Create a new database:**
    
    >>CREATE DATABASE erp_db;
    
4.  **Create a new database user (recommended):**
    
    >>CREATE USER erp_user WITH PASSWORD 'your_secure_password';
    (Replace `your_secure_password` with a strong password)

5.  **Grant privileges:**
    
    >>GRANT ALL PRIVILEGES ON DATABASE erp_db TO erp_user;
    
6.  **Exit psql:**
    
    >>\q
    

### 2. Project Setup

1.  Clone the repository (if applicable) or navigate to your project directory.
    bash
    git clone <your-repository-url>
    cd <your-project-folder>

    # If you already have the files:
    cd /path/to/your/erp_po_inventory_project
    
2.  Create a Python virtual environment:
    bash
    python -m venv venv
    
3.  Activate the virtual environment:
    * **Windows:** `.\venv\Scripts\activate`
    (You should see `(venv)` in your terminal prompt)

4.  **Install project dependencies:**
    bash
    pip install -r requirements.txt
    # If you haven't created requirements.txt yet, run:
    # pip install Django djangorestframework psycopg2-binary
    
5.  **Configure `settings.py`:**
    * Open `erp_po_inventory/settings.py`.
    * Update the `DATABASES` section with your PostgreSQL credentials:
        python
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'erp_db',
                'USER': 'erp_user',
                'PASSWORD': 'your_secure_password', # Use the password you set above
                'HOST': 'localhost',
                'PORT': '5432',
            }
        }
        
    * Ensure `INSTALLED_APPS` includes:
        python
        INSTALLED_APPS = [
            # ...
            'rest_framework',
            'core',
            'purchase_order',
            # ...
        ]
        
    * Add `AUTH_USER_MODEL = 'core.User'` to use the custom user model.

### 3. Run Migrations

1.  **Make migrations for your apps:**
    bash
    python manage.py makemigrations core
    python manage.py makemigrations purchase_order
    
2.  **Apply migrations to create database tables:**
    bash
    python manage.py migrate
   

### 4. Create a Superuser

This user will have full access to the Django Admin Panel.
bash
python manage.py createsuperuser

### 5. Start the Application

bash
python manage.py runserver

