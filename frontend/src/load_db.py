from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DECIMAL, Date, Text, Boolean
from sqlalchemy import text
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash


config = {'host': 'localhost', 'database_name': 'hr', 'user': 'root', 'password': 'rootpass'}
engine = create_engine(f'mysql+pymysql://{config["user"]}:{config["password"]}@{config["host"]}/{config["database_name"]}', echo=True)

with engine.connect() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {config['database_name']}"))

Base = declarative_base()

# Empresa model
class Empresa(Base):
    __tablename__ = 'Empresa'
    id = Column(Integer, primary_key=True)
    rut = Column(String(20))
    nombre = Column(String(100))
    direccion = Column(String(255))
    telefono = Column(String(20))
    giro = Column(String(100))

# Colaborador model
class Colaborador(Base):
    __tablename__ = 'Colaborador'
    id = Column(Integer, primary_key=True)
    rut = Column(String(20))
    nombre = Column(String(50))
    apellido = Column(String(50))
    fecha_nacimiento = Column(Date)
    fecha_ingreso = Column(Date)
    telefono = Column(String(20))
    salario = Column(DECIMAL(10, 2))
    nacionalidad = Column(String(50))
    contratos = relationship('Contrato', back_populates='colaborador')
    vacaciones = relationship('Vacaciones', back_populates='colaborador')
    evaluaciones = relationship('Evaluacion', back_populates='colaborador')
    capacitaciones = relationship('Capacitacion', back_populates='colaborador')
    remuneraciones = relationship('Remuneracion', back_populates='colaborador')
    cargos = relationship('Cargo', secondary='ColaboradorCargo', back_populates='colaboradores')

# Cargo model
class Cargo(Base):
    __tablename__ = 'Cargo'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    descripcion = Column(Text)
    colaboradores = relationship('Colaborador', secondary='ColaboradorCargo', back_populates='cargos')

# ColaboradorCargo association table (Many-to-Many relationship between Colaborador and Cargo)
class ColaboradorCargo(Base):
    __tablename__ = 'ColaboradorCargo'
    colaborador_id = Column(Integer, ForeignKey('Colaborador.id'), primary_key=True)
    cargo_id = Column(Integer, ForeignKey('Cargo.id'), primary_key=True)
    
# AFP model
class AFP(Base):
    __tablename__ = 'AFP'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    comision_porcentaje = Column(DECIMAL(5, 2))
    remuneraciones = relationship('Remuneracion', back_populates='afp')

# Departamento model
class Departamento(Base):
    __tablename__ = 'Departamento'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    contratos = relationship('Contrato', back_populates='departamento')

# Vacaciones model
class Vacaciones(Base):
    __tablename__ = 'Vacaciones'
    id = Column(Integer, primary_key=True)
    colaborador_id = Column(Integer, ForeignKey('Colaborador.id'))
    fecha_inicio = Column(Date)
    fecha_termino = Column(Date)
    dias_tomados = Column(Integer) # Days taken in the period above 
    dias_acumulados = Column(Integer) # Acumulated after the vacation period above
    colaborador_antiguo = Column(Boolean) #If 1 then it's an employee that has worked for 15 years (20 days assigned instead of 15)
    colaborador = relationship('Colaborador', back_populates='vacaciones')

# Evaluacion model
class Evaluacion(Base):
    __tablename__ = 'Evaluacion'
    id = Column(Integer, primary_key=True)
    colaborador_id = Column(Integer, ForeignKey('Colaborador.id'))
    fecha_evaluacion = Column(Date)
    evaluador = Column(String(100))
    factor_evaluacion = Column(DECIMAL(5, 2))
    calificacion = Column(String(50))  # Bueno, regular, malo/deficiente
    comentarios = Column(Text)
    colaborador = relationship('Colaborador', back_populates='evaluaciones')

# Capacitacion model
class Capacitacion(Base):
    __tablename__ = 'Capacitacion'
    id = Column(Integer, primary_key=True)
    colaborador_id = Column(Integer, ForeignKey('Colaborador.id'))
    fecha_capacitacion = Column(Date)
    curso = Column(String(100))
    calificacion = Column(DECIMAL(5, 2))
    institucion = Column(String(100))
    comentarios = Column(Text)
    colaborador = relationship('Colaborador', back_populates='capacitaciones')

