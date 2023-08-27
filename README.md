# Artifact Toolkit

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Reference Output](#reference-output)
- [Development](#development)

## Overview
Artifact Toolkit is a collection of Dockerized services focusing on secure authentication and other utilities. The primary service is Krypt-Server, a PKI/JSON based authentication service running in the artifacttoolkit-auth container.

## Features
- PKI-based authentication using public keys
- JSON data storage for user information
- Dockerized services for easy deployment
- Extensible architecture for future services

## Prerequisites
### Server
- [Docker](https://www.docker.com/)
- [Docker-Compose](https://docs.docker.com/compose/)
Or
- [Podman](https://podman.io/)
- [Podman-Compose](https://github.com/containers/podman-compose)

### Client
- [SSH](https://www.ssh.com/academy/ssh) (pending custom binary)

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

### Login
To log in, use the following command:
```bash
ssh -p 2222 username@server_address login
```
This will authenticate you and grant access to other services.

### List Users [authenticated]
To list all registered and pending users, use:
```bash
ssh -p 2222 username@server_address list-users
```

### List Keys [authenticated]
To list all your public keys stored on the server, use:
```bash
ssh -p 2222 username@server_address list-keys
```

### Purge Keys [authenticated]
To remove all your stored keys, use:
```bash
ssh -p 2222 username@server_address purge-keys
```
**Note**: This will remove all your keys, and you'll need to re-upload them for future authentication.

## Reference Output
### User Registration
![show registration](imgs/atk-registration.png)
### User Login
![show login](imgs/atk-valid-login.png)
### Duplicate Login
![show duplicate login](imgs/atk-duplicate-login.png)
### Invalid Login
![show invalid login](imgs/atk-invalid-login.png)
### Missing Key
![show missing key](imgs/atk-missing-key.png)
### Malformed Command
![show malformed command](imgs/atk-malformed-cmd.png)


## Development
The auth container is done for now. Next step is a storage solution. NFS/SMB aren't worth the time given the security/ease of use desired, SFTP is clunky ... I'll think of something ...


