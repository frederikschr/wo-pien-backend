FROM python:3.8.3-slim-buster

# copy the requirements file into the image

COPY app/requirements.txt /app/requirements.txt

# switch working directory
WORKDIR /app

# install the dependencies and packages in the requirements file
RUN pip install -r requirements.txt

# copy every content from the local file to the image
COPY .. /app

CMD gunicorn --bind 0.0.0.0:5000 main:app

#ENTRYPOINT [ "python" ]

#CMD ["main.py" ]