#  Multi-Shop Inventory & Sales Reporting

Real-time tracking, Google Sheets integration, and shop-wise dashboards — all in one place.

![Dashboard Page](/screenshots/misrdashboard.png)


## Features
### Shop Management
- Shop-Wise Control:
- Each user manages their own shop with personalized access to items, purchases, and sales logs.

### Reporting Dashboard
- Real-Time Reports:
- Get clean, up-to-date visualizations of inventory summaries, profits, and trends.

### Performance Metrics:
- Track cost rates, sales amounts, and profit margins for better decision-making.

### Google Sheets Integration
- Automatically sync purchase and sales data between Google Sheets and your dashboard.


## Benefits
- Centralized dashboard for multi-shop tracking
- Easy integration with Google Sheets
- Real-time analytics with interactive charts
- User-specific shop access control

## Use Cases
- Multi-branch retail stores tracking sales independently
- Teams needing collaborative inventory management via Google Sheets

## Tech Stack

- **Backend:** Django (Python)
- **Frontend:** Bootstrap 5 + HTML Templates
- **Database:** Mysql
- **Other:** Django Messages Framework, Static Files,Google Sheet Api



##  Installation Guide for To do App Project

### 1. Clone the repository
git clone https://github.com/Darpan-Anjanay/MISR.git  # Download the project from GitHub
cd MISR  # Move into the project directory

### 2. Create a virtual environment
python -m venv venv  # Create a virtual environment named 'venv'

### 3. Activate the virtual environment

venv\Scripts\activate  # For Windows

### 4.Install the project dependencies
pip install -r requirements.txt  # Install all required packages listed in requirements.txt

### 5. Set up the database
python manage.py makemigrations  # Generate migration files based on the models
python manage.py migrate  # Apply the migrations to create the database schema

### 6. Create a superuser for accessing the Django admin panel
python manage.py createsuperuser  # Follow the prompts (username, email, password)

### 7. Run the development server
python manage.py runserver  # Start the local server

###  Now, open your browser and go to: http://127.0.0.1:8000/
###  To access the admin panel, visit: http://127.0.0.1:8000/admin/
 


## Author

- **Name:** Darpan Anjanay
- **GitHub:** https://github.com/Darpan-Anjanay/


## Screenshots

### Landing Page
![Landing Page](/screenshots/landing.png)

### Request Access Page
![Request Access Page](/screenshots/requestaccess.png)

### Login Page
![Login Page](/screenshots/login.png)

### Sales Dashboard
![Sales Dashboard](/screenshots/sales1.png)

![Sales Dashboard](/screenshots/sales2.png)


### Receive Dashboard
![Receive Dashboard](/screenshots/receive.png)


### Inventory Dashboard
![ Inventory Dashboard](/screenshots/inventory.png)


### Profitability Dashboard
![ Profitability Dashboard](/screenshots/profit.png)


###  Shops Page
![ Shops Page](/screenshots/shops.png)

###  Items Page
![ Items Page](/screenshots/items.png)
