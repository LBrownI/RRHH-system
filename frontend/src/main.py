from flask import Flask, render_template, request, redirect, url_for, flash
from queries import *

app = Flask(__name__)
app.secret_key = 'magickey'


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
        the page employee without the employee_id of someone will not work.
        if there is no employee with the given id, or with enough info, the page will fail (e.g. if you put id 10 it will fail, despite 
        existing an employee with the id 10. This is because that employee doesn't have a record indicating his health_plan or simiar).
    # TODO:
        fix list index out of range (redirect to a page with a message or similar)
    """
    employee_id = request.args.get('employee_id', 'Employee Id')
    gi = general_info(employee_id)
    ad = aditional_info(employee_id)
    return render_template('employee.html', first_name=gi[0], last_name=gi[1], phone=gi[2], rut=gi[3], position=gi[4], net_amount=ad[0], health_plan=ad[1])

@app.route('/companies')
def show_companies():
    companies = all_companies()
    return render_template('companies.html', companies=companies)

# Route for the option of adding a new "Contract"
# WORKING BUT redirects to /add_contract instead of staying on the colaborator page.
@app.route('/add_contract', methods=['GET', 'POST'])
def add_contract_page():
    if request.method == 'POST':
        # Gather form data
        contract_data = {
            'employee_id': request.form['employee_id'],
            'contract_type': request.form['contract_type'],
            'start_date': request.form['start_date'],
            'end_date': request.form['end_date'],
            'classification': request.form['classification']
        }

        # Fetch the session and call the add_contract function
        session = Session()
        message = add_contract(session, contract_data)
        flash(message)
        
        return redirect(url_for('add_contract_page'))

    return render_template('add_contract.html')

@app.route('/train-eval')
def train_eval():
    # Start a session
    session = Session()

    # Query for evaluations and trainings
    evaluations = get_all_evaluations(session)
    trainings = get_all_trainings(session)
    
    # Close the session
    session.close()

    return render_template('train_eval.html', evaluations=evaluations, trainings=trainings)

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

@app.route('/get_employee_name/<int:employee_id>', methods=['GET'])
def get_employee_name(employee_id):
    employee_name = get_employee_name_by_id(employee_id)
    if employee_name:
        return employee_name  # Return the name as plain text
    else:
        return "Does not exist", 404

if __name__ == '__main__':
    app.run(debug=True)