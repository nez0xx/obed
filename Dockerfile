FROM python:3.12.3

WORKDIR /home/comm-bot

COPY requirements.txt .

RUN pip3.12 install -r requirements.txt

COPY . ./

ENV PYTHONPATH=/home/comm-bot

CMD python -m app.main