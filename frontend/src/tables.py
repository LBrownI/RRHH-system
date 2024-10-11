import os
from sqlalchemy import create_engine, text, Column, Integer, String, ForeignKey, DECIMAL, Date, Text, Boolean
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash

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
    bonuses = relationship("Bonus", back_populates="remuneracion")

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
    descuento = Column(DECIMAL(10, 2))  # Different from Isapre's discount
    plan_salud = relationship('PlanDeSalud', back_populates='fonasa')

class Isapre(Base):
    __tablename__ = 'Isapre'
    id = Column(Integer, primary_key=True)
    plan_salud_id = Column(Integer, ForeignKey('PlanDeSalud.id'))
    descuento = Column(DECIMAL(10, 2))  # Different from Fonasa's discount
    plan_salud = relationship('PlanDeSalud', back_populates='isapre')

class Bonus(Base):
    __tablename__ = 'Bonus'
    id = Column(Integer, primary_key=True)
    remuneracion_id = Column(Integer, ForeignKey('Remuneracion.id'))
    aporte = Column(DECIMAL(10, 2))  # Help for the employee for a discount in money
    beneficio = Column(DECIMAL(10, 2)) # Help for the employee as a monetary aid
    remuneracion = relationship("Remuneracion", back_populates="bonuses")

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