from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from load_db import Session, Vacaciones, Colaborador

def add_vacation_logic(colaborador_id, fecha_inicio_str, fecha_termino_str):
    session = Session()
    message = ""
    
    try:
        # Convert string dates to datetime objects
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        fecha_termino = datetime.strptime(fecha_termino_str, '%Y-%m-%d').date()

        # Ensure the start date is before the end date
        if fecha_inicio > fecha_termino:
            return False, "Start date must be before the end date!"

        # Query the collaborator
        colaborador = session.query(Colaborador).filter_by(id=colaborador_id).first()
        
        if not colaborador:
            return False, "Colaborador not found!"

        # Check if the collaborator is a long-term employee (15+ years)
        today = datetime.now().date()
        years_of_service = (today - colaborador.fecha_ingreso).days // 365  # Calculate years of service

        # Automatically add vacation days if a year has passed since last addition
        if years_of_service >= 1:
            if colaborador.colaborador_antiguo: 
                colaborador.dias_acumulados += 20  
            else:
                colaborador.dias_acumulados += 15  
            session.commit() 

        # Calculate the number of vacation days
        dias_acumulados = colaborador.dias_acumulados  # Assuming this field exists in Colaborador

        # Check if the vacation dates exceed the accumulated days
        if exceeds_accumulated_days(fecha_inicio, fecha_termino, dias_acumulados):
            return False, "Insufficient vacation days!"

        # Calculate the number of days taken
        dias_tomados = (fecha_termino - fecha_inicio).days + 1  # Include the start day
        
        # Update the accumulated days
        updated_dias_acumulados = dias_acumulados - dias_tomados
        
        # If all checks pass, create a new Vacaciones entry
        new_vacation = Vacaciones(
            colaborador_id=colaborador_id,
            fecha_inicio=fecha_inicio,
            fecha_termino=fecha_termino,
            dias_tomados=dias_tomados,
            dias_acumulados=updated_dias_acumulados,
            colaborador_antiguo=colaborador.colaborador_antiguo
        )
        session.add(new_vacation)
        session.commit()
        
        return True, "Vacation added!"
    except Exception as e:
        session.rollback()  # Rollback in case of error
        return False, str(e)
    finally:
        session.close()

def exceeds_accumulated_days(start_date, end_date, dias_acumulados):
    # Calculate the number of days requested
    requested_days = (end_date - start_date).days + 1  # Include the start day
    return requested_days > dias_acumulados
