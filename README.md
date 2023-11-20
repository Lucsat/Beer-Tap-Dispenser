## Table of Contents

- [{{ cookiecutter.project_name }}](#{{ cookiecutter.project_name }})
  - [Table of Contents](#table-of-contents)
  - [Características](#características)
  - [Docker](#docker)
    - [Construir (build) la imagen](#construir-build-la-imagen)
    - [Lanzar (run) la imagen](#lanzar-run-la-imagen)
    - [Parar (stop) el contenedor Docker](#parar-stop-el-contenedor-docker)
  - [Instalación y uso sin Docker](#instalación-y-uso)
    - [Instalar Python](#instalar-python)
    - [Instalar Pip](#instalar-pip)
    - [Instalar Pyenv](#instalar-pyenv)
    - [Instalar Poetry](#instalar-poetry)
    - [Instalar el proyecto](#instalar-el-proyecto)
    - [Ejecutar los tests](#ejecutar-los-tests)
    - [Ejecutar el servidor](#ejecutar-el-servidor)
  - [Documentación](#documentación)
  - [Construido con](#construido-con)



## Instalación y uso

Estas instrucciones te ayudarán a tenr una copia del proyecto en marcha en tu
máquina local para fines de desarrollo y pruebas. 

Necesitas una instalación de Python 3.11.4 funcionando, con Pip instalado.

<br/>

### Instalar Pyenv

Instala [pyenv](https://github.com/pyenv/pyenv) y el plugin [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv), para poder crear un entorno virtual para el proyecto.

Una vez instalados, es hora de crear el entorno virtual. En nuestro caso, vamos a tuilizar Python 3.11.4:

```console
$ pyenv virtualenv 3.11.4 beer-tap-dispenser
```

Entra dentro del entorno virtual de Python que acabamos de crear:

```console
$ pyenv activate beer-tap-dispenser
```

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
$ cd Beer\ Tap\ Dispenser
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


