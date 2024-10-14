import os
from decimal import Decimal
from sqlalchemy import create_engine, text, Column, Integer, String, ForeignKey, DECIMAL, Date, Text, Boolean
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from tables import Employee, EmployeePosition, JobPosition, Remuneration, HealthPlan, Company, Contract
# Load the MySQL root password from environment variables
mysql_root_password = os.getenv('MYSQL_ROOT_PASSWORD', 'default_root_pass')  # Fallback in case the env variable isn't set
# You can set it up by doing: export MYSQL_ROOT_PASSWORD=your_secure_password

config = {'host': 'localhost',
          'database_name': 'hr',
          'user': 'root',
          'password': mysql_root_password}

engine = create_engine(f'mysql+pymysql://{config["user"]}:{config["password"]}@{config["host"]}/{config["database_name"]}')
# engine = create_engine(f'mysql+pymysql://{config["user"]}:{config["password"]}@{config["host"]}', echo=True)

with engine.connect() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {config['database_name']}"))

Base = declarative_base()

Session = sessionmaker(bind=engine)
session = Session()

def general_info(employee_id: int):
    """Get first name, last name, phone, rut and position of an employee"""
    print('\n--- Running query general_info ---')
    try:
        info = session.query(Employee.first_name, Employee.last_name, Employee.phone, Employee.rut, JobPosition.name).join(EmployeePosition, Employee.id == EmployeePosition.employee_id).join(JobPosition, EmployeePosition.position_id == JobPosition.id).filter(Employee.id == employee_id).all()
        Employee_info = []
        for i in info:
            for j in i:
                Employee_info.append(j)
        return Employee_info
    except Exception as e:
        print(f'Error in query general_info: {e}')

def aditional_info(employee_id_to_find: int):
    """Get net amount and health plan of an employee"""
    print('\n--- Running query aditional_info ---')
    try:
        info = session.query(Remuneration.net_amount, HealthPlan.name).select_from(Employee).join(Remuneration, Employee.id == Remuneration.employee_id).join(HealthPlan, Remuneration.health_plan_id == HealthPlan.id).filter(Employee.id == employee_id_to_find).all()
        Employee_info = []
        for i in info:
            for j in i:
                if isinstance(j, Decimal):
                    Employee_info.append(int(j))
                else:
                    Employee_info.append(j)
        return Employee_info
    except Exception as e:
        print(f'Error in query aditional_info: {e}')

# test = aditional_info(1)
# print(test)
def all_employees():
    """Select all the data from the Employee table"""
    print('\n--- Running query_1 ---')
    try:
        with engine.connect() as conn:
            res = conn.execute(text(f"SELECT rut, first_name, last_name"))
            employees = []
            for row in res:
                employees.append({
                    'rut': row['rut'],
                    'first_name': row['name'],
                    'last_name': row['last_name']
                })
            print(employees)  # Para verificar los datos
            return employees
    except Exception as e:
        print(f'Error in query_1: {e}')


def add_contract(session, contract_data):
    # Fetch the Employee to get the department_id
    employee = session.query(Employee).get(contract_data['employee_id'])
    
    if not employee:
        return f"Employee with ID {contract_data['employee_id']} not found."

    # Fetch the position_id from the EmployeePosition table
    employee_position = session.query(EmployeePosition).filter_by(employee_id=contract_data['employee_id']).first()
    
    if not employee_position:
        return f"Position for employee with ID {contract_data['employee_id']} not found."
    
    # Auto-complete position_id based on EmployeePosition
    contract_data['position_id'] = employee_position.position_id

    # Auto-complete registration_date with the current date
    contract_data['registration_date'] = date.today()

    # Create the Contract object and add it to the session
    contract = Contract(**contract_data)
    session.add(contract)
    session.commit()
    
    return f"Contract added successfully."

def get_employee_name_by_id(employee_id):
    """Fetch employee name by ID"""
    session = Session()
    try:
        employee = session.query(Employee).get(employee_id)
        if employee:
            return employee.first_name + ' ' + employee.last_name
        else:
            return None
    finally:
        session.close()

def all_companies():
    """Select all the data from the Company table"""
    print('\n--- Running all_companies query ---') 
    try:
        companies = session.query(Company).all()
        result = []
        for company in companies:
            result.append({
                'rut': company.rut,
                'name': company.name,
                'address': company.address,
                'phone': company.phone,
                'industry': company.industry
            })
        print(result)  # Debug output to verify the data
        return result
    except Exception as e:
        print(f'Error in all_companies query: {e}')
    finally:
        session.close()