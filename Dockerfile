FROM python:3.9

COPY . .

WORKDIR src

RUN pip3 install -r requirements.txt

CMD python main.py