## Table of Contents

<!-- TOC -->

- [Table of Contents](#table-of-contents)
- [Instalación y uso](#instalación-y-uso)
  - [Descarga o clona el proyecto](#descarga-o-clona-el-proyecto)
  - [Instalar Pyenv](#instalar-pyenv)
  - [Instalar Poetry](#instalar-poetry)
  - [Instalar el proyecto](#instalar-el-proyecto)
  - [Ejecutar los tests](#ejecutar-los-tests)
  - [Ejecutar el servidor](#ejecutar-el-servidor)
  - [Ejecutar herramientas de análisis estático](#ejecutar-herramientas-de-análisis-estático)
- [Docker](#docker)
  - [Construir (build) la imagen y los servicios web y db](#construir-build-la-imagen-y-los-servicios-web-y-db)
  - [Parar (stop) los servicios](#parar-stop-los-servicios)
  - [Parar iniciar (start) los servicios](#parar-iniciar-start-los-servicios)
  - [Ejecutar los tests](#ejecutar-los-tests-1)
- [Documentación](#documentación)
- [Construido con](#construido-con)

<!-- /TOC -->



## Instalación y uso

Estas instrucciones te ayudarán a tener una copia del proyecto en marcha en tu
máquina local para fines de desarrollo y pruebas. 

Necesitas una instalación de Python 3.11.4 funcionando, con Pip instalado.

Estas intrucciones han sido redactadas para instalar el proyecto en sistemas Linux, aunque pueden adaptarse los comandos de forma muy sencilla a entornos Mac.

Para entornos de desarrollo y pruebas Windows, consultar los comendos equivalentes en Internet.

<br/>

### Descarga o clona el proyecto

Puedes descargarte o clonar el proyecto desde su [repositorio en GitHub](https://github.com/Lucsat/Beer-Tap-Dispenser). 

Para clonar el proyecto, utiliza el siguiente comando:

```console
git clone https://github.com/Lucsat/Beer-Tap-Dispenser.git
```

Si, por el contrario, te has descargado el fichero zomprimido con el proyecto, descomprímelo en tu unidad de disco local.

Una vez clonado, o descargado y descomprimido, entra en el directorio raíz del proyecto:

```console
cd Beer-Tap-Dispenser
```

### Instalar Pyenv

Instala [pyenv](https://github.com/pyenv/pyenv) y el plugin [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv), para poder crear un entorno virtual para el proyecto.

Una vez instalados, es hora de crear el entorno virtual. En nuestro caso, vamos a utilizar Python 3.11.4:

```console
$ pyenv virtualenv 3.11.4 beer-tap-dispenser
```

Entra dentro del entorno virtual de Python que acabamos de crear:

```console
$ pyenv activate beer-tap-dispenser
```

Asegúrate que te encuentras en el directorio raíz del proyecto.

Actualiza los paquetes `pip/setuptools`:

```console
$ pip install --upgrade pip
$ pip install --upgrade setuptools
```

<br/>

### Instalar Poetry

Vamos a hacer uso del paquete Python [Poetry](https://github.com/python-poetry/poetry) como
nuestro `sistema de construcción` (PEP518).
Lo instalamos antes de realizar ningún tipo de desarrollo en el proyecto:

```console
$ pip install poetry
```
<br/>

### Instalar el proyecto

Una vez que hayas instalado los requisitos previos, puedes proceder a instalar todos los paquetes y dependencias en el entorno virtual Python que acabamos de crear. 

Para ello utilizaremos Poetry y el fichero `pyproject.toml` (PEP517), incluído en el proyecto.

Inicia la instalación de las dependencias utilizando el comando `poetry`:

```console
$ poetry install
```

### Ejecutar los tests

Para ejecurar los tests del projecto puedes utilizar `pytest` con la opción de cobertura (`coverage`):

```console
pytest --cov --cov-report=xml ./
```

<br/>

### Ejecutar el servidor

Para ejecutar el proyecto debes estar en el directorio raíz del proyecto.

En primer lugar, debes tener la variable de entorno `DATABASE_URL` con la cadena de conexión con la base de datos:

```console
export DATABASE_URL=postgresql://user_test:pass_test@localhost:6432/tech_test
```

Una vez creada la variable, puedes lanzar el servidor ASGI [Uvicorn](https://www.uvicorn.org/):

```console
uvicorn app.main:app --port 8000 --reload
```

### Ejecutar herramientas de análisis estático

Se han utilizado las siguientes herramientas para el análisis estático de código:

* [Flake8](https://flake8.pycqa.org/en/latest/) - Análisis de estilo de codificación.
* [isort](https://pypi.org/project/isort/) - Organización de imports.
* [Black](https://pypi.org/project/black/) - Análisis de formato del código.
* [MyPy](https://www.mypy-lang.org/) - Static type checker.

Puedes comprobar el resultado de MyPy, Flake8, y Black, mediante los siguientes comandos:

```console
poetry run mypy app tests
```
```console
poetry run flake8 app tests
```
```console
poetry run black app tests
```

## Docker

Este proyecto se puede utilizar a través de [Docker](https://www.docker.com/) y [Docker Compose](https://docs.docker.com/compose/).

Las siguientes secciones describen las instrucciones `build/stop/start`.

### Construir (build) la imagen y los servicios web y db

Puedes construir la imagen Docker del proyecto y gestionarla con Docker Compose con el comando:

```
docker-compose up -d --build
```

### Parar (stop) los servicios

Para parar los servicios web y db, utiliza el comando:

```
docker-compose stop
```

### Parar iniciar (start) los servicios

Para iniciar los servicios, utiliza el argumento `start`:

```
docker-compose start
```

### Ejecutar los tests

Para ejecurar los tests del projecto en el servicio `web`, debes invocar el comando `poetry`, con los correspondientes parámetros de invocación de `pytest` con cobertura (`cov`):

```console
docker-compose exec web poetry run pytest --cov --cov-report=xml .
```

## Documentación

Puedes acceder a la documentación online accediendo tanto al servicio web de Docker, como a tu sistema local, dependiendo de cómo estés probando este proyecto.

Para probar la documentación local, puedes acceder a la [siguiente dirección](http://localhost:8000/docs), mientras que si quieres acceder a la documentación alojada en el servicio de Docker, puedes realizar en esta [otra dirección](http://localhost:8002/docs).


## Construido con

* [Python 3](https://docs.python.org/3/) - El lenguaje de programación.
* [FastAPI](https://fastapi.tiangolo.com/) - FastAPI es un moderno, rápido (alto rendimiento), 
  framework web para la construcción de API con Python 3.6+, basado en las 
  sugerencias de tipo estándar de Python.
* [Poetry](https://python-poetry.org/docs/) - Gestor de Dependencias.
* [SQLAlchemy](https://www.sqlalchemy.org/) - El ORM de acceso y gestión a la base de datos.
* [Pydantic](https://pydantic.dev/) - La librería de validación de datos.


