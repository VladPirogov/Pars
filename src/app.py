from fastapi import BackgroundTasks, FastAPI
from src.parsers import DellParser, LoopDellParser

# Initializing app
app = FastAPI()


@app.get("/")
async def ping():
    return {'version': '0.1',
            'name': 'della parser system',
            'documentation': 'go to /docs'}


@app.get("/start_pars")
async def start_pars():
    return DellParser().parser_site()


@app.get("/get_data_file")
def get_data_file():
    return DellParser().get_file()
