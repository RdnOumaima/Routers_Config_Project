import xlrd
import ipaddress
import re
import datetime  # Import the datetime module
import pymysql
from flask import Flask, render_template, request, send_file, url_for, redirect, flash, session
from flask import send_from_directory
from router_config_generator import generate_router_config  # Importez la fonction
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

import pymysql
app = Flask(__name__)

#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/huawei_db_app'  # Update the URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/huawei_db_app'
app.config['SECRET_KEY'] = '123456789'  # Set your secret key

db = SQLAlchemy(app)  # Initialize SQLAlchemy

def is_valid_password(password):
    # Vérification de la longueur minimale
    if len(password) < 8:
        return False
                # Vérification de la présence de chiffres et de lettres
    if not re.search(r'\d', password) or not re.search(r'[a-zA-Z]', password):
        return False        
   # Vérification de la présence d'au moins un caractère majuscule
    if not any(c.isupper() for c in password):
        return False
        
    return True

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.date_registered}')"





# Create the database and tables if they don't exist
with app.app_context():
    db.create_all()



@app.route('/')
def index():
    return render_template('sign_In.html')


#@app.route('/welcome', methods=['GET'])
#def welcome():
#    return render_template('welcome.html')

@app.route('/welcome', methods=['GET'])
def welcome():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('index.html', user=user)
    else:
        flash('Please log in to access this page.', 'info')
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if request.method == 'POST':
        # Handle form submission
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']


        # Vérifiez si l'adresse email est valide
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Invalid email address format. Please enter a valid email address.')
            return redirect(url_for('inscription'))
            

        # Vérifiez si tous les champs sont remplis
        if not username or not password:
            flash('Please fill in all required fields.')
            return redirect(url_for('inscription'))

        # Vérifiez si l'utilisateur existe déjà avec la même adresse email
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with this email address already exists.')
            return redirect(url_for('inscription'))
        
        # Vérifiez si le mot de passe respecte les règles
        if not is_valid_password(password):
            flash('Le mot de passe doit contenir au moins 8 caractères, des chiffres, des lettres et au moins une majuscule.', 'danger')
            return redirect(url_for('inscription'))

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Your account has been created! Login here')
        return redirect(url_for('index'))

    return render_template('inscription.html')




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session['user_id'] = user.id
            return redirect(url_for('welcome'))  # Redirect to the welcome page or index page
        else:
            flash('Login failed. Please check your credentials.', 'danger')
            return redirect(url_for('login'))  # Redirect back to the login page with error message
    else:
        # Render the login form for GET requests
        return render_template('sign_in.html')



@app.route('/upload', methods=['GET', 'POST'])
def upload():
    config_script_text = None  # Initialize the variable with None
    download_link = None
    
    if request.method == 'POST':
        # CHECK IF THE FILE IS PRESENT IN THE REQUEST 
        if 'file' not in request.files:
            return "No file part", 400
        file = request.files['file']

        # to check if the user selected a file 
        if file.filename == '':
            return "No selected file", 400

        # Process the uploaded file and generate the configuration script
        config_type = request.form.get('generate_option')  # Get the selected config type from the form
        config_script_text = generate_router_config(file, config_type)  # Pass the selected config type

        # Create a new file to store the configuration with a timestamp in the filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        output_file = f'router_configuration_{timestamp}.txt'

        # Write the configuration script to the output file
        with open(output_file, 'w') as f:
            f.write(config_script_text)

        # Create a download link for the user
        download_link = url_for('download', filename=output_file)

        # Return a response to the user with preformatted text
        response_text = f"Configuration saved to '{output_file}' file.\n\n<pre>{config_script_text}</pre>\n"
        print("Generated Configuration:\n", config_script_text)

    # Render the upload.html template for GET requests  
    return render_template('generated_config.html', config_script_text=config_script_text, download_link=download_link)


@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    return send_file(filename, as_attachment=True)




if __name__ == '__main__':
    app.run(debug=True)
