from flask import Flask, render_template, request, redirect, url_for, flash
from queries import *
# from sqlalchemy.orm import Session, sessionmaker
# from tables import engine, Colaborador
# from db_operations import add_contrato
# from vacation_logic import add_vacation_logic

app = Flask(__name__)
app.secret_key = 'magickey'

# Set up session for SQLAlchemy (Commented out for now)
# Session = sessionmaker(bind=engine)
# session = Session()

# Route for login page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Logic to validate user
        # For example, checking if user and password are correct.
        
        # REVISE: https://webdamn.com/login-and-registration-with-python-flask-mysql/cl

        # If validation is correct, redirects to homepage (index.html)
        if username == 'user' and password == 'pass':  # Validación simple de ejemplo
            return redirect(url_for('menu'))
        else:
            return render_template('login.html', error="Usuario o contraseña incorrectos")
    return render_template('login.html')

# Route for menu page (homepage)
@app.route('/menu')
def menu():
    employees = all_employees()
    return render_template('index.html', employees = employees)

# Route for the employee (optional)
@app.route('/employee')
def user():
    """
    gets the employee_id from the URL and returns the info of the employee
    # example:
        http://127.0.0.1:5000/employee?employee_id=1
        try changing the id number to see the different employees!
    # NOTE:
        the page employee without the employee_id of the employee will not work
    # TODO:
        fix list index out of range when there is no employee with the given id (redirect to a page with a message or similar)
    """
    employee_id = request.args.get('employee_id', 'Employee Id')
    gi = general_info(employee_id)
    ad = aditional_info(employee_id)
    return render_template('employee.html', first_name=gi[0], last_name=gi[1], phone=gi[2], rut=gi[3], position=gi[4], net_amount=ad[0], health_plan=ad[1])

# Route for the option of adding a new "Contrato" (mocked functionality)
@app.route('/add-contrato', methods=['GET', 'POST'])
def add_contrato_page():
    if request.method == 'POST':
        # Gather form data
        contract_data = {
            'employee_id': request.form['employee_id'],
            'contract_type': request.form['contract_type'],
            'start_date': request.form['start_date'],
            'end_date': request.form['end_date'],
            'classification': request.form['classification']
        }
        
        # Mock message for adding contrato
        message = "Mock: Contract added successfully!"
        flash(message)

        # Original setup
        """
         Call function from db_operations.py
         message = add_contract(session, contract_data)
         flash(message)
        """
        return redirect(url_for('add_contrato_page'))

    return render_template('add_contrato.html')

# Route for register vacation page
@app.route('/register_vacation')
def register_vacation():
    return render_template('register_vacation.html')  # Render the HTML form

# Route for adding vacation (no database interaction)
@app.route('/add_vacation', methods=['POST'])
def add_vacation():
    employee_id = request.form.get('employee_id')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    
    # Mock success and message (bypassing actual vacation logic)
    success = True
    message = "Mock: Vacation added!"

    # Original setup
    """  
    Call vacation logic from vacation_logic.py
    success, message = add_vacation_logic(int(employee_id), start_date, end_date)
    """ 
    if success:
        flash('Vacation registered successfully!', 'success')
    else:
        flash(f'Error: {message}', 'danger')
    
    return redirect('/register_vacation')

# Part of the /add-contrato and /register_vacation page for showing colaborador name to the side of the id (mocked functionality)
@app.route('/get_employee_name/<int:employee_id>', methods=['GET'])
def get_employee_name(employee_id):

    # Mocked employee lookup
    employee = {'name': 'Mock Employee'} if employee_id == 1 else None

    # Original setup
    """
    employee = session.query(Employee).get(employee_id)  # Use SQLAlchemy to fetch the employee
    """
    if employee:
        return employee['name']
    else:
        return "Does not exist", 404

if __name__ == '__main__':
    app.run(debug=True)