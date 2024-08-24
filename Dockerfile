from python:3.12

WORKDIR /bot

COPY ./requirements.txt /bot/requirements.txt

RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r /bot/requirements.txt
RUN pip install fastapi[standard]
COPY ./src .

CMD ["uvicorn", "fastapi_serv:app", "--host", "0.0.0.0", "--port", "8000"]
