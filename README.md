# Retro Arkanoid with Flask

Aplicacion web de Arkanoid construida con Flask. El juego se ejecuta en un canvas HTML5 y esta rama añade acceso con Google, persistencia en SQLite y soporte para jugar desde otros equipos de tu red local.

## Requisitos

- Windows con `pyenv-win` disponible como `pyenv`
- Python `3.12.7`
- Un cliente OAuth de Google configurado como aplicacion web

## Configuracion con pyenv-win

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

## Configuracion de Google OAuth

Copia `.env.example` a `.env` y rellena estos valores:

- `SECRET_KEY`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `DATABASE_URL` opcional; por defecto usa SQLite local en `instance/arkanoid.db`
- `HOST` con `0.0.0.0`
- `PORT` con `5000`
- `BASE_URL` con la IP local del PC anfitrion, por ejemplo `http://192.168.1.25:5000`

En Google Cloud Console debes anadir los redirect URI que vayas a usar. Como minimo:

```text
http://127.0.0.1:5000/auth/google/callback
http://TU_IP_LOCAL:5000/auth/google/callback
```

## Ejecutar la aplicacion en la red local

Inicia la app con:

```powershell
python app.py
```

La app escuchara por defecto en todas las interfaces de red (`0.0.0.0:5000`).

Para saber la IP local del ordenador anfitrion puedes usar:

```powershell
ipconfig
```

Busca la direccion IPv4 de tu adaptador activo y abre desde otro equipo de la misma red:

```text
http://TU_IP_LOCAL:5000
```

## Firewall de Windows

Si otro equipo no puede entrar, permite el puerto `5000` en el Firewall de Windows o acepta la excepcion cuando Windows la solicite al arrancar Flask.

## Juego y persistencia

- Los usuarios deben autenticarse con Google antes de jugar.
- Cada partida terminada se guarda en SQLite.
- La puntuacion maxima aparece al iniciar sesion.
- La barra lateral muestra las partidas recientes guardadas.
- Controles: flechas izquierda y derecha o `A` y `D`, `Espacio` y `R`.
