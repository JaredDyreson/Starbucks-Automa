FROM python:3.10.4-bullseye
COPY requirements.txt .
RUN pip install -r requirements.txt

ADD StarbucksAutoma/ ./StarbucksAutoma/
COPY setup.py .
COPY main.py .
COPY geckodriver /usr/bin

RUN pip install -e .

ADD _Config/ /tmp/StarbucksAutoma

CMD ["python", "main.py"]
