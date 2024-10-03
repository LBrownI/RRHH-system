from sqlalchemy.orm import Session
from load_db import Contrato
from datetime import date

# THIS db_opertions.py IS INTENDED FOR RETRIEVING DATA FROM THE DATABASE TO SHOW THE USER,
# OR THE OTHER WAY AROUND, GETTING DATA FROM THE USER TO INSERT INTO THE DATABASE.

# Inserts a new 'Contrato' into the database, ensuring mandatory fields are populated (no null allowed).
def add_contrato(session: Session, contrato_data: dict):

    # Fetch the Colaborador to get the departamento_id
    colaborador = session.query(Colaborador).get(contrato_data['colaborador_id'])
    
    if not colaborador:
        return f"Colaborador with ID {contrato_data['colaborador_id']} not found."

    # Auto-complete departamento_id based on colaborador
    contrato_data['departamento_id'] = colaborador.departamento_id

    # Auto-complete fecha_registro with the current date
    contrato_data['fecha_registro'] = date.today()


    contrato = Contrato(**contrato_data)
    session.add(contrato)
    session.commit()
    
    return f"Contrato added successfully."