# Remuneracion (extended) model
class Remuneracion(Base):
    __tablename__ = 'Remuneracion'
    id = Column(Integer, primary_key=True)
    colaborador_id = Column(Integer, ForeignKey('Colaborador.id'))
    afp_id = Column(Integer, ForeignKey('AFP.id'))
    plan_salud_id = Column(Integer, ForeignKey('PlanDeSalud.id'))
    monto_bruto = Column(DECIMAL(10, 2))
    impuesto = Column(DECIMAL(5, 2))
    deducciones = Column(DECIMAL(10, 2))
    bonus = Column(DECIMAL(10, 2))
    aporte_bienestar = Column(DECIMAL(10, 2))
    monto_liquido = Column(DECIMAL(10, 2))
    colaborador = relationship('Colaborador', back_populates='remuneraciones')
    afp = relationship('AFP', back_populates='remuneraciones')
    plan_salud = relationship('PlanDeSalud', back_populates='remuneraciones')

class PlanDeSalud(Base):
    __tablename__ = 'PlanDeSalud'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    tipo = Column(String(50))
    fonasa = relationship('Fonasa', back_populates='plan_salud')
    isapre = relationship('Isapre', back_populates='plan_salud')
    remuneraciones = relationship('Remuneracion', back_populates='plan_salud')

# PlanDeSalud extension for Fonasa and Isapre
class Fonasa(Base):
    __tablename__ = 'Fonasa'
    id = Column(Integer, primary_key=True)
    plan_salud_id = Column(Integer, ForeignKey('PlanDeSalud.id'))
    descuento = Column(DECIMAL(5, 2))  # Different from Isapre's discount
    plan_salud = relationship('PlanDeSalud', back_populates='fonasa')

class Isapre(Base):
    __tablename__ = 'Isapre'
    id = Column(Integer, primary_key=True)
    plan_salud_id = Column(Integer, ForeignKey('PlanDeSalud.id'))
    descuento = Column(DECIMAL(5, 2))  # Different from Fonasa's discount
    plan_salud = relationship('PlanDeSalud', back_populates='isapre')

class Bonus(Base):
    __tablename__ = 'Bonus'
    id = Column(Integer, primary_key=True)
    remuneracion_id = Column(Integer, ForeignKey('Remuneracion.id'))
    aporte = Column(DECIMAL(5, 2))  # Help for the employee for a discount in money
    beneficio = relationship('PlanDeSalud', back_populates='isapre') # Help for the employee as a monetary aid

class Contrato(Base):
    __tablename__ = 'Contrato'
    id = Column(Integer, primary_key=True)
    colaborador_id = Column(Integer, ForeignKey('Colaborador.id'))
    tipo_contrato = Column(String(50))  # contrata, suplencia, reemplazo, planta
    fecha_inicio = Column(Date)
    fecha_termino = Column(Date)
    escalafon = Column(String(50))  # auxiliar, administrativo, tecnico, profesional, directivo
    departamento_id = Column(Integer, ForeignKey('Departamento.id'))  # Dpto/unidad asignado
    fecha_registro = Column(Date)
    colaborador = relationship('Colaborador', back_populates='contratos')
    departamento = relationship('Departamento', back_populates='contratos')

class User(Base):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Method to set hashed password
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    # Method to check password
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Create the tables in the database
Base.metadata.create_all(engine)



# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# Insert data into Empresa table
empresa_data = [
    {'id': 1, 'rut': '61.234.567-8', 'nombre': 'Empresa A', 'direccion': '123 Main St', 'telefono': '555-1234', 'giro': 'Tech'},
    {'id': 2, 'rut': '62.234.567-9', 'nombre': 'Empresa B', 'direccion': '456 Market Ave', 'telefono': '555-5678', 'giro': 'Finance'},
    {'id': 3, 'rut': '63.234.567-0', 'nombre': 'Empresa C', 'direccion': '789 Broadway Blvd', 'telefono': '555-9101', 'giro': 'Health'},
    {'id': 4, 'rut': '64.234.567-1', 'nombre': 'Empresa D', 'direccion': '321 Elm St', 'telefono': '555-1123', 'giro': 'Education'},
    {'id': 5, 'rut': '65.234.567-2', 'nombre': 'Empresa E', 'direccion': '654 Pine Rd', 'telefono': '555-1415', 'giro': 'Retail'}
]

for data in empresa_data:
    empresa = Empresa(**data)
    session.add(empresa)
session.commit()

