FROM python:3.12.2

WORKDIR /src

COPY ./requirements.txt /src
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . /src

CMD ["python", "src/main.py"]