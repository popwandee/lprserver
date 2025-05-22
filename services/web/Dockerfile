# pull official base image
FROM python:3.11.3-slim-buster

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


#install system dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN apt-get update && apt-get install -y netcat-openbsd

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy project files
COPY . /usr/src/app/

# run the entrypoint script
ENTRYPOINT [ "/usr/src/app/entrypoint.sh" ]
# command to run the application
#CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "wsgi:app"]