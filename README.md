# Descargar el proyecto

## Clonar el repositorio
git clone https://github.com/ctrbts/asistencia-becarios.git
cd asistencia-becarios

## Crea e instala dependencias en un entorno virtual
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

## Crea tu archivo .env con los datos correctos
nano .env

## Despliegue en servidor 🚀
Instalar Prerrequisitos en el Servidor

    sudo apt update
    sudo apt install python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx curl

Configurar la base de datos PostgreSQL

    sudo -u postgres psql
    postgres=# CREATE DATABASE mi_asistencia_db;
    postgres=# CREATE USER mi_usuario WITH PASSWORD 'mi_contraseña_segura';
    postgres=# ALTER ROLE mi_usuario SET client_encoding TO 'utf8';
    postgres=# ALTER ROLE mi_usuario SET default_transaction_isolation TO 'read committed';
    postgres=# ALTER ROLE mi_usuario SET timezone TO 'UTC';
    postgres=# GRANT ALL PRIVILEGES ON DATABASE mi_asistencia_db TO mi_usuario;
    postgres=# \q

Actualiza la DATABASE_URL en tu archivo .env con estos datos.


# Configurar el Proyecto
## Ejecuta los comandos de Django

    python manage.py migrate
    python manage.py collectstatic --noinput # Recolecta todos los archivos estáticos
    python manage.py createsuperuser

## Configurar Gunicorn con systemd
systemd gestionará el proceso de Gunicorn.

    sudo nano /etc/systemd/system/gunicorn.service

Pega la siguiente configuración, ajustando las rutas y nombres de usuario:

    Ini, TOML

    [Unit]
    Description=gunicorn daemon para la app de asistencia
    After=network.target

    [Service]
    User=tu_usuario          # El usuario con el que corre el proceso
    Group=www-data
    WorkingDirectory=/home/tu_usuario/asistencia-becarios
    ExecStart=/home/tu_usuario/asistencia-becarios/.venv/bin/gunicorn \
            --access-logfile - \
            --workers 3 \
            --bind unix:/run/gunicorn.sock \
            mi_proyecto.wsgi:application

    [Install]
    WantedBy=multi-user.target

## Inicia y habilita Gunicorn:

    sudo systemctl start gunicorn
    sudo systemctl enable gunicorn

Configurar Nginx como Reverse Proxy
Crea un archivo de configuración para tu sitio:

    sudo nano /etc/nginx/sites-available/asistencia

Pega la siguiente configuración, ajustando server_name:

    server {
        listen 80;
        server_name la_ip_de_tu_servidor www.tu_dominio.com;

        location = /favicon.ico { access_log off; log_not_found off; }

        # Sirve los archivos estáticos directamente
        location /static/ {
            root /home/tu_usuario/asistencia-becarios;
        }

        # Pasa el resto de las peticiones a Gunicorn
        location / {
            include proxy_params;
            proxy_pass http://unix:/run/gunicorn.sock;
        }
    }

Activa la configuración y reinicia Nginx:

    sudo ln -s /etc/nginx/sites-available/asistencia /etc/nginx/sites-enabled
    sudo nginx -t # Para probar que no hay errores de sintaxis
    sudo systemctl restart nginx