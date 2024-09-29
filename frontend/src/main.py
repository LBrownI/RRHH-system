from flask import Flask, render_template, g

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('./index.html')

@app.route('/login')
def login():
    return render_template('./login.html')

@app.route('/user')
def user():
    return render_template('./user.html')

if __name__ == '__main__':
    app.run(debug=True)