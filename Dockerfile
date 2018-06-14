FROM python:3.6-alpine
COPY requirements.txt /
RUN pip install -r requirements.txt
COPY . /app
WORKDIR /app
RUN python3 setup.py install
WORKDIR example
EXPOSE 2121/udp
EXPOSE 2121/tcp
EXPOSE 60000-60009
CMD ["zosftp","&"]
