from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker

app = FastAPI()

# 1. Database Setup
DB_URL = "mysql+pymysql://root:1234@localhost:3306/labelguard_db"
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. Database Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    badge_number = Column(String(20), unique=True)

class ScanRecord(Base):
    __tablename__ = "scan_records"
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(100))
    mrp_status = Column(String(20))
    inspector_id = Column(Integer, ForeignKey("users.id"))

Base.metadata.create_all(bind=engine)

# 3. Pydantic Models
class UserCreate(BaseModel):
    name: str
    badge_number: str

class ScanRecordCreate(BaseModel):
    product_name: str
    mrp_status: str
    inspector_id: int

# 4. API Routes
@app.get("/")
def read_root():
    return {"message": "Hello SIH 2026! The backend is alive!"}

@app.post("/add-inspector")
def add_inspector(user: UserCreate):
    db = SessionLocal()
    new_user = User(name=user.name, badge_number=user.badge_number)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()
    return {"message": "Inspector added!", "user": new_user}

@app.post("/add-scan")
def add_scan(scan: ScanRecordCreate):
    db = SessionLocal()
    new_scan = ScanRecord(
        product_name=scan.product_name,
        mrp_status=scan.mrp_status,
        inspector_id=scan.inspector_id
    )
    db.add(new_scan)
    db.commit()
    db.refresh(new_scan)
    db.close()
    return {"message": "Product scan logged successfully!", "scan": new_scan}

@app.get("/get-scans")
def get_all_scans():
    db = SessionLocal()
    all_scans = db.query(ScanRecord).all()
    db.close()
    return {"scans": all_scans}
