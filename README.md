# Artifact Toolkit

This repository contains the Dockerized services for the Artifact Toolkit project.

## Services

- `artifacttoolkit-auth`: Krypt-Server pubkey/JSON based authentication service.

## Setup

1. Clone the repository.
2. Copy `.env-sample` to `.env` and update the environment variables as needed.
3. Run `docker-compose up --build` to start the services.
4. Add users to user_data.json (required).

## Development

Currently focusing on the `artifacttoolkit-auth` service. Other services are planned for future development.

## Directory Structure

./

├── README.md

├── .env

├── .env-sample

├── docker-compose.yml

└── artifacttoolkit-auth/

    └── Dockerfile

    └── krypt-server.py

    └── temp_server_key

    └── user_data.json
