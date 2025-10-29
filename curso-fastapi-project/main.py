import zoneinfo
from fastapi import FastAPI, HTTPException, status
from datetime import datetime

from models import Customer, CustomerCreate, CustomerUpdate, Transaction, Invoice
from db import SessionDep, create_all_tables
from sqlmodel import select


app = FastAPI(lifespan=create_all_tables)

@app.get("/")
async def root():
    return {"message": "Hello, Janice!"}


country_timezones = {
    'CO': 'America/Bogota',
    'MX': 'America/Mexico_City',
    'AR': 'America/Argentina/Buenos_Aires',
    'BR': 'America/Sao_Paulo',
    'PE': 'America/Lima',
}


@app.get("/time/{iso_code}")
async def time(iso_code: str):
    # Co => CO
    iso = iso_code.upper()
    timezone_str = country_timezones.get(iso)
    tz = zoneinfo.ZoneInfo(timezone_str)
    return {"time": datetime.now(tz)}


db_customers: list[Customer] = []


@app.post("/customers", response_model=Customer)
async def create_customer(customer_data: CustomerCreate, session: SessionDep):
    customer = Customer.model_validate(customer_data.model_dump())
    session.add(customer)
    session.commit()    #EJECUTA LA INSERCION
    session.refresh(customer)
    return customer



@app.get("/customers/{customer_id}", response_model=Customer)
async def read_customer(customer_id: int, session: SessionDep):
    customer_db = session.get(Customer, customer_id)
    if not customer_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer doesn't exist")
    return customer_db



@app.patch("/customers/{customer_id}", response_model=Customer, status_code=status.HTTP_201_CREATED)
async def read_customer(customer_id: int, customer_data: CustomerUpdate, session: SessionDep):
    customer_db = session.get(Customer, customer_id)
    if not customer_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer doesn't exist")
    customer_data_dict = customer_data.model_dump(exclude_unset=True)
    customer_db.sqlmodel_update(customer_data_dict)
    session.add(customer_db)
    session.commit()
    session.refresh(customer_db)
    return customer_db



@app.delete("/customers/{customer_id}")
async def delete_customer(customer_id: int, session: SessionDep):
    customer_db = session.get(Customer, customer_id)
    if not customer_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer doesn't exist")
    
    session.delete(customer_db)
    session.commit()
    return {"detail": "Customer deleted"}





@app.get("/customers", response_model=list[Customer])
async def list_customer(session: SessionDep):
    return session.exec(select(Customer)).all()



@app.post("/transactions")
async def create_transaction(transaction_data: Transaction):

    return transaction_data

@app.post("/invoices")
async def create_invoice(invoice_data: Invoice):

    return invoice_data