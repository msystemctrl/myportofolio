# Portfolio — Marsya Rizka Aulia

| | |
|---|---|
| **Course** | Platform-Based Programming (PBP) |
| **NPM** | 2506537606 |
| **Class** | PBP E |
| **Faculty** | Faculty of Computer Science, Universitas Indonesia |
| **Lecturer** | Daya Adianto, S.Kom., M.Kom. |

## About the Project

A personal portfolio website featuring an organizational history, academic background, completed projects, and a photo gallery, built on Django and deployed to PWS.

## Deployment

[marsya-rizka-myportofolio.pws.cs.ui.ac.id](https://marsya-rizka-myportofolio.pws.cs.ui.ac.id)

## Installation and Deployment

### Requirements

- Python 3.10+
- pip
- Git

### Local Preview

Clone this repository
```bash
git clone https://github.com/<username>/myportofolio.git
cd myportofolio
```

Create a virtual environment
```bash
python -m venv env

# Windows (cmd/PowerShell)
env\Scripts\activate

# Unix (macOS/Linux)
source env/bin/activate
```

Install dependencies
```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root for local configuration:
```
PRODUCTION=False
```

Run migrations and start the server
```bash
python manage.py migrate  # local development uses SQLite by default
python manage.py runserver
```

Then open `http://127.0.0.1:8000/`.

### Deployment

Production uses PostgreSQL. Create a new project on [PWS](https://pws.cs.ui.ac.id), then set the following environment variables under the **Environs** tab:
```
PRODUCTION=True

DB_NAME=<database-name>
DB_USER=<database-user>
DB_PASSWORD=<database-password>
DB_HOST=<database-host>
DB_PORT=<database-port>
SCHEMA=tutorial
```

Add the PWS deployment URL to `ALLOWED_HOSTS` in `settings.py`, and make sure `WhiteNoiseMiddleware` is enabled so static files are served correctly in production.

To push changes to PWS:
```bash
git add .
git commit -m "chore: deploy"
git push pws main:master
```

## Assignments & Reflections

| No. | Topic | Answer |
|---|---|---|
| 1 | Static Web with HTML5 and CSS3 | [TUGAS1.md](/essay/Tugas1.md) |

## Credits

Individual project for the PBP course, Fasilkom UI.