[![CodeFactor](https://www.codefactor.io/repository/github/midnightgb/taxicontrolsystem/badge)](https://www.codefactor.io/repository/github/midnightgb/taxicontrolsystem)
[![English Badge](app-screenshots/icons8-circular-de-ee-uu-48.png)](README.md) For the english version
# TaxiControlSystem
TaxiControlSystem - Software de gestión de flotas para operaciones de taxi eficientes

# Capturas de pantalla
## Inicio de sesión
![Login](app-screenshots/login.png){width=900px}

## Panel de control
![Dashboard](app-screenshots/home.png){width=900px}

## Conductores
![Drivers](app-screenshots/users.png){width=900px}

### Registro de conductor
![Driver Reports](app-screenshots/register-user.png){width=900px}

### Informes de conductores
![Driver Reports](app-screenshots/user-report.png){width=900px}

### Pago del conductor
![Driver Report Payment](app-screenshots/user-report-payment.png){width=900px}

### Actualizar pago del conductor
![Driver Report Update Payment](app-screenshots/user-report-update-payment.png){width=900px}

### Actualizar información del vehículo
![Driver Report Update Vehicle Information](app-screenshots/user-report-update-car-info.png){width=900px}

### Actualizar información del conductor
![Driver Report Update Driver Information](app-screenshots/user-report-update-info.png){width=900px}

## Vehículos
![Vehicles](app-screenshots/vehicles.png){width=900px}

### Registro de vehículos
![Vehicle Registration](app-screenshots/register-vehicle.png){width=900px}

### Informes de vehículos
![Vehicle Reports](app-screenshots/vehicle-report.png){width=900px}

### Mantenimiento de vehículos
![Vehicle Maintenance](app-screenshots/vehicle-register-maintenance.png){width=900px}

# Para informar de errores
## Cree un problema con la siguiente información
```bash
1. Lo que estabas intentando hacer
2. Lo que esperabas que sucediera
3. Lo que realmente sucedió
4. Pasos para reproducir el problema
5. Capturas de pantalla si es posible
```

# Para demostración en vivo
## Instalar dependencias de Python
debe estar en el directorio de la aplicación para ejecutar los siguientes comandos
```bash
pip install -r requirements.txt
```

## Configurar la base de datos
```bash
insert TaxiControlSystemDATA.sql en su sistema de gestión de bases de datos
```

## Ejecutar la aplicación
```bash
uvicorn main:app --reload
```

## Credenciales de inicio de sesión
```bash
usuario: "1234" o "admin@admin.com"
contraseña: admin
```


# Para contribuir
### Instalar dependencias de Python y Configurar la base de datos
## Instalar dependencias de NodeJS
debe estar en el directorio de la aplicación para ejecutar los siguientes comandos
```bash
npm install
```

## Ejecutar TailwindCSS
```bash
npx tailwindcss -i ./public/dist/css/tailwind/input.css -o ./public/dist/css/tailwind/output.css --watch
```




