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

config = {
    'host': 'localhost',
    'database_name': 'hr',
    'user': 'root',
    'password': 'rootpass'  
    }

engine = create_engine(f'mysql+pymysql://{config["user"]}:{config["password"]}@{config["host"]}/{config["database_name"]}', echo=True)
# engine = create_engine(f'mysql+pymysql://{config["user"]}:{config["password"]}@{config["host"]}', echo=True)

Base = declarative_base()

Session = sessionmaker(bind=engine)
session = Session()

def get_contract_by_employee_id(session, employee_id):
    """Get the contract associated with a specific employee."""
    try:
        contract = session.query(Contract).filter_by(employee_id=employee_id).first()
        return contract
    except SQLAlchemyError as e:
        print(f'Error retrieving contract for employee {employee_id}: {e}')
        return None



def search_employee_by_name_or_rut(search_query, session):
    """Search an employee by name or RUT with flexible matching."""
    search_terms = search_query.split()
    if len(search_terms) == 1:
        term = f"%{search_terms[0]}%"
        result = session.query(Employee).filter(
            (Employee.first_name.like(term)) | 
            (Employee.last_name.like(term)) | 
            (Employee.rut == search_query)
        ).first()
    elif len(search_terms) == 2:
        result = session.query(Employee).filter(
            (Employee.first_name.like(f"%{search_terms[0]}%")) &
            (Employee.last_name.like(f"%{search_terms[1]}%"))
        ).first()
    else:
        result = None
    return result

def get_job_positions(session):
    """Get all job positions."""
    return session.query(JobPosition).all()

def get_departments(session):
    """Get all departments."""
    return session.query(Department).all()

def get_filtered_employees(session, job_position_id=None, department_id=None):
    """Get employees filtered by job position and/or department."""
    query = (
        session.query(Employee.id, Employee.rut, Employee.first_name, Employee.last_name, JobPosition.name.label('position_name'), Department.name.label('department_name'))
        .outerjoin(EmployeePosition, Employee.id == EmployeePosition.employee_id)
        .outerjoin(JobPosition, EmployeePosition.position_id == JobPosition.id)
        .outerjoin(Department, JobPosition.department_id == Department.id)
    )

    # Apply filters if provided
    if job_position_id:
        query = query.filter(JobPosition.id == job_position_id)
    if department_id:
        query = query.filter(Department.id == department_id)
    
    return [
        {
            "id": emp.id,
            "rut": emp.rut,
            "first_name": emp.first_name,
            "last_name": emp.last_name,
            "position": emp.position_name or "Sin posición",
            "department": emp.department_name or "Sin departamento",
        }
        for emp in query.all()
    ]

def aditional_info(session, employee_id):
    """Get additional information about an employee including net amount, health plan, nationality, birth date, start date, salary, and AFP."""
    try:
        info = session.query(
            Employee.nationality,
            Employee.birth_date,
            Employee.start_date,
            Employee.salary,
            Remuneration.net_amount,
            HealthPlan.name.label('health_plan'),
            AFP.name.label('afp_name')
        ).select_from(Employee) \
        .outerjoin(Remuneration, Employee.id == Remuneration.employee_id) \
        .outerjoin(HealthPlan, Remuneration.health_plan_id == HealthPlan.id) \
        .outerjoin(AFP, Remuneration.afp_id == AFP.id) \
        .filter(Employee.id == employee_id).first()  # Changed to first()

        if info:
            today = datetime.today().date()
            age = (today.year - info[1].year) if info[1] else None
            days_since_start = (today - info[2]).days if info[2] else None
            net_amount = int(info[4]) if isinstance(info[4], Decimal) else info[4]

            return {
                'nationality': info[0],
                'birth_date': info[1],
                'age': age,
                'start_date': info[2],
                'days_since_start': days_since_start,
                'salary': info[3],
                'net_amount': net_amount,
                'health_plan': info[5] or "No health plan registered",
                'afp_name': info[6] or "No AFP registered"
            }
    except Exception as e:
        print(f'Error in aditional_info: {e}')
    return None

