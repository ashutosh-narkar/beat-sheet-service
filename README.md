# BeatSheetService

## 1. Description
The **BeatSheetService** is a Flask-based application designed to allow creators to structure their content into a
"beat sheet," a storytelling tool used to outline various elements like scenes, dialogues, or musical cues.

The service integrates with a MySQL database to store structured data and uses OpenAI's SDK to suggest the next beat
or act based on the previous ones.

## 2. Steps to Run the App

### Prerequisites:
1. **Docker** and **Docker Compose** installed on your system.
2. An active OpenAI API key.

### Steps:

- Clone the repository:

```bash
git clone https://github.com/ashutosh-narkar/beat-sheet-service.git
```

- Build and start the services

Before running the below command, in the `.env` file replace `your-openai-api-key` with an active OpenAI API key.

```bash
docker-compose up --build
```

- Check running containers

You should see the `app` and `mysql-db` containers up and running.

```bash
docker ps
```

- Test the Service

Ensure the containers are running. Run the test suite using the provided test file `test_app.py`. This test exercises all
the APIs mentioned in the problem statement along with the AI integration API.

> **_NOTE:_**  The test needs the `requests` library.

```bash
python test_app.py
```

- Cleanup

Stop the containers.

```bash
docker-compose down -v
```