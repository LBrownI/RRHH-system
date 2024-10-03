from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Ruta para la página de login
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Aquí puedes agregar la lógica para validar al usuario.
        # Por ejemplo, comprobar si el usuario y la contraseña son correctos.
        
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
@app.route('/colaborador')
def user():
    return render_template('colaborador.html')

if __name__ == '__main__':
    app.run(debug=True)
