# VipherAid

VipherAid is a Flask-based animal rescue reporting web app. It helps citizens quickly report animals in distress, lets rescuers view incoming cases, and includes pages for donations and shelter information.

## Features

- Home page for the platform overview
- Emergency reporting page for urgent cases
- Standard report page for animal rescue cases
- Rescue dashboard login for responders
- Shelter information page
- Donation page
- SQLite database support through Flask-SQLAlchemy
- Photo upload support for rescue reports

## Tech Stack

- Python
- Flask
- Flask-SQLAlchemy
- HTML / CSS / Jinja templates
- SQLite

## Project Structure

```
VipherAid/
├── app.py
├── migrate_db.py
├── requirements.txt
├── .gitignore
├── static/
│   ├── logo_cropped.png
│   ├── qrcode.jpeg
│   ├── style.css
│   └── uploads/
└── templates/
    ├── base.html
    ├── donate.html
    ├── emergency.html
    ├── index.html
    ├── report.html
    ├── rescue-login.html
    ├── rescue.html
    └── shelter.html
```

## Setup

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the app:

```bash
python app.py
```

5. Open the local URL shown in the terminal.

## Notes

- Runtime files like the local database and uploaded images are intentionally excluded from GitHub.
- The app currently uses SQLite and stores uploads in `static/uploads/`.

## Git Commands

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/VipherAid.git
git push -u origin main
```
