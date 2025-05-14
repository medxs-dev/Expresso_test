from app.core.db import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean, Date

# from app.config.db import Base
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geometry


class StoreOwnerModel(Base):
    __tablename__ = "exp_store_owners"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    dob = Column(Date, nullable=False)
    gender_id = Column(Integer, ForeignKey(
        "exp_gender_master.id"), nullable=False)
    age = Column(Integer, nullable=True)  # can be calculated, optional
    email = Column(String(100), unique=True, nullable=True)
    mobile = Column(String(15), unique=True, nullable=False)
    phone = Column(String(15), nullable=True)
    current_addr = Column(String(255), nullable=False)
    permanent_addr = Column(String(255), nullable=True)
    created_by = Column(Integer, nullable=False)
    updated_by = Column(Integer, nullable=True)
    created_on = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    updated_on = Column(DateTime(timezone=True),
                        onupdate=func.now(), nullable=True)
