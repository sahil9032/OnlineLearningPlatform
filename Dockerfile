FROM python:3.7

RUN  apt-get update \
    && apt install -y ffmpeg

ENV PATH="/usr/bin/ffmpeg:/usr/share/ffmpeg:${PATH}"


WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .

EXPOSE 80
CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]
