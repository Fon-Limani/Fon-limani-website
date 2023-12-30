# Fon Limanı

To run the application:

### Option 1: Use Docker

0 - Change the .env files in both folders according to your informations.

1 - Install Docker and start the Docker service:

1.1 - From terminal:

```bash
yum install docker git -y
systemctl restart docker
```

1.2 - Using Docker Desktop:

1.2.1 - Install Docker Desktop from [Docker website](https://www.docker.com/products/docker-desktop/)

1.2.2 - Open Docker Desktop

2 -  Install Docker Compose:

2.1 - From terminal:

```bash
sudo curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose version
```
2.2 - Using Docker Desktop: It comes with the Docker Desktop

3 - Build & Run: Create images and run the whole application. 

```bash
docker-compose up --build
```

### Option 2: Create a New Env

0 - Change the .env_merge file according to your informations. Change the file's name from .env_merge to .env

1 - Create a new environment:

1.1 - Python 3.10 is a must for the project. If you have anaconda with an another version of python, create a new environment called `python310`:

```bash
conda create -n py310 python=3.10
```

Then, activate the conda environment:

```bash
conda actiavte py310
```

1.2 - If you have python 3.10.x, continue from here:

```bash
python3.10.6 -m venv venv
```

2 - Activate venv:

```bash
venv\Scripts\activate.bat
```

3 - Install requirements:

```bash
pip install -r requirements.txt
```

4 - In a terminal, activate venv and run (if you are using conda, activate venv after activating py310)

```bash
python backend/main.py
```

5 - In another terminal, run (if you are using conda, activate venv after activating py310)

```bash
python frontend/main.py
```

Go to your browser and access the project:

> Backend Link -> localhost:1111

> Frontend Link -> localhost:5000


## Demo ( Click to watch video )

[![Demo ( Click to watch video )](https://lh3.googleusercontent.com/u/0/drive-viewer/AEYmBYT15yH6dC7NXVLZKKUI3852oGdls0hoZJRUgZZ-YvCef_HpvM-MqtIAKiAaO_-zS2K7z9SQ3c6tskjPsJviUQwksqUQ=w1920-h1080-k-pd)](https://drive.google.com/file/d/1eAqdcN6NHRK1JDSAQnWShdfb1ZKZ1CnU/preview)

## Known Issues

1. When someone tries to request without selection the program crashes due to unknown data pass.
2. When someone tries to pick a date on the weekend, the functions related to datetime won't work.
3. Can not upload a profile picture currently.

## Issues That Need Improvements

1. API UI
2. Admin Page
3. Multiple Pages for default website
4. 400, 404, 500 Page UI's
