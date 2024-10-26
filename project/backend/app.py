import os
from flask import Flask, render_template, request, redirect, url_for, flash
from queries import *

app = Flask(
    __name__, 
    template_folder=os.path.join(os.getcwd(), 'project', 'frontend', 'src', 'templates'),
    static_folder=os.path.join(os.getcwd(), 'project', 'frontend', 'src', 'static')
)
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
            return redirect(url_for('homepage'))
        else:
            return render_template('login.html', error="Usuario o contraseña incorrectos")
    return render_template('login.html')

# Route for menu page (homepage)
@app.route('/homepage')
def homepage():
    job_position_id = request.args.get('job_position', type=int)
    department_id = request.args.get('department', type=int)

    # Get filtered employees
    employees = get_filtered_employees(session, job_position_id, department_id)
    
    # Fetch job positions and departments for the dropdown lists
    job_positions = get_job_positions(session)
    departments = get_departments(session)

    return render_template('index.html', employees=employees, job_positions=job_positions, departments=departments)



# Route for the employee (optional)
@app.route('/employee')
def user():
    """
    Gets the employee_id from the URL and returns the info of the employee.
    If certain data is missing, it will show a message on the page instead of redirecting.
    """
    employee_id = request.args.get('id')

    if not employee_id:
        # Show a message if no employee_id is provided
        return render_template('employee.html', error_message="No employee ID provided")

    # Retrieve general and additional information
    gi = general_info(employee_id)
    ad_info = aditional_info(employee_id)

    # Check if general info is missing
    if not gi:
        return render_template('employee.html', error_message="Employee not found")

    first_name, last_name, email, phone, rut, position = gi

    # Display missing info
    missing_info = []
    if not ad_info:
        missing_info.append("No additional info available")
    if not ad_info.get('net_amount'):
        missing_info.append("No net amount registered")
    if ad_info.get('health_plan') == "No health plan registered":
        missing_info.append("No health plan registered")

    # Pass the data to the template, including missing information
    return render_template(
        'employee.html',
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        rut=rut,
        position=position,
        nationality=ad_info.get('nationality', "Not registered"),
        birth_date=ad_info.get('birth_date', "Not registered"),
        age=ad_info.get('age', "Not available"),
        start_date=ad_info.get('start_date', "Not registered"),
        days_since_start=ad_info.get('days_since_start', "Not available"),
        salary=ad_info.get('salary', "Not registered"),
        net_amount=ad_info.get('net_amount', "Not registered"),
        health_plan=ad_info.get('health_plan', "Not registered"),
        afp_name=ad_info.get('afp_name', "Not registered"),
        missing_info=missing_info
    )

@app.route('/companies')
def show_companies():
    companies = all_companies()
    return render_template('companies.html', companies=companies)

# Route for the option of adding a new "Contract"
# WORKING BUT redirects to /add_contract instead of staying on the colaborator page.
@app.route('/add-contract', methods=['GET', 'POST'])
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
def eval_train():
    with Session() as session:
        evaluations = get_all_evaluations(session)
        trainings = get_all_trainings(session)
    return render_template('train_eval.html', evaluations=evaluations, trainings=trainings)

@app.route('/add-evaluation', methods=['GET', 'POST'])
def handle_add_evaluation():
    if request.method == 'POST':
        evaluation_data = {
            'employee_id': request.form['employee_id'],
            'evaluation_date': request.form['evaluation_date'],
            'evaluator': request.form['evaluator'],
            'evaluation_factor': request.form['evaluation_factor'],
            'rating': request.form['rating'],
            'comments': request.form['comments']
        }
        session = Session()
        result = add_evaluation(session, evaluation_data)
        flash(result)

        return redirect(url_for('train_eval'))
    
    return render_template('add_eval.html')

@app.route('/department')
def department():
    """
    Fetches the department details by ID from the URL query parameter.
    Also, fetches all employees belonging to the department.
    """
    department_id = request.args.get('id')

    if not department_id:
        return render_template('department.html', error_message="No department ID provided")

    # Fetch department info (name and description)
    dep_info = department_info(department_id)

    # Fetch all employees belonging to the department
    employees = get_employees_by_department(department_id)

    if not employees:
        return render_template('department.html', error_message="No employees found for this department")

    # Pass department info (name) and employee list to the template
    return render_template(
        'department.html',
        dep_name=dep_info[0] if dep_info else "Unknown Department",
        employees=employees
    )


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