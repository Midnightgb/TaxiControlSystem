[![CodeFactor](https://www.codefactor.io/repository/github/midnightgb/taxicontrolsystem/badge)](https://www.codefactor.io/repository/github/midnightgb/taxicontrolsystem)
[![Spanish Badge](app-screenshots/icons8-espa%C3%B1a2-circular-48.png)](readme-es.md) For the spanish version
# TaxiControlSystem
TaxiControlSystem - Fleet management software for efficient taxi operations

# Screenshots
### Login
![Login](app-screenshots/login.png){width=900px}

### Dashboard
![Dashboard](app-screenshots/home.png){width=900px}

## Drivers
![Drivers](app-screenshots/users.png){width=900px}

#### Driver Registration
![Driver Reports](app-screenshots/register-user.png){width=900px}

#### Driver Reports
![Driver Reports](app-screenshots/user-report.png){width=900px}

#### Driver Report Payment
![Driver Report Payment](app-screenshots/user-report-payment.png){width=900px}

#### Driver Report Update Payment
![Driver Report Update Payment](app-screenshots/user-report-update-payment.png){width=900px}

#### Driver Report Update Vehicle Information
![Driver Report Update Vehicle Information](app-screenshots/user-report-update-car-info.png){width=900px}

#### Driver Report Update Driver Information
![Driver Report Update Driver Information](app-screenshots/user-report-update-info.png){width=900px}

## Vehicles
![Vehicles](app-screenshots/vehicles.png){width=900px}

#### Vehicle Registration
![Vehicle Registration](app-screenshots/register-vehicle.png){width=900px}

#### Vehicle Reports
![Vehicle Reports](app-screenshots/vehicle-report.png){width=900px}

#### Vehicle Maintenance
![Vehicle Maintenance](app-screenshots/vehicle-register-maintenance.png){width=900px}

# For Bug Reporting
### Please create an issue with the following information
```bash
1. What you were trying to do
2. What you expected to happen
3. What actually happened
4. Steps to reproduce the problem
5. Screenshots if possible
```

# For live demo
## Install Python dependencies
you need to be in the app directory to run the following commands
```bash
conda create --name taxicontrol python=3.9 
conda activate taxicontrol
pip install -r requirements.txt
```

## Create the database
```bash
insert TaxiControlSystemDATA.sql into your database management system
```

## Run the app
```bash
uvicorn main:app --reload
```

# Login credentials
```bash
username: "1234" or "admin@admin.com"
password: admin
```

# Only for development

## Install NodeJS dependencies
you need to be in the app directory to run the following commands
```bash
npm install
```

## Run TailwindCSS
```bash
npx tailwindcss -i ./public/dist/css/tailwind/input.css -o ./public/dist/css/tailwind/output.css --watch
```
