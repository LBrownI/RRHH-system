import os
from flask import Flask, render_template, request, redirect, url_for, flash
from queries import *
from interactions import *

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
    status = request.args.get('status', 1) # Default status is 1 (active)

    # Get filtered employees
    employees = get_filtered_employees(session, job_position_id, department_id, status)
    
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
            return redirect(url_for('user', id=employee.id))  # Cambio aquí para asegurar redireccionamiento con ?id

        # Mostrar mensaje de error si el empleado no es encontrado
        return render_template('index.html', error_message="Employee not found")
    
    # Obtener el ID del empleado si no hay parámetro de búsqueda
    employee_id = request.args.get('id')

    if not employee_id:
        # Mostrar mensaje si no se proporciona employee_id
        return render_template('employee.html', error_message="No employee ID provided")

    # Obtener la información del empleado
    gi = general_info(session, employee_id)
    ad_info = aditional_info(session, employee_id)

    # Verificar si falta información general
    if not gi:
        return render_template('employee.html', error_message="Employee not found")

    # Obtener el contrato actual
    contract = get_contract_info(session, employee_id)
    
    # Order the data to be passed to the template
    contract_data = {
        'contract_type': contract.contract_type,
        'start_date': contract.start_date,
        'end_date': contract.end_date,
        'classification': contract.classification,
        'position': contract.name, # it's actually not the name of the contract, but the name of the JobPosition
        'registration_date': contract.registration_date
    } if contract else None

    # Datos del empleado
    first_name, last_name, email, phone, rut, position, status = gi

    # Cambiar el estado del empleado a "Activo" o "Inactivo"
    if status == 0:
        status = "Inactive"
    elif status == 1:
        status = "Active"
    else:
        status = "Unknown"

    # Mostrar información faltante
    missing_info = []
    if not ad_info:
        missing_info.append("No additional info available")
    if not ad_info.get('net_amount'):
        missing_info.append("No net amount registered")
    if ad_info.get('health_plan') == "No health plan registered":
        missing_info.append("No health plan registered")

    # Obtener job positions y departments
    job_positions = get_job_positions(session)
    departments = get_departments(session)

    # Pasar los datos a la plantilla, incluyendo el contrato actual y los job_positions y departments
    return render_template(
        'employee.html',
        employee_id=employee_id,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        rut=rut,
        position=position,
        status=status,
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
        contract=contract_data,
        job_positions=job_positions,  # Pasa las posiciones de trabajo
        departments=departments       # Pasa los departamentos
    )


@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        # Recoge los datos del formulario
        employee_data = {
            'rut': request.form['rut'],
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'birth_date': request.form['birth_date'],
            'start_date': request.form['start_date'],
            'email': request.form['email'],
            'phone': request.form['phone'],
            'salary': request.form['salary'],
            'nationality': request.form['nationality'].capitalize(),
            'afp': request.form['afp_id'],
            'healthplan': request.form['healthplan_id'],
        }

        # Llama a la función para agregar el empleado
        result = add_employee_to_db(session, employee_data)
        flash(result)
        return redirect(url_for('homepage'))
    
    afps = all_afps(session)

    healthplans = all_health_plans(session)
    
    return render_template('add_employee.html', afps=afps, healthplans=healthplans)

    # Obtener los cargos para mostrar en el formulario
    job_positions = get_job_positions(session)
    return render_template('add_employee.html', job_positions=job_positions)

@app.route("/edit_employee", methods=['GET', 'POST'])
def edit_employee():
    employee_id = request.args.get('id')
    
    if request.method == 'POST':
        data = {
            'employee_id': int(request.form['employee_id']),
            'first_name': request.form['First Name'],
            'last_name': request.form['Last Name'],
            'email': request.form['Email'],
            'phone': request.form['Phone'],
            'rut': request.form['RUT'],
        }
        # make query to update the values
        print("this should be the employee id", data['employee_id'])
        update_employee(session, data)
        return redirect(url_for('homepage'))
    
    gi = general_info(session, employee_id)
    labels = ['First Name', 'Last Name', 'Email', 'Phone', 'RUT', 'Position', 'Status']
    gi_data = {}
    for i in range(len(labels)):
        gi_data[labels[i]] = gi[i]
    
    # NOTE:
    # It isn't necessary to make a dictionary with labels to aditional info because it is already 
    # defined as a dict with labels, unlike general_info, which is only defined as an array
    ad_info = aditional_info(session, employee_id)
    for key, value in ad_info.items():
        print(key, value)
    return render_template('edit_employee.html', gi_data=gi_data, ad_info_data=ad_info, employee_id=employee_id)

@app.route('/disable_employee/<int:employee_id>')
def disable_employee(employee_id):
    # Lógica para cargar la información del contrato que se desea eliminar
    employee = Employee.query.get(employee_id)
    return render_template('disable_employee.html', employee=employee)


@app.route('/confirm_disable_employee/<int:employee_id>', methods=['POST'])
def confirm_disable_employee(employee_id):
    # Obtener el contrato usando la función de consulta personalizada
    contract_deactivated = deactivate_employee(session, employee_id)

    # Mostrar mensaje de éxito o error
    if contract_deactivated:
        flash('Contract successfully deactivated', 'success')
    else:
        flash('Error: Contract could not be deactivated', 'danger')

    return redirect(url_for('user', id=employee_id))

