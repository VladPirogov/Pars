from fastapi import FastAPI

# Initializing app
app = FastAPI()


@app.get("/")
def ping():
    return {'version': '0.1',
            'name': 'della parser system',
            'documentation': 'go to /docs'}






