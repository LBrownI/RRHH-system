from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from tables import engine, Vacation, Employee

# Create a session to interact with the database
Session = sessionmaker(bind=engine)

def add_vacation_logic(employee_id, start_date_str, end_date_str):
    session = Session()
    message = ""
    
    try:
        # Convert string dates to datetime objects
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        # Ensure the start date is before the end date
        if start_date > end_date:
            return False, "Start date must be before the end date!"

        # Query the employee
        employee = session.query(Employee).filter_by(id=employee_id).first()
        
        if not employee:
            return False, "Employee not found!"

        # Check if the employee is a long-term employee (15+ years)
        today = datetime.now().date()
        years_of_service = (today - employee.start_date).days // 365  # Calculate years of service

        # Automatically add vacation days if a year has passed since last addition
        if years_of_service >= 1:
            if employee.long_service_employee: 
                employee.accumulated_days += 20  
            else:
                employee.accumulated_days += 15  
            session.commit() 

        # Calculate the number of vacation days
        accumulated_days = employee.accumulated_days  # Assuming this field exists in Employee

        # Check if the vacation dates exceed the accumulated days
        if exceeds_accumulated_days(start_date, end_date, accumulated_days):
            return False, "Insufficient vacation days!"

        # Calculate the number of days taken
        days_taken = (end_date - start_date).days + 1  # Include the start day
        
        # Update the accumulated days
        updated_accumulated_days = accumulated_days - days_taken
        
        # If all checks pass, create a new Vacation entry
        new_vacation = Vacation(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            days_taken=days_taken,
            accumulated_days=updated_accumulated_days,
            long_service_employee=employee.long_service_employee
        )
        session.add(new_vacation)
        session.commit()
        
        return True, "Vacation added!"
    except Exception as e:
        session.rollback()  # Rollback in case of error
        return False, str(e)
    finally:
        session.close()

def exceeds_accumulated_days(start_date, end_date, accumulated_days):
    # Calculate the number of days requested
    requested_days = (end_date - start_date).days + 1  # Include the start day
    return requested_days > accumulated_days
