FROM python:3.10.4-bullseye
RUN pip install -r requirements.txt

COPY StarbucksAutoma/ .
COPY main.py .

CMD ["python", "main.py"]
