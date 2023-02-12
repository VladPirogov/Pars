from fastapi import FastAPI
from .della_parser import parser_site, get_file

# Initializing app
app = FastAPI()


@app.get("/")
async def ping():
    return {'version': '0.1',
            'name': 'della parser system',
            'documentation': 'go to /docs'}


@app.get("/start_pars")
async def start_pars():
    return parser_site()


@app.get("/get_data_file")
def get_data_file():
    return get_file()