# MENU PAGES ------------------------------------------------------------------------------------------------|

@app.route('/afps')
def show_afps():
    with Session() as session:
        afps = all_afps(session)
    return render_template('afps.html', afps=afps)


@app.route('/companies')
def show_companies():
    with Session() as session:
        companies = all_companies(session)
    return render_template('companies.html', companies=companies)

@app.route('/add_company', methods=['GET', 'POST']) 
def add_company():
    if request.method == 'POST':
        # Gather form data
        company_data = {
            'rut': request.form['rut'],
            'name': request.form['name'],
            'address': request.form['address'],
            'phone': request.form['phone'],
            'industry': request.form['industry'].capitalize(),
        }

        # Call the function to add the company
        result = add_company_to_db(session, company_data)
        flash(result)
        job_positions = get_job_positions(session)
        departments = get_departments(session)

        return redirect(url_for('homepage'))  # Redirect to homepage or appropriate view
    
    return render_template('add_company.html', job_positions=job_positions, departments=departments)


@app.route('/health_plans')
def health_plans():
    session = Session()

    #get all health plans with their discounts
    health_plans = all_health_plans(session)

    # Return the template with the health plans data
    return render_template('health_plans.html', health_plans=health_plans)

# TOPBAR PAGES ------------------------------------------------------------------------------------------------|

@app.route('/remuneration')
def remunerations_page():
    session = Session()
    remuneration = all_remunerations(session)
    session.close()
    return render_template('remunerations.html', remunerations=remuneration)

@app.route('/add_remuneration', methods=['GET', 'POST'])
def add_remuneration_page():
    if request.method == 'POST':
        remuneration_data = {
            'employee_id': request.form['employee_id'],
            'afp_id': request.form['afp_id'],
            'health_plan_id': request.form['health_plan_id'],
            'gross_amount': request.form['gross_amount'],
            'tax': request.form['tax'],
            'deductions': request.form['deductions'],
            'bonus': request.form['bonus'],
            'welfare_contribution': request.form['welfare_contribution'],
            'net_amount': request.form['net_amount']
        }
        session = Session()
        result = add_remuneration(session, remuneration_data)
        flash(result)

        return redirect(url_for('add_remuneration.html'))
    
    session = Session()
    afps = session.query(AFP).all()
    healthplans = session.query(HealthPlan).all()
    
    return render_template('add_remuneration.html', afps=afps, healthplans=healthplans)

@app.route('/contracts')
def show_contracts():
    with Session() as session:
        contracts = all_contracts(session)
    return render_template('contracts.html', contracts=contracts)

# Route for the option of adding a new "Contract"
@app.route('/add_contract', methods=['GET', 'POST'])
def add_contract_page():
    if request.method == 'POST':
        # Recolectar datos del formulario
        contract_data = {
            'employee_id': request.form.get('employee_id'),  # Cambiar a employee_id si se utiliza internamente
            'contract_type': request.form.get('contract_type'),
            'start_date': request.form.get('start_date'),
            'end_date': request.form.get('end_date'),
            'classification': request.form.get('classification'),
            'position': request.form.get('position'),
            'department_name': request.form.get('department_name')
        }

        # Validar que los campos obligatorios están presentes
        required_fields = ['employee_id', 'contract_type', 'start_date', 'position', 'department_name']
        missing_fields = [field for field in required_fields if not contract_data.get(field)]
        
        if missing_fields:
            flash(f"Error: Missing fields: {', '.join(missing_fields)}", 'danger')
            return redirect(url_for('add_contract_page'))

        # Intentar agregar el contrato
        session = Session()
        try:
            message = add_contract(session, contract_data)
            flash(message, 'success')
            return redirect(url_for('show_contracts'))  # Redirigir a la página de contratos
        except Exception as e:
            session.rollback()
            flash(f"Error adding contract: {e}", 'danger')
        finally:
            session.close()
    
    # Preparar datos para el formulario
    with Session() as session:
        employees = session.query(Employee).all()
        job_positions = get_job_positions(session)
        departments = get_departments(session)
    return render_template(
        'add_contract.html', 
        employees=employees,
        job_positions=job_positions,
        departments=departments
    )


@app.route('/vacations')
def show_vacations():
    with Session() as session:
        vacations = all_vacations(session)
    return render_template('vacations.html', vacations=vacations)


# Route for adding vacation (no database interaction)
@app.route('/add_vacation', methods=['GET', 'POST'])
def add_vacation():
    if request.method == 'POST':
        # Get form data
        vacation_data = {
            'employee_id': request.form['employee_id'],
            'start_date': request.form['start_date'],
            'end_date': request.form['end_date']
        }

        # Call the query function
        success, message = add_vacation_to_db(session, vacation_data)

        # Provide feedback to the user
        flash(message)
        return redirect(url_for('homepage'))

    # Fetch necessary data for the form
    employees = session.query(Employee).all()
    return render_template('add_vacation.html', employees=employees)


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


@app.route('/get_employee_name/<string:employee_rut>', methods=['GET'])  # Cambiado a <string:employee_rut>
def get_employee_name(employee_rut):
    employee_name = get_employee_name_by_rut(employee_rut)  # Llamamos a la nueva función
    if employee_name:
        return employee_name  # Return the name as plain text
    else:
        return "Does not exist", 404

if __name__ == '__main__':
    app.run(debug=True)