def general_info(session, employee_id):
    """Get basic information about an employee."""
    try:
        info = session.query(Employee.first_name, Employee.last_name, Employee.email, Employee.phone, Employee.rut, JobPosition.name, Employee.active_employee) \
            .outerjoin(EmployeePosition, Employee.id == EmployeePosition.employee_id) \
            .outerjoin(JobPosition, EmployeePosition.position_id == JobPosition.id) \
            .filter(Employee.id == employee_id).first()
        return info
    except Exception as e:
        print(f'Error in general_info: {e}')
    return None

def all_employees(session):
    """Retrieve all employees with their rut, first name, last name, position, and department"""
    try:
        query = session.query(
            Employee.id, Employee.rut, Employee.first_name, Employee.last_name,
            JobPosition.name.label('position_name'), Department.name.label('department_name')
        ).outerjoin(EmployeePosition, Employee.id == EmployeePosition.employee_id) \
         .outerjoin(JobPosition, EmployeePosition.position_id == JobPosition.id) \
         .outerjoin(Department, JobPosition.department_id == Department.id)
        return [
            {
                "id": row.id,
                "rut": row.rut,
                "first_name": row.first_name,
                "last_name": row.last_name,
                "position": row.position_name or "Sin posición",
                "department": row.department_name or "Sin departamento",
            }
            for row in query.all()
        ]
    except Exception as e:
        print(f'Error in all_employees: {e}')
    return []

def get_employee_name_by_rut(employee_rut):
    """Fetch employee name by RUT"""
    session = Session()
    try:
        employee = session.query(Employee).filter_by(rut=employee_rut).first()  # Buscar por RUT
        if employee:
            return employee.first_name + ' ' + employee.last_name
        else:
            return None
    finally:
        session.close()


def add_contract(session, contract_data):
    """Add a contract for an employee."""
    try:
        # Fetch the Employee using employee_rut
        employee = session.query(Employee).filter_by(rut=contract_data['employee_rut']).first()
        
        if not employee:
            return f"Employee with RUT {contract_data['employee_rut']} not found."

        # Fetch the position_id from the EmployeePosition table using employee.id
        employee_position = session.query(EmployeePosition).filter_by(employee_id=employee.id).first()
        if not employee_position:
            return f"Position for employee with RUT {contract_data['employee_rut']} not found."

        # Auto-complete position_id and registration_date
        contract_data['position_id'] = employee_position.position_id
        contract_data['employee_id'] = employee.id
        contract_data['registration_date'] = date.today()

        # Remove 'employee_rut' from contract_data as it is not a field in the Contract model
        contract_data.pop('employee_rut', None)

        # Create the Contract object and add it to the session
        contract = Contract(**contract_data)
        session.add(contract)
        session.commit()

        return "Contract added successfully."
    except SQLAlchemyError as e:
        session.rollback()
        return f"Error adding contract: {str(e)}"

def add_employee_to_db(session, employee_data):
    try:
        new_employee = Employee(
            rut=employee_data['rut'],
            first_name=employee_data['first_name'],
            last_name=employee_data['last_name'],
            birth_date=employee_data['birth_date'],
            start_date=employee_data['start_date'],
            email=employee_data['email'],
            phone=employee_data['phone'],
            salary=employee_data['salary'],
            nationality=employee_data['nationality'],
            afp_id=employee_data['afp'],
            health_plan_id=employee_data['healthplan'],
        )
        session.add(new_employee)
        session.commit()
        return "Empleado agregado exitosamente"
    except Exception as e:
        session.rollback()
        return f"Error al agregar el empleado: {e}"

    

def deactivate_employee(session, employee_id):
    """Deactivate an employee by setting active_employee to False."""
    try:
        employee = session.query(Employee).filter_by(id=employee_id).first()
        if employee:
            employee.active_employee = False
            session.commit()
            return "Employee deactivated successfully."
        return f"Employee with ID {employee_id} not found."
    except SQLAlchemyError as e:
        session.rollback()
        return f"Error deactivating employee: {str(e)}"


