# Artifact Toolkit

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Development](#development)

## Overview
Artifact Toolkit is a collection of Dockerized services focusing on secure authentication and other utilities. The primary service is `artifacttoolkit-auth`, a Krypt-Server pubkey/JSON based authentication service.

## Features
- SSH-based authentication using public keys
- JSON data storage for user information
- Dockerized services for easy deployment
- Extensible architecture for future services

## Prerequisites
### Server
- Docker
- Python 3.x
- [Paramiko](https://www.paramikoproject.com/)
### Client
- SSH(pending custom binary)

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/0xdreadnaught/ArtifactToolkit.git
    ```
2. Copy `.env-sample` to `.env` and update the environment variables as needed.
    ```bash
    cp .env-sample .env
    ```
3. Build and run the Docker services:
    ```bash
    docker-compose up -d
    ```
4. Add users to `user_data.json` (optional).

## Usage
<TDB>

## Development
The auth container is done for now. Next step is a storage solution. NFS/SMB aren't worth the time given the security/ease of use desired, SFTP is clunky ... I'll think of something ...


