from flask import Flask, render_template, request, redirect, url_for, flash
# from sqlalchemy.orm import Session, sessionmaker
# from load_db import engine, Colaborador
# from db_operations import add_contrato
# from vacation_logic import add_vacation_logic

# HI, I MADE LOTS OF CHANGES, IM SURE YOU'LL READ THIS ( ͡° ͜ʖ ͡°)
# OK SO IT WORKS, ITS A MOCKED VERSION O THE CODE, WHICH MEANS IT'S SIMULATED/FALSE/TEMPORARY CODE JUST TO
# MIMIC SOME FUNCTIONALITIES WITHOUT FULLY INTEGRATING IT. SO INSTEAD OF CONNECTING TO THE DATABASE
# IT GENERATES FALSE RESPONSES TO TEST OUT. THE DB IMPLEMENTATION IS COMMENTED-OUT WITH '''

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
    return render_template('index.html')

# Route for the colaborador (optional)
@app.route('/colaborador')
def user():
    return render_template('colaborador.html')

# Route for the option of adding a new "Contrato" (mocked functionality)
@app.route('/add-contrato', methods=['GET', 'POST'])
def add_contrato_page():
    if request.method == 'POST':
        # Gather form data
        contrato_data = {
            'colaborador_id': request.form['colaborador_id'],
            'tipo_contrato': request.form['tipo_contrato'],
            'fecha_inicio': request.form['fecha_inicio'],
            'fecha_fin': request.form['fecha_fin'],
            'escalafon': request.form['escalafon']
        }
        
        # Mock message for adding contrato
        message = "Mock: Contrato added successfully!"
        flash(message)

        # Original setup
        """
         Call function from db_operations.py
         message = add_contrato(session, contrato_data)
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
    colaborador_id = request.form.get('colaborador_id')
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_termino = request.form.get('fecha_termino')
    
    # Mock success and message (bypassing actual vacation logic)
    success = True
    message = "Mock: Vacation added!"

    # Original setup
    """  
    Call vacation logic from vacation_logic.py
    success, message = add_vacation_logic(int(colaborador_id), fecha_inicio, fecha_termino)
    """ 
    if success:
        flash('Vacation registered successfully!', 'success')
    else:
        flash(f'Error: {message}', 'danger')
    
    return redirect('/register_vacation')

# Part of the /add-contrato and /register_vacation page for showing colaborador name to the side of the id (mocked functionality)
@app.route('/get_colaborador_name/<int:colaborador_id>', methods=['GET'])
def get_colaborador_name(colaborador_id):

    # Mocked collaborator lookup
    colaborador = {'nombre': 'Mock Collaborator'} if colaborador_id == 1 else None

    # Original setup
    """
    colaborador = session.query(Colaborador).get(colaborador_id)  # Use SQLAlchemy to fetch the collaborator
    """
    if colaborador:
        return colaborador['nombre']
    else:
        return "Does not exist", 404

if __name__ == '__main__':
    app.run(debug=True)