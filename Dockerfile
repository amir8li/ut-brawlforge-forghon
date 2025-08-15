FROM python:3.13-slim

EXPOSE 8765

ENV PYTHONUNBUFFERED=1

COPY requirements.txt requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python3", "run_server.py" ]