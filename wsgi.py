import uvicorn
from src import app

if __name__ == "__main__":
    uvicorn.run(app, port=5000, log_level="info")