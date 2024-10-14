import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from tables import Company, Employee, JobPosition, EmployeePosition, AFP, Department, Vacation, Evaluation, Training, Remuneration, HealthPlan, Fonasa, Isapre, Bonus, Contract, User

# Load the MySQL root password from environment variables
mysql_root_password = os.getenv('MYSQL_ROOT_PASSWORD', 'default_root_pass')  # Fallback in case the env variable isn't set
# You can set it up by doing: export MYSQL_ROOT_PASSWORD=your_secure_password

config = {'host': 'localhost',
          'database_name': 'hr',
          'user': 'root',
          'password': mysql_root_password}

engine = create_engine(f'mysql+pymysql://{config["user"]}:{config["password"]}@{config["host"]}/{config["database_name"]}', echo=True)
# engine = create_engine(f'mysql+pymysql://{config["user"]}:{config["password"]}@{config["host"]}', echo=True)

with engine.connect() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {config['database_name']}"))

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# Insert data into Company table
company_data = [
    {'id': 1, 'rut': '76.123.456-7', 'name': 'TechCorp', 'address': '123 Main Street', 'phone': '555-0100', 'industry': 'Technology'},
    {'id': 2, 'rut': '78.234.567-8', 'name': 'HealthSolutions', 'address': '456 Oak Avenue', 'phone': '555-0200', 'industry': 'Healthcare'}
]

for data in company_data:
    company = Company(**data)
    session.add(company)
session.commit()

# Insert data into Employee table
employee_data = [
    {'id': 1, 'rut': '12.345.678-9', 'first_name': 'John', 'last_name': 'Doe', 'birth_date': date(1980, 5, 12), 'start_date': date(2020, 1, 15), 'phone': '555-2345', 'salary': 2000.00, 'nationality': 'Chilean'},
    {'id': 2, 'rut': '12.345.678-1', 'first_name': 'Mary', 'last_name': 'Johnson', 'birth_date': date(1985, 9, 22), 'start_date': date(2019, 3, 10), 'phone': '555-6789', 'salary': 2500.00, 'nationality': 'Chilean'},
    {'id': 3, 'rut': '13.345.678-2', 'first_name': 'Carlos', 'last_name': 'Williams', 'birth_date': date(1990, 7, 18), 'start_date': date(2021, 6, 5), 'phone': '555-9102', 'salary': 1800.00, 'nationality': 'Chilean'},
    {'id': 4, 'rut': '14.345.678-3', 'first_name': 'Anna', 'last_name': 'Brown', 'birth_date': date(1992, 11, 2), 'start_date': date(2018, 9, 25), 'phone': '555-1124', 'salary': 2300.00, 'nationality': 'Chilean'},
    {'id': 5, 'rut': '18.145.678-4', 'first_name': 'Louis', 'last_name': 'Davis', 'birth_date': date(1995, 2, 15), 'start_date': date(2022, 2, 1), 'phone': '555-1416', 'salary': 2100.00, 'nationality': 'Chilean'},
    {'id': 6, 'rut': '16.245.678-5', 'first_name': 'Laura', 'last_name': 'Miller', 'birth_date': date(1997, 6, 25), 'start_date': date(2020, 8, 14), 'phone': '555-1718', 'salary': 2400.00, 'nationality': 'Chilean'},
    {'id': 7, 'rut': '16.645.678-6', 'first_name': 'Robert', 'last_name': 'Wilson', 'birth_date': date(1987, 4, 8), 'start_date': date(2017, 10, 12), 'phone': '555-1920', 'salary': 2200.00, 'nationality': 'Chilean'},
    {'id': 8, 'rut': '12.945.678-7', 'first_name': 'Fernanda', 'last_name': 'Taylor', 'birth_date': date(1988, 1, 3), 'start_date': date(2021, 4, 8), 'phone': '555-2021', 'salary': 2700.00, 'nationality': 'Chilean'},
    {'id': 9, 'rut': '14.745.678-8', 'first_name': 'George', 'last_name': 'Anderson', 'birth_date': date(1986, 12, 20), 'start_date': date(2020, 3, 14), 'phone': '555-2223', 'salary': 2600.00, 'nationality': 'Chilean'},
    {'id': 10, 'rut': '10.345.678-K', 'first_name': 'Claudia', 'last_name': 'Thomas', 'birth_date': date(1983, 10, 30), 'start_date': date(2016, 7, 3), 'phone': '555-2324', 'salary': 1900.00, 'nationality': 'Chilean'},
    {'id': 11, 'rut': '12.987.654-3', 'first_name': 'Jean', 'last_name': 'Baptiste', 'birth_date': date(1990, 3, 18), 'start_date': date(2021, 7, 12), 'phone': '555-3456', 'salary': 2100.00, 'nationality': 'Haitian'}
]


