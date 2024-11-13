from db.session import engine
from db.base_class import Base
from fastapi import FastAPI
from core.config import settings
from apis.base import api_router

def include_router(app):
    app.include_router(api_router)



def start_application():
    app=FastAPI(title=settings.PROJECT_TITLE,version=settings.PROJECT_VERSION)  
    include_router(app)
    return app 


app=start_application()

