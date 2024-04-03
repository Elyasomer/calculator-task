from fastapi import Depends, FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from db import Base, sync_engine, get_session, AsyncSession, Calculations

app = FastAPI()


origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=sync_engine)

class CalcInput(BaseModel):
    stmnt: str
    answer: str


class CalcOutput(BaseModel):
    id: int
    stmnt: str
    answer: str


@app.post("/calculations", response_model=CalcOutput)
async def save_calcultaion(calc: CalcInput, db: AsyncSession = Depends(get_session)):
    calc = Calculations(stmnt=calc.stmnt, answer=calc.answer)
    db.add(calc)
    await db.commit()
    await db.refresh(calc)

    return calc
