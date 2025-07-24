FROM python:3.12

WORKDIR /app

COPY requirements.txt pyproject.toml README.rst LICENSE .

RUN pip install -r requirements.txt

COPY src ./src

RUN pip install .

EXPOSE 80

CMD ["flask", "--app", "gha_prometheus.app", "run", "--host", "0.0.0.0", "--port", "80"]
