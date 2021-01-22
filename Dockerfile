FROM python:3.6

WORKDIR /code

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY src/ .

COPY entrypoint.sh .

RUN chmod +x entrypoint.sh

ENTRYPOINT ["/code/entrypoint.sh"]