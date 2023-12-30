import uvicorn
from api import app

app = app

if __name__ == '__main__':
    uvicorn.run("main:app", port=1111, host='0.0.0.0', reload=True)