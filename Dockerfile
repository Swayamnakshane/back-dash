FROM python:3.11.4

Workdir /app

Copy requirements.txt .

RUN pip install --upgrade pip
Run pip install -r requirements.txt
COPY . .
Expose 5000

CMD ["python","run.py"]