for data in employee_data:
    employee = Employee(**data)
    session.add(employee)
session.commit()

# Insert data into Department table
department_data = [
    {'id': 1, 'name': 'IT Department'},
    {'id': 2, 'name': 'HR Department'},
    {'id': 3, 'name': 'Finance Department'},
    {'id': 4, 'name': 'Marketing Department'}
]

for data in department_data:
    department = Department(**data)
    session.add(department)
session.commit()

# Insert data into JobPosition table
job_position_data = [
    {'id': 1, 'name': 'Software Engineer', 'description': 'Develops and maintains software applications.', 'department_id': 1},
    {'id': 2, 'name': 'HR Specialist', 'description': 'Handles employee relations and recruitment.', 'department_id': 2},
    {'id': 3, 'name': 'Project Manager', 'description': 'Leads and manages project execution.', 'department_id': 1},
    {'id': 4, 'name': 'System Administrator', 'description': 'Manages IT systems and infrastructure.', 'department_id': 1},
    {'id': 5, 'name': 'Marketing Analyst', 'description': 'Analyzes marketing data and trends.', 'department_id': 4}
]

for data in job_position_data:
    job_position = JobPosition(**data)
    session.add(job_position)
session.commit()

employee_position_data = [
    {'employee_id': 1, 'position_id': 1},  # John -> Software Engineer
    {'employee_id': 2, 'position_id': 2},  # Mary -> HR Specialist
    {'employee_id': 3, 'position_id': 1},  # Carlos -> Software Engineer
    {'employee_id': 4, 'position_id': 2},  # Anna -> HR Specialist
    {'employee_id': 5, 'position_id': 3},  # Louis -> Project Manager
    {'employee_id': 6, 'position_id': 4},  # Laura -> System Administrator
    {'employee_id': 7, 'position_id': 4},  # Robert -> System Administrator
    {'employee_id': 8, 'position_id': 5},  # Fernanda -> Marketing Analyst
    {'employee_id': 9, 'position_id': 5},  # George -> Marketing Analyst
    {'employee_id': 10, 'position_id': 3},  # Claudia -> Project Manager
    {'employee_id': 11, 'position_id': 1}   # Jean -> Software Engineer
]

for data in employee_position_data:
    emp_pos = EmployeePosition(**data)
    session.add(emp_pos)
session.commit()

# Insert data into AFP table
afp_data = [
    {'id': 1, 'name': 'AFP Capital', 'commission_percentage': 1.44},
    {'id': 2, 'name': 'AFP Cuprum', 'commission_percentage': 1.44},
    {'id': 3, 'name': 'AFP Habitat', 'commission_percentage': 1.27},
    {'id': 4, 'name': 'AFP Modelo', 'commission_percentage': 0.58},
    {'id': 5, 'name': 'AFP Planvital', 'commission_percentage': 1.16},
    {'id': 6, 'name': 'AFP Provida', 'commission_percentage': 1.45},
    {'id': 7, 'name': 'AFP Uno', 'commission_percentage': 0.49}
]

for data in afp_data:
    afp = AFP(**data)
    session.add(afp)
session.commit()


# Insert data into HealthPlan, Fonasa, and Isapre tables
health_plan_data = [
    {'id': 1, 'name': 'Fonasa Plan A', 'type': 'Fonasa'},
    {'id': 2, 'name': 'Fonasa Plan B', 'type': 'Fonasa'},
    {'id': 3, 'name': 'Fonasa Plan C', 'type': 'Fonasa'},
    {'id': 4, 'name': 'Fonasa Plan D', 'type': 'Fonasa'},
    {'id': 5, 'name': 'Isapre Plan 1', 'type': 'Isapre'},
    {'id': 6, 'name': 'Isapre Plan 2', 'type': 'Isapre'}
]

