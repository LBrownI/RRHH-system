import os
from sqlalchemy import create_engine, text, Column, Integer, String, ForeignKey, DECIMAL, Date, Text, Boolean
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from tables import Employee, EmployeePosition, JobPosition
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
    """Select the first and last name of the Employee table"""
    print('\n--- Running query_1 ---')
    try:
        info = session.query(Employee.first_name, Employee.last_name, Employee.phone, Employee.rut, JobPosition.name).join(EmployeePosition, Employee.id == EmployeePosition.employee_id).join(JobPosition, EmployeePosition.position_id == JobPosition.id).filter(Employee.id == employee_id).all()
        Employee_info = []
        for i in info:
            for j in i:
                Employee_info.append(j)
        return Employee_info
    except Exception as e:
        print(f'Error in query_2: {e}')

# test = general_info(1)
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
