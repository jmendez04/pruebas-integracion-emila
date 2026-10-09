# Pruebas de Integración – EMILA

## Descripción

Proyecto académico para demostrar las **pruebas de integración** utilizando Flask, Postman y Google Calendar API.

Se desarrolló una API independiente que simula la gestión de entregas de la floristería EMILA, permitiendo crear, modificar y eliminar eventos en Google Calendar.

## Tecnologías utilizadas

- Python y Flask
- Google Calendar API
- OAuth 2.0
- Postman
- Pytest
- Git y GitHub

## Funcionalidades

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/health` | Verificar funcionamiento de Flask |
| POST | `/api/entregas` | Crear una entrega |
| PATCH | `/api/entregas/{id}` | Modificar el horario |
| DELETE | `/api/entregas/{id}` | Eliminar una entrega |

## Ejecución del proyecto

Instalar dependencias:
pip install -r requirements.txt


Configurar las credenciales OAuth 2.0 y autorizar el acceso a Google Calendar.
Iniciar Flask:
python app.py


La API estará disponible en:

`http://127.0.0.1:5000`

## Pruebas realizadas

Se realizaron **10 pruebas manuales en Postman**:

- **QA01–QA05:** creación de entregas y validaciones de datos.
- **QA06–QA08:** modificación de horarios y manejo de errores.
- **QA09–QA10:** eliminación de eventos y comprobación de eventos inexistentes.

Las 10 pruebas obtuvieron los resultados esperados.

También se configuraron pruebas automáticas en Postman para los métodos POST, PATCH y DELETE.

## Evidencias

Las capturas de las pruebas realizadas se incluyen en el repositorio como evidencia de los resultados obtenidos.

## Conclusión

Las pruebas permitieron comprobar la comunicación entre Flask y Google Calendar API mediante OAuth 2.0.

Se verificó la creación, modificación y eliminación de eventos reales, así como las validaciones y el manejo de errores.

**Nota:** Este proyecto es únicamente una demostración académica y no modifica el sistema original de EMILA.
