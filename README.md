# Portal de Procesos - Mexicargo

Aplicación web para automatizar procesos internos sin depender de Excel ni macros VBA.

## Procesos incluidos
- Cruce de Agendamiento
- (Próximamente) Inventario de Cajas

## Tecnologías
- Python 3.11
- FastAPI
- Pandas
- OpenPyXL
- HTML / CSS / JS

## Ejecución local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
