from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from typing import List

db = SQLAlchemy()

class User(db.Model):

    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    employee_id: Mapped[str] = mapped_column(String(7), unique=True, nullable=False)
    role: Mapped[str] = mapped_column(String(128), nullable=False)

    # Permisos que el usuario ha solicitado
    requests_made: Mapped[list["Permit"]] = relationship('Permit', back_populates='user_requester', foreign_keys='Permit.requester_id')

    # Permisos que el usuario ha aprobado
    approvals_made: Mapped[list["Permit"]] = relationship('Permit', back_populates='user_approver', foreign_keys='Permit.approver_id')

    # Conexion con Department
    departement_id: Mapped[int] = mapped_column(Integer, ForeignKey('departments.id'))

    department: Mapped['Department'] = relationship('Department', back_populates='users')

    

    def __repr__(self):
        return f'<User {self.email}>'

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "employee_id": self.employee_id,
            "role":self.role,

            # do not serialize the password, its a security breach
        }
    

class Department(db.Model):
    __tablename__ = 'departments'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    users: Mapped[list['User']] = relationship('User', back_populates='department')

    def __repr__(self):
        return f'<Department {self.name}>'

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
        }


# Tabla intermedia entre PersonalInfo y Permit para manejar la relación muchos a muchos
personal_info_permits = db.Table(
    'personal_info_permits',
    db.Model.metadata,
    db.Column('personal_info_id', db.Integer, db.ForeignKey('personal_info.id'), primary_key=True),
    db.Column('permit_id', db.Integer, db.ForeignKey('permits.id'), primary_key=True)
)

# Tabla intermedia para la relación N:N entre Permisos y Station
permit_station = db.Table('permit_station',
    db.Column('permit_id', db.Integer, db.ForeignKey('permits.id'), primary_key=True),
    db.Column('station_id', db.Integer, db.ForeignKey('stations.id'), primary_key=True)
)

    
class Permit(db.Model):

    __tablename__ = 'permits'
    id: Mapped[int] = mapped_column(primary_key=True)
    control_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='pending')
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)


    # Relacion con PersonalInfo
    # Relación N:N inversa
    people: Mapped[list['PersonalInfo']] = relationship(
        'PersonalInfo', 
        secondary=personal_info_permits, # <-- Misma tabla intermedia
        back_populates='permits'
    )
    # Foreign keys
    requester_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    approver_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=True)

    # Relaciones
    user_requester: Mapped['User'] = relationship('User', back_populates='requests_made', foreign_keys=[requester_id])
    user_approver: Mapped['User'] = relationship('User', back_populates='approvals_made', foreign_keys=[approver_id])

    # Relación N:N con Station
    stations: Mapped[list['Station']] = relationship(
        'Station',
        secondary=permit_station,
        back_populates='permits'
    )

    def __repr__(self):
        return f'<Permit {self.type} from {self.start_date} to {self.end_date}>'
    
    def serialize(self):
        return {
        "id": self.id,
        "control_number": self.control_number,
        "type": self.type,
        "status": self.status,
        "start_date": self.start_date.isoformat(),
        "end_date": self.end_date.isoformat(),
        "requester_id": self.requester_id,
        "approver_id": self.approver_id,
        "stations": [s.name for s in self.stations],
        # Serializamos datos básicos de las personas para evitar el bucle
        "people": [
            {
                "id": person.id,
                "full_name": person.full_name
            } for person in self.people
        ]
    }


class Station(db.Model):
    __tablename__ = 'stations'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    coordenates: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(String(200), nullable=False)
    
    # Dependencia con Contact Station
    contacts: Mapped[list['ContactStation']] = relationship('ContactStation', back_populates='station')
    # Dependencias con Region
    region_id: Mapped[int] = mapped_column(Integer, ForeignKey('region.id'))
    region: Mapped['Region'] = relationship('Region', back_populates='station')

    # Dependencias con Market
    market_id: Mapped[int] = mapped_column(Integer, ForeignKey('market.id'))
    market: Mapped['Market'] = relationship('Market', back_populates='station')

    # Dependencia con Permit
    permits: Mapped[list['Permit']] = relationship(
        'Permit',
        secondary=permit_station,
        back_populates='stations'
    )

    def __repr__(self):
        return f'<Station {self.name}>'

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "contacts":self.contacts,
            "region":self.region,
            'market': self.market,
            "permits": [p.id for p in self.permits]


        }
    

class Region(db.Model):
    __tablename__= 'region'

    id: Mapped[int] = mapped_column(primary_key=True)
    region: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # Dependencias con Station
    station: Mapped['Station'] = relationship('Station', back_populates='region')

    # Dependencias con Market
    market: Mapped['Market'] = relationship('Market', back_populates='region')


    def __repr__(self):
        return f'<Region {self.region}>'
    
    def serialize(self):
        return {
            "id": self.id,
            "region": self.region,
            "station_id": self.station_id,
            "market_id": self.market_id,
        }


class ContactStation(db.Model):
    __tablename__ = 'contactstations'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)

    # Dependencia con Contact Station
    station_id: Mapped[int] = mapped_column(Integer, ForeignKey('stations.id'))
    station: Mapped['Station'] = relationship('Station', back_populates='contacts')


    def __repr__(self):
        return f'<Contact {self.name}>'

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "station_id": self.station_id,

        }

class Market(db.Model):
    __tablename__ = 'market'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # Dependencias con Station
    #station_id: Mapped[int] = mapped_column(Integer, ForeignKey('station.id'))
    station: Mapped['Station'] = relationship('Station', back_populates='market')

    # Dependencias con Region
    region_id: Mapped[int] = mapped_column(Integer, ForeignKey('region.id'))
    region: Mapped['Region'] = relationship('Region', back_populates='market')

    def __repr__(self):
        return f'<Market {self.name}>'

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "station_id": self.station_id,
            "region_id": self.region_id,
        }
    
class PersonalInfo(db.Model):
    __tablename__ = 'personal_info'
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    national_id: Mapped[str] = mapped_column(String(7), unique=True, nullable=False)
    is_allow: Mapped[bool] = mapped_column(db.Boolean, default=False)


    contractor: Mapped['Contractor'] = relationship('Contractor', back_populates='personal_info', uselist=False)

    # Relacion con Permit
    permits: Mapped[list['Permit']] = relationship(
        'Permit', 
        secondary=personal_info_permits, # <-- relacion muchos a muchos
        back_populates='people'
    )
    def __repr__(self):
        return f'<PersonalInfo {self.full_name}>'

    def serialize(self):
        return {
        "id": self.id,
        "full_name": self.full_name,
        "national_id": self.national_id,
        "is_allow": self.is_allow,
        "contractor": self.contractor,
        
        "permits": [
            {
                "id": p.id,
                "control_number": p.control_number,
                "status": p.status
            } for p in self.permits
        ]
    }

class Contractor(db.Model):
    __tablename__ = 'contractors'
    id: Mapped[int] = mapped_column(primary_key=True)
    company_name: Mapped[str] = mapped_column(String(100), nullable=False)
    contact_email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    contact_phone: Mapped[str] = mapped_column(String(20), nullable=False)

    # Relacion con PersonalInfo
    personal_info_id: Mapped[int] = mapped_column(Integer, ForeignKey('personal_info.id'), nullable=False)
    personal_info: Mapped['PersonalInfo'] = relationship('PersonalInfo', back_populates='contractor', uselist=False)

    def __repr__(self):
        return f'<Contractor {self.company_name}>'

    def serialize(self):
        return {
            "id": self.id,
            "company_name": self.company_name,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "personal_info_id": self.personal_info_id,
        }
    

