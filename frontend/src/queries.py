import os
from decimal import Decimal
from sqlalchemy import create_engine, text, Column, Integer, String, ForeignKey, DECIMAL, Date, Text, Boolean
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from tables import Employee, EmployeePosition, JobPosition, Remuneration, HealthPlan, Company, Contract, Training, Evaluation
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

def aditional_info(employee_id_to_find: int):
    """Get net amount and health plan of an employee"""
    print('\n--- Running query aditional_info ---')
    try:
        info = session.query(Remuneration.net_amount, HealthPlan.name).select_from(Employee) \
            .join(Remuneration, Employee.id == Remuneration.employee_id) \
            .join(HealthPlan, Remuneration.health_plan_id == HealthPlan.id) \
            .filter(Employee.id == employee_id_to_find).first()  # Changed to first()
        
        if info:
            net_amount = int(info[0]) if isinstance(info[0], Decimal) else info[0]
            health_plan = info[1] if info[1] else "No health plan registered"
            return net_amount, health_plan
        else:
            return None, "No additional info available"
    except Exception as e:
        print(f'Error in query aditional_info: {e}')
        return None, "Error fetching additional info"

def general_info(employee_id: int):
    """Get first name, last name, phone, rut and position of an employee"""
    print('\n--- Running query general_info ---')
    try:
        info = session.query(Employee.first_name, Employee.last_name, Employee.phone, Employee.rut, JobPosition.name) \
            .join(EmployeePosition, Employee.id == EmployeePosition.employee_id) \
            .join(JobPosition, EmployeePosition.position_id == JobPosition.id) \
            .filter(Employee.id == employee_id).first()  # Changed to first()

        if info:
            return info
        else:
            return None
    except Exception as e:
        print(f'Error in query general_info: {e}')
        return None

# test = aditional_info(1)
# print(test)
def all_employees(session):
    """Select all the data from the Employee table."""
    print('\n--- Running query_1 ---')
    session = Session()
    try:
        # Query the Employee table using SQLAlchemy's session.query
        employees = session.query(Employee).all()
        
        # Create a list of dictionaries to store the employee data
        employee_list = []
        for employee in employees:
            employee_list.append({
                'id': employee.id,
                'rut': employee.rut,
                'first_name': employee.first_name,
                'last_name': employee.last_name
            })
        
        if not employee_list:
            print("No employees found.")
        else:
            print(f"Employees found: {employee_list}")
        
        return employee_list

    except Exception as e:
        print(f'Error in query_1: {e}')
        return []  # Return an empty list if there's an error
    finally:
        session.close()


def add_contract(session, contract_data):
    # Fetch the Employee to get the position_id
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

def add_training(session, training_data):
    try:
        training = Training(**training_data)
        session.add(training)
        session.commit()
        return "Training added successfully."
    except SQLAlchemyError as e:
        session.rollback()  # Rollback the transaction on error
        return f"An error occurred while adding training: {str(e)}"
    finally:
        session.close()  # Ensure session is closed

def add_evaluation(session, evaluation_data):
    try:
        # Get the evaluation factor (numeric grade)
        evaluation_factor = float(evaluation_data.get('evaluation_factor', 0))
        
        # Initialize the rating variable
        rating = ""
        
        # Determine rating based on the evaluation factor ranges
        if evaluation_factor == 7:
            rating = "Excellent"
        elif 6.5 <= evaluation_factor < 7:
            rating = "Very Good"
        elif 6 <= evaluation_factor < 6.4:
            rating = "Good"
        elif 5 <= evaluation_factor < 6:
            rating = "Satisfactory"
        elif 4 >= evaluation_factor > 5:
            rating = "Fair"
        else:
            rating = "Deficient"  # If it's below 4.0

        # Add the rating to the evaluation data
        evaluation_data['rating'] = rating

        # Create the evaluation record and add to the database
        evaluation = Evaluation(**evaluation_data)
        session.add(evaluation)
        session.commit()

        return "Evaluation added successfully."

    except SQLAlchemyError as e:
        session.rollback()  # Rollback the transaction on error
        return f"An error occurred while adding evaluation: {str(e)}"
    finally:
        session.close()  # Ensure session is closed

def get_all_evaluations(session):
    # Perform a join with the Employee table to get the first name and last name
    evaluations = session.query(Evaluation, Employee).join(Employee, Evaluation.employee_id == Employee.id).all()

    # Prepare a list of evaluations with employee details
    evals_with_employee = []
    for evaluation, employee in evaluations:
        eval_with_name = {
            'evaluation_date': evaluation.evaluation_date,
            'evaluator': evaluation.evaluator,
            'evaluation_factor': evaluation.evaluation_factor,
            'rating': evaluation.rating,
            'comments': evaluation.comments,
            'employee_name': f"{employee.first_name} {employee.last_name}"  # Add employee's full name
        }
        evals_with_employee.append(eval_with_name)

    return evals_with_employee

def get_all_trainings(session):
    # Perform a join with the Employee table to get the first name and last name
    trainings = session.query(Training, Employee).join(Employee, Training.employee_id == Employee.id).all()

    # Prepare a list of trainings with employee details
    trainings_with_employee = []
    for training, employee in trainings:
        training_with_name = {
            'training_date': training.training_date,
            'course': training.course,
            'score': training.score,
            'institution': training.institution,
            'comments': training.comments,
            'employee_name': f"{employee.first_name} {employee.last_name}"  # Add employee's full name
        }
        trainings_with_employee.append(training_with_name)

    return trainings_with_employee

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