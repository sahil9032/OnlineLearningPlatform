# Online Learning Platform

Online Learning Platform is a project created in Django.

## Run

Install ffmpeg from [here](https://ffmpeg.org/download.html) and make sure this command runs successfully:

```bash
ffmpeg -version
```

Clone the project

```bash
git clone https://github.com/sahil9032/OnlineLearningPlatform
cd OnlineLearningPlatform
```

Install required packages

```bash
pip install -r requirements.txt
```

Enable Google Drive API from [here](https://developers.google.com/drive/api/v3/enable-drive-api) and download
client-secrets.json file. Change Team Drive Id and Folder Id accordingly in /teacher/views.py file.

Run following command.

```bash
python3 manage.py runserver
```

Browse website at [here](http://localhost:8000)

## Live at

Link: [Here](http://sahilbhuva.codes/accounts/login/)

## Want to dockerize project?

Create image

```bash
sudo docker build -t onlinelearningplatform .
```

Verify Image is created

```bash
sudo docker images
```

Check image is working properly

```bash
sudo docker run -p 80:80 onlinelearningplatform
```

Create container from the image

```bash
sudo docker container create --name onlinelearningplatform -p 80:80 onlinelearningplatform
```

Start container

```bash
sudo docker container start onlinelearningplatform
```

(Optional) Set restart policy to on-faliure

```bash
sudo docker update --restart=on-failure onlinelearningplatform
```

Visit site at http://your-ip:80 or http://localhost:80