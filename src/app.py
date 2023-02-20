from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from src.parsers import DellParser
from fastapi_pagination.ext.pymongo import paginate

# Initializing app
app = FastAPI()


@app.on_event("startup")
@repeat_every(seconds=300)
async def startup_event():
    DellParser().parser_site()


@app.get("/")
async def ping():
    return {'version': '0.1',
            'name': 'della parser system',
            'documentation': 'go to /docs'}


@app.get("/fors_pars")
async def start_pars():
    return DellParser().parser_site()


@app.get('/cards')
async def get_cards():
    return paginate()


@app.get("/get_data_file")
def get_data_file():
    return DellParser().get_file()
