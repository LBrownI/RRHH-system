from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DECIMAL, Date, Text, Boolean
from sqlalchemy import text
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker


config = {'host': 'localhost', 'database_name': 'mycardb', 'user': 'root', 'password': 'rootpass'}
engine = create_engine(f'mysql+pymysql://{config["user"]}:{config["password"]}@{config["host"]}/{config["database_name"]}', echo=True)

with engine.connect() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {config['database_name']}"))

Base = declarative_base()

# Empresa model
class Empresa(Base):
    __tablename__ = 'Empresa'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    direccion = Column(String(255))
    telefono = Column(String(20))
    giro = Column(String(100))

# Colaborador model
class Colaborador(Base):
    __tablename__ = 'Colaborador'
    id = Column(Integer, primary_key=True)
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

# Create the tables in the database
Base.metadata.create_all(engine)



# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# Insert data into Model table
company_data = [
    {'ModelID': 1, 'Make': 'Toyota', 'ModelName': 'Camry'},
    {'ModelID': 2, 'Make': 'Honda', 'ModelName': 'Civic'},
    {'ModelID': 3, 'Make': 'Ford', 'ModelName': 'Mustang'}
]
for data in company_data:
    empresa = Empresa(**data)
    session.add(empresa)
    session.commit()

# Insert data into Cars table
car_data = [
    {'CarID': 1, 'ModelID': 1, 'Year': 2023, 'Color': 'Silver', 'VIN': '1A2B3C4D5E', 'Mileage': 5000, 'Price': 25000.00},
    {'CarID': 2, 'ModelID': 2, 'Year': 2022, 'Color': 'Blue', 'VIN': '6F7G8H9J0K', 'Mileage': 10000, 'Price': 20000.00},
    {'CarID': 3, 'ModelID': 3, 'Year': 2021, 'Color': 'Red', 'VIN': '1L2M3N4O5P', 'Mileage': 15000, 'Price': 30000.00},
    {'CarID': 4, 'ModelID': 1, 'Year': 2020, 'Color': 'Black', 'VIN': '6Q7R8S9T0U', 'Mileage': 20000, 'Price': 22000.00},
    {'CarID': 5, 'ModelID': 2, 'Year': 2019, 'Color': 'White', 'VIN': '1V2W3X4Y5Z', 'Mileage': 25000, 'Price': 18000.00},
    {'CarID': 6, 'ModelID': 3, 'Year': 2018, 'Color': 'Gray', 'VIN': '6A7B8C9D0E', 'Mileage': 30000, 'Price': 28000.00},
    {'CarID': 7, 'ModelID': 1, 'Year': 2017, 'Color': 'Green', 'VIN': '1F2G3H4J5K', 'Mileage': 35000, 'Price': 15000.00},
    {'CarID': 8, 'ModelID': 2, 'Year': 2024, 'Color': 'Pearl White', 'VIN': '6L7M8N9O0P', 'Mileage': 1000, 'Price': 23000.00},
    {'CarID': 9, 'ModelID': 3, 'Year': 2023, 'Color': 'Burgundy', 'VIN': '1Q2R3S4T5U', 'Mileage': 3000, 'Price': 32000.00},
    {'CarID': 10, 'ModelID': 1, 'Year': 2022, 'Color': 'Sand', 'VIN': '6V7W8X9Y0Z', 'Mileage': 8000, 'Price': 24000.00}
]
for data in car_data:
    car = Car(**data)
    session.add(car)

# Commit the changes to the database
session.commit()

# Close the session
session.close()