colaborador_data = [
    {'id': 1, 'rut': '12.345.678-9', 'nombre': 'Juan', 'apellido': 'Perez', 'fecha_nacimiento': date(1980, 5, 12), 'fecha_ingreso': date(2020, 1, 15), 'telefono': '555-2345', 'salario': 2000.00, 'nacionalidad': 'Chilena'},
    {'id': 2, 'rut': '12.345.678-1', 'nombre': 'Maria', 'apellido': 'Gonzalez', 'fecha_nacimiento': date(1985, 9, 22), 'fecha_ingreso': date(2019, 3, 10), 'telefono': '555-6789', 'salario': 2500.00, 'nacionalidad': 'Chilena'},
    {'id': 3, 'rut': '13.345.678-2', 'nombre': 'Carlos', 'apellido': 'Sanchez', 'fecha_nacimiento': date(1990, 7, 18), 'fecha_ingreso': date(2021, 6, 5), 'telefono': '555-9102', 'salario': 1800.00, 'nacionalidad': 'Chilena'},
    {'id': 4, 'rut': '14.345.678-3', 'nombre': 'Ana', 'apellido': 'Rodriguez', 'fecha_nacimiento': date(1992, 11, 2), 'fecha_ingreso': date(2018, 9, 25), 'telefono': '555-1124', 'salario': 2300.00, 'nacionalidad': 'Chilena'},
    {'id': 5, 'rut': '18.145.678-4', 'nombre': 'Luis', 'apellido': 'Torres', 'fecha_nacimiento': date(1995, 2, 15), 'fecha_ingreso': date(2022, 2, 1), 'telefono': '555-1416', 'salario': 2100.00, 'nacionalidad': 'Chilena'},
    {'id': 6, 'rut': '16.245.678-5', 'nombre': 'Laura', 'apellido': 'Ramirez', 'fecha_nacimiento': date(1997, 6, 25), 'fecha_ingreso': date(2020, 8, 14), 'telefono': '555-1718', 'salario': 2400.00, 'nacionalidad': 'Chilena'},
    {'id': 7, 'rut': '16.645.678-6', 'nombre': 'Roberto', 'apellido': 'Flores', 'fecha_nacimiento': date(1987, 4, 8), 'fecha_ingreso': date(2017, 10, 12), 'telefono': '555-1920', 'salario': 2200.00, 'nacionalidad': 'Chilena'},
    {'id': 8, 'rut': '12.945.678-7', 'nombre': 'Fernanda', 'apellido': 'Morales', 'fecha_nacimiento': date(1988, 1, 3), 'fecha_ingreso': date(2021, 4, 8), 'telefono': '555-2021', 'salario': 2700.00, 'nacionalidad': 'Chilena'},
    {'id': 9, 'rut': '14.745.678-8', 'nombre': 'Jorge', 'apellido': 'Vega', 'fecha_nacimiento': date(1986, 12, 20), 'fecha_ingreso': date(2020, 3, 14), 'telefono': '555-2223', 'salario': 2600.00, 'nacionalidad': 'Chilena'},
    {'id': 10, 'rut': '10.345.678-K', 'nombre': 'Claudia', 'apellido': 'Pizarro', 'fecha_nacimiento': date(1983, 10, 30), 'fecha_ingreso': date(2016, 7, 3), 'telefono': '555-2324', 'salario': 1900.00, 'nacionalidad': 'Chilena'}
    {'id': 11, 'rut': '12.987.654-3', 'nombre': 'Jean', 'apellido': 'Baptiste', 'fecha_nacimiento': date(1990, 3, 18), 'fecha_ingreso': date(2021, 7, 12), 'telefono': '555-3456', 'salario': 2100.00, 'nacionalidad': 'Haitiana'}
]

for data in colaborador_data:
    colaborador = Colaborador(**data)
    session.add(colaborador)
session.commit()

# Insert data into AFP table
afp_data = [
    {'id': 1, 'nombre': 'AFP Capital', 'comision_porcentaje': 1.44},
    {'id': 2, 'nombre': 'AFP Cuprum', 'comision_porcentaje': 1.44},
    {'id': 3, 'nombre': 'AFP Habitat', 'comision_porcentaje': 1.27},
    {'id': 4, 'nombre': 'AFP Modelo', 'comision_porcentaje': 0.58},
    {'id': 5, 'nombre': 'AFP Planvital', 'comision_porcentaje': 1.16},
    {'id': 6, 'nombre': 'AFP Provida', 'comision_porcentaje': 1.45},
    {'id': 7, 'nombre': 'AFP Uno', 'comision_porcentaje': 0.49}
]

for data in afp_data:
    afp = AFP(**data)
    session.add(afp)
session.commit()

# Insert user and password into User table
new_user = User(username='LBrownI')
new_user.set_password('Ingreso_07')
session.add(new_user)
session.commit()

# Close the session
session.close()
