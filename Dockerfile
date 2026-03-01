FROM python:3.12-alpine

WORKDIR /game/path

COPY requirements.txt  .

RUN pip install -r requirements.txt

COPY . .

RUN mkdir -p /data

CMD [ "python", "game.py" ]

EXPOSE 5000

