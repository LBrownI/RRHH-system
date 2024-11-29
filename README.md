# RRHH-system

This project is a **Flask-based HR management system** designed to streamline employee and organizational data management. It allows administrators to manage employee records, contracts, vacations, training, evaluations, remuneration details, and more. The application uses **SQLAlchemy** for efficient database interactions and employs HTML templates and CSS styling for the frontend, minimizing reliance on JavaScript.


---

## Features

- **Homepage**:  
  View all employees in the database and filter them by department, status, or other criteria for quick access.

- **Employee Page**:  
  Access detailed information for each employee in the database. From this page, you can edit employee details or add a new contract.

- **AFP Page**:  
  View and manage all pension funds, including associated discounts.

- **Health Plan Page**:  
  Explore all available public and private health plans, along with their details.

- **Company Page**:  
  View and manage all affiliated companies linked to the organization. Add new companies directly to the database from this page.

- **Remuneration Page**:  
  Access the complete history and details of employee compensations, with the ability to add records.

- **Contracts Page**:  
  View and manage all employee contracts. This page allows you to add new contracts to the database.

- **Vacation Page**:  
  View all recorded vacation data for employees and add new vacation entries as needed.

- **Training and Evaluation Page**:  
  Access all employee training and evaluation records. Add new records to the database directly from this page.


---

## Technologies Used

- **Backend**:
  - Python   
  - Flask
  - SQLAlchemy
- **Frontend**:
  - HTML
  - CSS (optional custom stylesheets)
  - JavaScript
- **Database**:
  - MySQL
- **Others**:
  - Docker
  - Microsoft Azure

---


## Installation and Setup

Follow one of the three methods below to set up the project:

---

### 1. **Connect to Azure Virtual Machine (VM)**

go to http://172.214.209.5:5000/

- BEWARE: This is 1 commit behind 
- Feature missing: add remuneration button on /remuneration page. To add a remuneration go manually to /add_remuneration
---

### 2. **Manual Setup (Old School)**

1. **Clone the repository**:  
   ```bash
   git clone https://github.com/LBrownI/RRHH-system.git
   cd RRHH-system
   ```

2. **Install Python and dependencies**:  
   - Install Python 3.12 or higher. (https://www.python.org/downloads/) 
   - Install dependencies (inside project folder):  
     ```bash
     pip install -r requirements.txt
     ```

3. **Set up the database**:  
   Initialize the database with SQLAlchemy models by running the setup script load_db.py (located on /project/setup/).  

4. **Run the application**:  
   Start the Flask development server (in folder project/backend/):  
   ```bash
   python app.py
   ```

5. **Access the application**:  
   Open a browser and navigate to `http://localhost:5000`.

---

Choose the method that best suits your environment or deployment needs.


