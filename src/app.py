from fastapi import FastApi
from src.lifespan import lifespan


app = FastApi(lifespan=lifespan)
