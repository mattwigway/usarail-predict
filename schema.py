from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Date, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry
from datetime import datetime

Base = declarative_base()
Base.metadata.schema = 'amtrak'

class Route(Base):
    __tablename__ = 'routes'
    
    number = Column(Integer, primary_key=True)
    name = Column(String)
    trains = relationship("Train", backref='route')

class Train(Base):
    __tablename__ = 'trains'

    fid = Column(Integer, primary_key=True)
    trainNumber = Column(Integer, ForeignKey('routes.number'))
    depDate = Column(Date)
    completed = Column(Boolean)
    statuses = relationship("TrainStatus", backref='train')

class TrainStatus(Base):
    __tablename__ = 'trainstatus'

    fid = Column(Integer, primary_key=True)
    trainId = Column(Integer, ForeignKey('trains.fid'))
    velocity = Column(Numeric(15,12))
    status = Column(Enum('Active', 'Completed', 'Predeparture', name='trainstatus'))
    retrieved = Column(DateTime(timezone=False)) # store in UTC
    the_geom = Column(Geometry)
    
    stations = relationship('StationStatus', backref='trainStatus')

class StationStatus(Base):
    __tablename__ = 'stationstatus'

    fid = Column(Integer, primary_key=True)
    number = Column(Integer)
    schedArr = Column(DateTime(timezone=True))
    schedDep = Column(DateTime(timezone=True))
    estArr   = Column(DateTime(timezone=True))
    estDep   = Column(DateTime(timezone=True))
    actArr   = Column(DateTime(timezone=True))
    actDep   = Column(DateTime(timezone=True))
    
    trainStatusId = Column(Integer, ForeignKey('trainstatus.fid'))
    stationId = Column(String, ForeignKey('stations.code'))

class Station(Base):
    __tablename__ = 'stations'

    code = Column(String, primary_key=True)
    name = Column(String)
    the_geom = Column(Geometry)

    statuses = relationship('StationStatus', backref='station')
