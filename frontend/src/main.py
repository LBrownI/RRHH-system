from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy.orm import Session, sessionmaker
from load_db import engine, Colaborador
from db_operations import add_contrato
from vacation_logic import add_vacation_logic

# HI, I MADE LOTS OF CHANGES, IM SURE YOU'LL READ THIS ( ͡° ͜ʖ ͡°)
# CODE DOES NOT WORK, HELP @DANTE, @ALAN I KNOW THE add-contrato PAGE WORKS,
# I TESTED IT BEFORE BRINGING THE WHOLE DB AND SESSION HERE I'VE TRIED STUFF BUT NOTHING SEEMS TO WORK,
# I TRUST TOMORROW WE'LL REVISE IT BETTER

app = Flask(__name__)
app.secret_key = 'magickey'

# Set up session for SQLAlchemy
Session = sessionmaker(bind=engine)
session = Session()

# Ruta para la página de login
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Aquí puedes agregar la lógica para validar al usuario.
        # Por ejemplo, comprobar si el usuario y la contraseña son correctos.
        
        # REVISE: https://webdamn.com/login-and-registration-with-python-flask-mysql/cl

        # Si la validación es correcta, redirige al menú (index.html)
        if username == 'user' and password == 'pass':  # Validación simple de ejemplo
            return redirect(url_for('menu'))
        else:
            return render_template('login.html', error="Usuario o contraseña incorrectos")
    return render_template('login.html')

# Ruta para la página del menú
@app.route('/menu')
def menu():
    return render_template('index.html')

# Ruta para la página del usuario (opcional)
@app.route('/user')
def user():
    return render_template('user.html')

#Route for the option of adding a new "Contrato" (that I hope we do somewhere)
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
        
        # Call function from db_operations.py
        message = add_contrato(session, contrato_data)
        flash(message)
        
        return redirect(url_for('add_contrato_page'))

    return render_template('add_contrato.html')

@app.route('/register_vacation')
def register_vacation():
    return render_template('register_vacation.html')  # Render the HTML form

@app.route('/add_vacation', methods=['POST'])
def add_vacation():
    colaborador_id = request.form.get('colaborador_id')
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_termino = request.form.get('fecha_termino')
    
    # Call vacation logic from vacation_logic.py
    success, message = add_vacation_logic(int(colaborador_id), fecha_inicio, fecha_termino)
    
    if success:
        flash('Vacation registered successfully!', 'success')
    else:
        flash(f'Error: {message}', 'danger')
    
    return redirect('/register_vacation')

# Part of the /add-contrato and /register_vacation page for showing colaborador name to the side of the id (kinda pointless but I like it)
@app.route('/get_colaborador_name/<int:colaborador_id>', methods=['GET'])
def get_colaborador_name(colaborador_id):
    session = Session()  
    colaborador = session.query(Colaborador).get(colaborador_id)  # Use SQLAlchemy to fetch the collaborator

    if colaborador:
        return colaborador.nombre
    else:
        return "Does not exist", 404 #lol

if __name__ == '__main__':
    app.run(debug=False)