for data in health_plan_data:
    health_plan = HealthPlan(**data)
    session.add(health_plan)
session.commit()

# Insert data into Fonasa table
fonasa_data = [
    {'id': 1, 'health_plan_id': 1, 'discount': 4.00},
    {'id': 2, 'health_plan_id': 2, 'discount': 6.00},
    {'id': 3, 'health_plan_id': 3, 'discount': 7.00},
    {'id': 4, 'health_plan_id': 4, 'discount': 7.00},
]

for data in fonasa_data:
    fonasa = Fonasa(**data)
    session.add(fonasa)
session.commit()

# Insert data into Isapre table
isapre_data = [
    {'id': 1, 'health_plan_id': 5, 'discount': 10.00},
    {'id': 2, 'health_plan_id': 6, 'discount': 12.00}
]

for data in isapre_data:
    isapre = Isapre(**data)
    session.add(isapre)
session.commit()

# Insert data into Contract table
contract_data = [
    {'id': 1, 'employee_id': 1, 'contract_type': 'permanent', 'start_date': date(2020, 1, 15), 'end_date': date(2023, 1, 15), 'classification': 'professional', 'position_id': 1, 'registration_date': date(2020, 1, 15)},
    {'id': 2, 'employee_id': 2, 'contract_type': 'fixed-term', 'start_date': date(2019, 3, 10), 'end_date': date(2022, 3, 10), 'classification': 'administrative', 'position_id': 2, 'registration_date': date(2019, 3, 10)},
    {'id': 3, 'employee_id': 3, 'contract_type': 'temporary', 'start_date': date(2021, 6, 5), 'end_date': date(2022, 6, 5), 'classification': 'technical', 'position_id': 3, 'registration_date': date(2021, 6, 5)},
    {'id': 4, 'employee_id': 4, 'contract_type': 'substitute', 'start_date': date(2018, 9, 25), 'end_date': date(2021, 9, 25), 'classification': 'auxiliary', 'position_id': 4, 'registration_date': date(2018, 9, 25)},
    {'id': 5, 'employee_id': 5, 'contract_type': 'permanent', 'start_date': date(2022, 2, 1), 'end_date': date(2025, 2, 1), 'classification': 'executive', 'position_id': 1, 'registration_date': date(2022, 2, 1)}
]

for data in contract_data:
    contract = Contract(**data)
    session.add(contract)
session.commit()


# Insert data into Vacation table
vacation_data = [
    {'id': 1, 'employee_id': 1, 'start_date': date(2023, 1, 5), 'end_date': date(2023, 1, 20), 'days_taken': 15, 'accumulated_days': 10, 'long_service_employee': False},
    {'id': 2, 'employee_id': 2, 'start_date': date(2023, 6, 1), 'end_date': date(2023, 6, 10), 'days_taken': 9, 'accumulated_days': 5, 'long_service_employee': False},
    {'id': 3, 'employee_id': 3, 'start_date': date(2022, 12, 15), 'end_date': date(2022, 12, 30), 'days_taken': 15, 'accumulated_days': 3, 'long_service_employee': False},
    {'id': 4, 'employee_id': 4, 'start_date': date(2022, 8, 1), 'end_date': date(2022, 8, 15), 'days_taken': 14, 'accumulated_days': 6, 'long_service_employee': True},
    {'id': 5, 'employee_id': 5, 'start_date': date(2023, 2, 10), 'end_date': date(2023, 2, 25), 'days_taken': 15, 'accumulated_days': 8, 'long_service_employee': False}
]

for data in vacation_data:
    vacation = Vacation(**data)
    session.add(vacation)
session.commit()

# Insert data into Evaluation table
evaluation_data = [
    {'id': 1, 'employee_id': 1, 'evaluation_date': date(2023, 5, 15), 'evaluator': 'Supervisor A', 'evaluation_factor': 4.5, 'rating': 'Good', 'comments': 'Excellent performance.'},
    {'id': 2, 'employee_id': 2, 'evaluation_date': date(2023, 7, 10), 'evaluator': 'Supervisor B', 'evaluation_factor': 3.8, 'rating': 'Fair', 'comments': 'Needs to improve teamwork.'},
    {'id': 3, 'employee_id': 3, 'evaluation_date': date(2023, 3, 25), 'evaluator': 'Supervisor C', 'evaluation_factor': 4.0, 'rating': 'Good', 'comments': 'Generally good performance.'},
    {'id': 4, 'employee_id': 4, 'evaluation_date': date(2022, 12, 5), 'evaluator': 'Supervisor A', 'evaluation_factor': 4.7, 'rating': 'Good', 'comments': 'Highly recommended for promotions.'},
    {'id': 5, 'employee_id': 5, 'evaluation_date': date(2023, 1, 20), 'evaluator': 'Supervisor B', 'evaluation_factor': 3.5, 'rating': 'Fair', 'comments': 'Could improve punctuality.'}
]

