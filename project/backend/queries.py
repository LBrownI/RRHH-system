import os
from decimal import Decimal
from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from datetime import date, datetime
from werkzeug.security import generate_password_hash, check_password_hash
from tables import *

# Load the MySQL root password from environment variables
mysql_root_password = os.getenv('MYSQL_ROOT_PASSWORD', 'default_root_pass')  # Fallback in case the env variable isn't set
# You can set it up by doing: export MYSQL_ROOT_PASSWORD=your_secure_password

config = {'host': 'localhost',
          'database_name': 'hr',
          'user': 'root',
          'password': mysql_root_password}

engine = create_engine(f'mysql+pymysql://{config["user"]}:{config["password"]}@{config["host"]}/{config["database_name"]}', echo=True)
# engine = create_engine(f'mysql+pymysql://{config["user"]}:{config["password"]}@{config["host"]}', echo=True)

Base = declarative_base()

Session = sessionmaker(bind=engine)
session = Session()

def aditional_info(employee_id_to_find: int):
    """Get additional information about an employee including net amount, health plan, nationality, birth date, start date, salary, and AFP."""
    print('\n--- Running query aditional_info ---')
    try:
        # Perform the query to get all the additional information
        info = session.query(
            Employee.nationality,
            Employee.birth_date,
            Employee.start_date,
            Employee.salary,
            Remuneration.net_amount,
            HealthPlan.name.label('health_plan'),
            AFP.name.label('afp_name')
        ).select_from(Employee) \
        .join(Remuneration, Employee.id == Remuneration.employee_id) \
        .join(HealthPlan, Remuneration.health_plan_id == HealthPlan.id) \
        .join(AFP, Remuneration.afp_id == AFP.id) \
        .filter(Employee.id == employee_id_to_find).first()  # Changed to first()

        if info:
            # Extract the information
            nationality = info[0]
            birth_date = info[1]
            start_date = info[2]
            salary = info[3]
            net_amount = int(info[4]) if isinstance(info[4], Decimal) else info[4]
            health_plan = info[5] if info[5] else "No health plan registered"
            afp_name = info[6] if info[6] else "No AFP registered"

            # Calculate age
            age = None
            if birth_date:
                today = datetime.today().date()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

            # Calculate days since start date
            days_since_start = None
            if start_date:
                today = datetime.today().date()
                days_since_start = (today - start_date).days

            # Return the collected information
            return {
                'nationality': nationality,
                'birth_date': birth_date,
                'age': age,
                'start_date': start_date,
                'days_since_start': days_since_start,
                'salary': salary,
                'net_amount': net_amount,
                'health_plan': health_plan,
                'afp_name': afp_name
            }

        else:
            return None

    except Exception as e:
        print(f'Error in query aditional_info: {e}')
        return None

def general_info(employee_id: int):
    """Get first name, last name, phone, rut and position of an employee"""
    print('\n--- Running query general_info ---')
    try:
        info = session.query(Employee.first_name, Employee.last_name, Employee.email, Employee.phone, Employee.rut, JobPosition.name) \
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
    """Select all employees with their rut, first name, last name, position, and department"""
    print('\n--- Running all_employees query ---')
    try:
        # Consulta usando SQLAlchemy para obtener los empleados junto con su posición y departamento
        info = (
            session.query(Employee.id,Employee.rut, Employee.first_name, Employee.last_name, JobPosition.name.label('position_name'), Department.name.label('department_name')).
            outerjoin(EmployeePosition, Employee.id == EmployeePosition.employee_id).
            outerjoin(JobPosition, EmployeePosition.position_id == JobPosition.id).
            outerjoin(Department, JobPosition.department_id == Department.id).all()
        )

        
        # Crear una lista de diccionarios para cada empleado
        employees = [
            {
                "id": row.id,
                "rut": row.rut,
                "first_name": row.first_name,
                "last_name": row.last_name,
                "position": row.position_name if row.position_name else "Sin posición",
                "department": row.department_name if row.department_name else "Sin departamento",
            }
            for row in info
        ]
        
        return employees  # Agregar este return para asegurarse de que la función devuelve la lista de empleados
    except Exception as e:
        print(f'Error in all_employees query: {e}')
        return []  # Devolver una lista vacía en caso de error




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

def get_employees_by_department(department_id):
    """
    Fetches all employees who are in positions within a given department.
    """
    # Query the employees through the JobPosition and Department relationship
    employees = session.query(Employee).join(EmployeePosition).join(JobPosition).filter(JobPosition.department_id == department_id).all()

    return employees

def department_info(department_id):
    """
    Fetches department name and description by department ID.
    """
    # Query for the department name and description
    department = session.query(Department).filter(Department.id == department_id).first()

    if department:
        return department.name, department.description
    return None

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