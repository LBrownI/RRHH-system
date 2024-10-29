import os
from flask import Flask, render_template, request, redirect, url_for, flash
from queries import *

app = Flask(
    __name__, 
    template_folder=os.path.join(os.getcwd(), 'project', 'frontend', 'src', 'templates'),
    static_folder=os.path.join(os.getcwd(), 'project', 'frontend', 'src', 'static')
)
app.secret_key = 'magickey'

# Route for menu page (homepage)
@app.route('/')
def homepage():
    job_position_id = request.args.get('job_position', type=int)
    department_id = request.args.get('department', type=int)

    # Get filtered employees
    employees = get_filtered_employees(session, job_position_id, department_id)
    
    # Fetch job positions and departments for dropdown lists
    job_positions = get_job_positions(session)
    departments = get_departments(session)

    return render_template('index.html', employees=employees, job_positions=job_positions, departments=departments)



# Ruta para el perfil del empleado con búsqueda integrada
@app.route('/employee')
def user():
    search_query = request.args.get('search_query')
    
    # Realizar la búsqueda si hay un parámetro de búsqueda
    if search_query:
        employee = search_employee_by_name_or_rut(search_query, session)
        
        # Redireccionar al perfil si se encuentra un empleado
        if employee:
            return redirect(url_for('user', id=employee.id))
        
        # Mostrar un mensaje de error si el empleado no es encontrado
        return render_template('index.html', error_message="Employee not found")
    
    # Obtener el ID del empleado si no hay parámetro de búsqueda
    employee_id = request.args.get('id')

    if not employee_id:
        # Mostrar un mensaje si no se proporciona employee_id
        return render_template('employee.html', error_message="No employee ID provided")

    # Obtener información general y adicional del empleado
    gi = general_info(session, employee_id)
    ad_info = aditional_info(session, employee_id)

    # Verificar si falta información general
    if not gi:
        return render_template('employee.html', error_message="Employee not found")

    # Obtener el contrato actual del empleado
    contract = session.query(Contract).filter_by(employee_id=employee_id).order_by(Contract.start_date.desc()).first()

    # Preparar datos del contrato actual si existe
    contract_data = {
        'contract_type': contract.contract_type,
        'start_date': contract.start_date,
        'end_date': contract.end_date,
        'classification': contract.classification,
        'position': contract.position_id,
        'registration_date': contract.registration_date
    } if contract else None

    # Datos del empleado
    first_name, last_name, email, phone, rut, position = gi

    # Mostrar información faltante
    missing_info = []
    if not ad_info:
        missing_info.append("No additional info available")
    if not ad_info.get('net_amount'):
        missing_info.append("No net amount registered")
    if ad_info.get('health_plan') == "No health plan registered":
        missing_info.append("No health plan registered")

    # Pasar los datos a la plantilla, incluyendo el contrato actual
    return render_template(
        'employee.html',
        employee_id=employee_id,
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
        missing_info=missing_info,
        contract=contract_data
    )


@app.route('/companies')
def show_companies():
    with Session() as session:
        companies = all_companies(session)
    return render_template('companies.html', companies=companies)

@app.route('/afps')
def show_afps():
    with Session() as session:
        afps = all_afps(session)
    return render_template('afps.html', afps=afps)

# Route for the option of adding a new "Contract"
# WORKING BUT redirects to /add_contract instead of staying on the colaborator page.
@app.route('/add-contract', methods=['GET', 'POST'])
def add_contract_page():
    if request.method == 'POST':
        # Gather form data
        contract_data = {
            'employee_rut': request.form['employee_rut'],  # Cambiado de employee_id a employee_rut
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

@app.route('/remove_contract/<int:employee_id>')
def remove_contract(employee_id):
    # Lógica para cargar la información del contrato que se desea eliminar
    employee = Employee.query.get(employee_id)
    return render_template('remove_contract.html', employee=employee)


@app.route('/confirm_remove_contract/<int:employee_id>', methods=['POST'])
def confirm_remove_contract(employee_id):
    # Obtener el contrato usando la función de consulta personalizada
    contract = get_contract_by_employee_id(session, employee_id)
    if contract:
        session.delete(contract)
        session.commit()
    return redirect(url_for('user', id=employee_id))




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

@app.route('/get_employee_name/<string:employee_rut>', methods=['GET'])  # Cambiado a <string:employee_rut>
def get_employee_name(employee_rut):
    employee_name = get_employee_name_by_rut(employee_rut)  # Llamamos a la nueva función
    if employee_name:
        return employee_name  # Return the name as plain text
    else:
        return "Does not exist", 404



if __name__ == '__main__':
    app.run(debug=True)