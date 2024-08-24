# Nisfak: Take Home Project

## Getting Started

### Prerequisites

Ensure you have Docker and Docker Compose installed on your machine.

### Setup

1. **Setup the `.env` file**:
    - Copy the `.env.sample` to `.env`:
      ```bash
      cp .env.sample .env
      ```
    - Edit the `.env` file to include all the required environment variables.

2. **Run the project with Docker Compose**:
    ```bash
    docker-compose up -d
    ```

3. **Run the initial migrations and setup roles and permissions**:
    - After the containers are up, go inside the app container:
      ```bash
      docker-compose exec app bash
      ```
    - Run the following commands:
      ```bash
      python manage.py migrate
      python manage.py create_roles_and_permissions
      ```

## Running Security Tests

To run security tests on the codebase, use the `bandit` tool:

```bash
bandit -r survey_builder/
```

### Accessing the Load Test

To access the load testing tool, visit:

```bash
http://localhost:8089/
```