def add_training(session, training_data):
    """Add a training record."""
    try:
        session.add(Training(**training_data))
        session.commit()
        return "Training added successfully."
    except SQLAlchemyError as e:
        session.rollback()  # Rollback the transaction on error
        return f"Error adding training: {str(e)}"

def add_evaluation(session, evaluation_data):
    """Add an evaluation for an employee."""
    try:
        # Get the evaluation factor (numeric grade)
        evaluation_factor = float(evaluation_data.get('evaluation_factor', 0))

        # Add the rating to the evaluation data
        rating = (
             # Determine rating based on the evaluation factor ranges
            "Excellent" if evaluation_factor == 7 else
            "Very Good" if 6.5 <= evaluation_factor < 7 else
            "Good" if 6 <= evaluation_factor < 6.4 else
            "Satisfactory" if 5 <= evaluation_factor < 6 else
            "Fair" if 4 >= evaluation_factor > 5 else "Deficient"
        )
        evaluation_data['rating'] = rating
        session.add(Evaluation(**evaluation_data))
        session.commit()
        return "Evaluation added successfully."
    except SQLAlchemyError as e:
        session.rollback()
        return f"Error adding evaluation: {str(e)}"

def get_all_evaluations(session):
    """Get all evaluations with employee details."""
    evaluations = session.query(Evaluation, Employee).join(Employee, Evaluation.employee_id == Employee.id).all()
    return [
        {
            'evaluation_date': eval.evaluation_date,
            'evaluator': eval.evaluator,
            'evaluation_factor': eval.evaluation_factor,
            'rating': eval.rating,
            'comments': eval.comments,
            'employee_name': f"{employee.first_name} {employee.last_name}"
        }
        for eval, employee in evaluations
    ]

def get_all_trainings(session):
    """Get all trainings with employee details."""
    trainings = session.query(Training, Employee).join(Employee, Training.employee_id == Employee.id).all()
    return [
        {
            'training_date': train.training_date,
            'course': train.course,
            'score': train.score,
            'institution': train.institution,
            'comments': train.comments,
            'employee_name': f"{employee.first_name} {employee.last_name}"  # Add employee's full name
        }
        for train, employee in trainings
    ]

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

def all_companies(session):
    """Retrieve all companies and their data."""
    try:
        companies = session.query(Company).all()
        return [
            {
                'rut': company.rut,
                'name': company.name,
                'address': company.address,
                'phone': company.phone,
                'industry': company.industry
            }
            for company in companies
        ]
    except Exception as e:
        print(f'Error in all_companies: {e}')
    return []

def all_afps(session):
    """Retrieve all afps and their data."""
    try:
        afps = session.query(AFP).all()
        return [
            {
                'id': afp.id,
                'name': afp.name,
                'commission_percentage': afp.commission_percentage,
            }
            for afp in afps
        ]
    except Exception as e:
        print(f'Error in all_companies: {e}')
    return []

def all_contracts(session):
    """Retrieve all contracts and their employee data."""
    try:
        contracts = session.query(Contract, Employee, JobPosition).join(Employee, Contract.employee_id == Employee.id).join(JobPosition, Contract.position_id == JobPosition.id).all()
        return [
            {
                'id': contract.id,
                'employee': f"{employee.first_name} {employee.last_name}",
                'contract_type': contract.contract_type,
                'start_date': contract.start_date,
                'end_date': contract.end_date,
                'classification': contract.classification,
                'position': position.name,
                'registration_date': contract.registration_date,
            }
            for contract, employee, position in contracts
        ]
    except Exception as e:
        print(f'Error in all_contracts: {e}')
    return []

def all_vacations(session):
    """Retrieve all vacations and their employee data."""
    vacations = (
        session.query(
            Vacation.id,
            (Employee.first_name + " " + Employee.last_name).label("name"),
            Vacation.start_date,
            Vacation.end_date,
            Vacation.days_taken,
            Vacation.accumulated_days,
            Vacation.long_service_employee
        )
        .join(Employee, Vacation.employee_id == Employee.id)
        .all()
    )
    return vacations

