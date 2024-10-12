from sqlalchemy.orm import Session
from tables import Contract, Employee
from datetime import date

# THIS db_opertions.py IS INTENDED FOR RETRIEVING DATA FROM THE DATABASE TO SHOW THE USER,
# OR THE OTHER WAY AROUND, GETTING DATA FROM THE USER TO INSERT INTO THE DATABASE.

# Inserts a new 'Contract' into the database, ensuring mandatory fields are populated (no null allowed).
def add_contract(session: Session, contract_data: dict):

    # Fetch the Colaborador to get the departamento_id
    employee = session.query(Employee).get(contract_data['emnployee_id'])
    
    if not employee:
        return f"Employee with ID {contract_data['emnployee_id']} not found."

    # Auto-complete department_id based on colaborador
    contract_data['department_id'] = employee.department_id

    # Auto-complete registration_date with the current date
    contract_data['registration_date'] = date.today()


    contract = Contract(**contract_data)
    session.add(contract)
    session.commit()
    
    return f"Contract added successfully."

