# Artifact Toolkit

This repository contains the Dockerized services for the Artifact Toolkit project.

## Services

- `artifacttoolkit-auth`: Authentication service.

## Setup

1. Clone the repository.
2. Copy `.env-sample` to `.env` and update the environment variables as needed.
3. Run `docker-compose up --build` to start the services.

## Development

Currently focusing on the `artifacttoolkit-auth` service. Other services are planned for future development.

## Directory Structure

./
├── README.md
├── .env-sample
├── docker-compose.yml
└── artifacttoolkit-auth/
    └── Dockerfile
