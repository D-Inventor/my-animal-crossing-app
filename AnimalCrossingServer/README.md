# AnimalCrossingServer — example starters
The animal crossing server stores information about Animal Crossing Villagers and connects them with information about Amiibo's.
It exposes an API that will eventually be used by the app to request and present the information.

## Running the project
The following software is needed to run the project:
 - Docker
 - Python 3.14+

| ℹ️ Recommendation: |
|---|
| Use a virtual environment with python so your dependencies are isolated |

### Installing the dependencies
Install all dependencies by running the following command:

```bash
pip install -e .[dev]
```

### Running the project
The project must run in docker. The docker-compose file sets up all dependencies and necessary environment.
Before composing the services, you need to create secret files. The secret files go into a secrets folder like this:

- 📄 /docker-compose.api.yaml
- 📁 /secrets
  - 📄 /db_root_password.txt
  - 📄 /db_user_password.txt

The secret files should contain randomly generated passwords. There is no specific requirements for the passwords.
Then run the project by calling the following command:

```bash
docker compose -f docker-compose.api.yaml up --build --watch
```

The service is now available on **http://localhost:8000**

### Debugging
This project is built with Test Driven Development and debugging is done accordingly. Find a test that demonstrates the bug. Run the test in debug mode if you need to step through.