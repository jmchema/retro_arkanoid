# Retro Arkanoid with Flask

Aplicacion web de Arkanoid construida con Flask. El juego se ejecuta en un canvas HTML5, usa autenticacion con Google y guarda partidas y puntuaciones. El proyecto puede desplegarse con Docker Compose en dos modos: limpio para VPS y con certificado corporativo para intranet.

## Requisitos para desarrollo local

- Windows con `pyenv-win` disponible como `pyenv`
- Python `3.12.7`
- Un cliente OAuth de Google configurado como aplicacion web

## Configuracion local con pyenv-win

Instala y selecciona la version local de Python:

```powershell
pyenv install 3.12.7
pyenv local 3.12.7
```

Crea y activa el entorno virtual:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Instala las dependencias:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Variables de entorno

Copia `.env.example` a `.env` y rellena estos valores:

- `SECRET_KEY`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `DATABASE_URL`
- `HOST`
- `PORT`
- `BASE_URL`
- `FLASK_DEBUG`

### Valores recomendados en Docker

```env
DATABASE_URL=sqlite:////app/instance/arkanoid.db
HOST=0.0.0.0
PORT=5000
BASE_URL=https://tu-dominio-o-url-publica
FLASK_DEBUG=0
```

## Google OAuth

En Google Cloud Console debes anadir un redirect URI que coincida exactamente con tu `BASE_URL`:

```text
https://tu-dominio-o-url-publica/auth/google/callback
```

Si trabajas en local fuera de Docker, puedes seguir usando tambien:

```text
http://127.0.0.1:5000/auth/google/callback
```

## Docker Compose para VPS o entornos limpios

### Archivos

- `Dockerfile`: imagen base limpia, sin certificados corporativos
- `docker-compose.yml`: despliegue estandar para VPS o entornos sin proxy corporativo

### Arranque

```powershell
docker-compose up --build -d
```

### Logs

```powershell
docker-compose logs -f web
```

### Parada

```powershell
docker-compose down
```

## Docker Compose para intranet corporativa

### Archivos

- `Dockerfile.intranet`: variante de la imagen que instala `lala.crt`
- `docker-compose.intranet.yml`: override para usar el Dockerfile corporativo y las variables CA

### Requisitos

- Coloca `lala.crt` en la raiz del proyecto antes de construir
- Ese certificado no debe formar parte del despliegue del VPS

### Arranque en intranet

```powershell
docker-compose -f docker-compose.yml -f docker-compose.intranet.yml up --build -d
```

### Ver configuracion final de intranet

```powershell
docker-compose -f docker-compose.yml -f docker-compose.intranet.yml config
```

## Persistencia

Docker Compose crea un volumen llamado `arkanoid_instance` y monta `/app/instance` dentro del contenedor. Ahi se guarda el fichero SQLite, por lo que los datos sobreviven a reinicios del contenedor.

## Comprobaciones recomendadas

- VPS: `docker-compose config`
- Intranet: `docker-compose -f docker-compose.yml -f docker-compose.intranet.yml config`
- Abrir `http://localhost:5000`
- Iniciar sesion con Google usando una `BASE_URL` autorizada
- Jugar una partida y confirmar que se guarda
- Reiniciar el contenedor y comprobar que la puntuacion maxima sigue estando disponible

## Notas importantes

- La app usa `gunicorn` en Docker, no el servidor de desarrollo de Flask.
- Para despliegue real con Google OAuth necesitas una URL publica valida en `BASE_URL`.
- Una IP privada local no es valida como callback de Google para una aplicacion web publicada.
- `lala.crt` queda reservado al flujo de intranet y esta ignorado por Git para no contaminar el despliegue del VPS.
