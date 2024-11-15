import os
from decimal import Decimal
from sqlalchemy import create_engine, text, func, update
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from datetime import date, datetime
from tables import *

# Load the MySQL root password from environment variables
mysql_root_password = os.getenv('MYSQL_ROOT_PASSWORD', 'default_root_pass')  # Fallback in case the env variable isn't set
# You can set it up by doing: export MYSQL_ROOT_PASSWORD=your_secure_password

config = {
    'host': 'localhost',
    'database_name': 'hr',
    'user': 'root',
    'password': mysql_root_password 
    }

engine = create_engine(f'mysql+pymysql://{config["user"]}:{config["password"]}@{config["host"]}/{config["database_name"]}', echo=True)
# engine = create_engine(f'mysql+pymysql://{config["user"]}:{config["password"]}@{config["host"]}', echo=True)

Base = declarative_base()

Session = sessionmaker(bind=engine)
session = Session()


def add_remuneration(session, remuneration_data):
    """Add a remuneration for an employee."""
    try:
        # Fetch the Employee using employee_id
        employee = session.query(Employee).filter_by(id=remuneration_data['employee_id']).first()
        
        if not employee:
            return f"Employee with ID {remuneration_data['employee_id']} not found."
        
        # Auto-complete afp_id and health_plan_id from Employee's AFP and HealthPlan
        remuneration_data['afp_id'] = employee.afp_id
        remuneration_data['health_plan_id'] = employee.health_plan_id

        # Ensure numeric fields are converted to float
        gross_amount = float(remuneration_data.get('gross_amount', 0))
        tax = float(remuneration_data.get('tax', 0))
        deductions = float(remuneration_data.get('deductions', 0))
        bonus = float(remuneration_data.get('bonus', 0))
        welfare_contribution = float(remuneration_data.get('welfare_contribution', 0))
        net_amount = float(remuneration_data.get('net_amount', 0))

        # Create new Remuneration record
        remuneration = Remuneration(
            employee_id=remuneration_data['employee_id'],
            afp_id=remuneration_data['afp_id'],
            health_plan_id=remuneration_data['health_plan_id'],
            gross_amount=gross_amount,
            tax=tax,
            deductions=deductions,
            bonus=bonus,
            welfare_contribution=welfare_contribution,
            net_amount=net_amount
        )

        # Add to session and commit
        session.add(remuneration)
        session.commit()
        return "Remuneration added successfully."

    except SQLAlchemyError as e:
        session.rollback()
        return f"Error adding remuneration: {str(e)}"
    
def update_employee(session, data):
    try:
        # Check if the employee exists
        employee = session.query(Employee).filter(Employee.id == data['employee_id']).first()
        
        if employee:
            # Update the first name
            employee.first_name = data['first_name']
            employee.last_name = data['last_name']
            employee.email = data['email']
            employee.phone = data['phone']
            employee.rut = data['rut']
            session.commit()
            print(f"Employee {data['employee_id']}'s first name updated to '{data['first_name']}'.")
        else:
            print(f"No employee found with ID {data['employee_id']}")
    except Exception as e:
        session.rollback()  # Roll back the session in case of error
        print(f'Error updating employee: {e}')
    finally:
        session.close()
    return None


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

def add_vacation_to_db(session, vacation_data):
    """Adds a vacation for an employee to the database."""
    try:
        # Convert dates from string to date objects
        start_date = datetime.strptime(vacation_data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(vacation_data['end_date'], '%Y-%m-%d').date()

        # Validate that start_date is before end_date
        if start_date > end_date:
            return False, "Start date must be before the end date!"

        # Fetch the employee
        employee = session.query(Employee).filter_by(id=vacation_data['employee_id']).first()
        if not employee:
            return False, "Employee not found!"

        # Check employee's years of service
        today = datetime.now().date()
        years_of_service = (today - employee.start_date).days // 365

        # Automatically add vacation days based on years of service
        if years_of_service >= 1:
            if employee.long_service_employee:
                employee.accumulated_days += 20
            else:
                employee.accumulated_days += 15
            session.commit()

        # Check if requested vacation exceeds accumulated days
        requested_days = (end_date - start_date).days + 1
        if requested_days > employee.accumulated_days:
            return False, "Insufficient vacation days!"

        # Update accumulated days
        employee.accumulated_days -= requested_days

        # Create a new Vacation entry
        new_vacation = Vacation(
            employee_id=vacation_data['employee_id'],
            start_date=start_date,
            end_date=end_date,
            days_taken=requested_days,
            accumulated_days=employee.accumulated_days,
            long_service_employee=employee.long_service_employee
        )
        session.add(new_vacation)
        session.commit()

        return True, "Vacation added successfully!"
    except Exception as e:
        session.rollback()
        return False, str(e)
