from fastapi import FastAPI, Depends

from app.core.db import init_db
from app.core.config import process_environment_variables, get_processed_environment_variables
from app.core.utils import VerifyToken
from app.users.router import users_router


app = FastAPI()


@app.on_event("startup")
async def startup_event():
    await process_environment_variables()
    auth = VerifyToken()
    app.include_router(users_router, prefix="/users", tags=["users"], dependencies=[Depends(auth.verify)])
    init_db()