for data in evaluation_data:
    evaluation = Evaluation(**data)
    session.add(evaluation)
session.commit()

# Insert data into Training table
training_data = [
    {'id': 1, 'employee_id': 1, 'training_date': date(2023, 3, 5), 'course': 'Advanced Python', 'score': 4.5, 'institution': 'Tech Academy', 'comments': 'Excellent participation.'},
    {'id': 2, 'employee_id': 2, 'training_date': date(2023, 4, 15), 'course': 'Project Management', 'score': 4.0, 'institution': 'University A', 'comments': 'Good grasp of the subject.'},
    {'id': 3, 'employee_id': 3, 'training_date': date(2022, 11, 22), 'course': 'Cybersecurity', 'score': 3.8, 'institution': 'Tech Institute', 'comments': 'Acceptable performance.'},
    {'id': 4, 'employee_id': 4, 'training_date': date(2022, 6, 18), 'course': 'Digital Marketing', 'score': 4.2, 'institution': 'Online Academy', 'comments': 'Good tool mastery.'},
    {'id': 5, 'employee_id': 5, 'training_date': date(2023, 1, 10), 'course': 'Scrum Master', 'score': 3.5, 'institution': 'Scrum Training', 'comments': 'Needs to improve leadership.'}
]

for data in training_data:
    training = Training(**data)
    session.add(training)
session.commit()

# Insert data into Remuneration table
remuneration_data = [
    {'id': 1, 'employee_id': 1, 'afp_id': 1, 'health_plan_id': 1, 'gross_amount': 2500.00, 'tax': 10.0, 'deductions': 150.00, 'bonus': 200.00, 'welfare_contribution': 50.00, 'net_amount': 2200.00},
    {'id': 2, 'employee_id': 2, 'afp_id': 2, 'health_plan_id': 2, 'gross_amount': 3000.00, 'tax': 12.0, 'deductions': 200.00, 'bonus': 250.00, 'welfare_contribution': 60.00, 'net_amount': 2650.00},
    {'id': 3, 'employee_id': 3, 'afp_id': 3, 'health_plan_id': 3, 'gross_amount': 2300.00, 'tax': 9.0, 'deductions': 130.00, 'bonus': 150.00, 'welfare_contribution': 40.00, 'net_amount': 2070.00},
    {'id': 4, 'employee_id': 4, 'afp_id': 4, 'health_plan_id': 1, 'gross_amount': 2800.00, 'tax': 11.0, 'deductions': 180.00, 'bonus': 300.00, 'welfare_contribution': 55.00, 'net_amount': 2455.00},
    {'id': 5, 'employee_id': 5, 'afp_id': 5, 'health_plan_id': 2, 'gross_amount': 2700.00, 'tax': 10.5, 'deductions': 170.00, 'bonus': 280.00, 'welfare_contribution': 50.00, 'net_amount': 2390.00}
]

for data in remuneration_data:
    remuneration = Remuneration(**data)
    session.add(remuneration)
session.commit()

# Insert data into Bonus table
bonus_data = [
    {'id': 1, 'remuneration_id': 1, 'benefit': 500.00},
    {'id': 2, 'remuneration_id': 2, 'benefit': 300.00},
    {'id': 3, 'remuneration_id': 3, 'benefit': 400.00},
    {'id': 4, 'remuneration_id': 4, 'benefit': 200.00},
    {'id': 5, 'remuneration_id': 5, 'benefit': 350.00}
]

for data in bonus_data:
    bonus = Bonus(**data)
    session.add(bonus)
session.commit()

# Insert user and password into User table
new_user = User(username='LBrownI')
new_user.set_password('Ingreso_07')
session.add(new_user)
session.commit()

# Close the session
session.close()
