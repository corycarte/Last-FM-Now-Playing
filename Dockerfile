FROM python

RUN echo "Installing python requirements"
COPY ./requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD ["python", "app.py"]