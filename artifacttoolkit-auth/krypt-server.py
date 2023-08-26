#!/usr/bin/env python3

import paramiko
import socket
import threading
import json
from os.path import exists
from paramiko import RSAKey
from base64 import decodebytes
import time
from datetime import datetime

def log_message(status, message):
    status_colors = {
        "OK": "\033[92m",
        "FAIL": "\033[91m",
        "INFO": "\033[94m",
        "WARN": "\033[93m",
        "end": "\033[0m"
    }
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{status_colors[status]}{status}\033[0m] {message}")

# Function to read user data from JSON file
def read_user_data():
    try:
        with open("user_data.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Function to write user data to JSON file
def write_user_data(data):
    with open("user_data.json", "w") as f:
        json.dump(data, f)

def generate_temp_key():
    temp_key_path = "temp_server_key"
    if not exists(temp_key_path):
        log_message("WARN", "Server key not found. Generating a new key...")
        temp_key = paramiko.RSAKey.generate(bits=2048)
        temp_key.write_private_key_file(temp_key_path)
    return temp_key_path

class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()
        self.username = None

    def check_auth_publickey(self, username, key):
        self.username = username
        log_message("INFO", f"{username} connected from {client_address[0]}") # Log connection

        user_data = read_user_data()

        if username not in user_data:
            user_data[username] = {
                "pubkeys": [],
                "first_seen": str(datetime.utcnow()),
                "last_seen": str(datetime.utcnow())
            }

        user_data[username]["last_seen"] = str(datetime.utcnow())

        # Key validation logic here...
        key_str = key.get_base64()
        if key_str in user_data[username]["pubkeys"]:
            log_message("OK", f"{username} key validation passed") # Log key validation
            write_user_data(user_data)
            return paramiko.AUTH_SUCCESSFUL

        authorized_keys_path = f'/home/{username}/.ssh/authorized_keys'
        try:
            with open(authorized_keys_path, 'r') as file:
                for line in file:
                    key_parts = line.strip().split()
                    if len(key_parts) < 2:
                        continue
                    key_type, key_base64 = key_parts[:2]
                    key_data = decodebytes(key_base64.encode('utf-8'))
                    authorized_key = RSAKey(data=key_data)
                    if authorized_key == key:
                        user_data[username]["pubkeys"].append(key_str)
                        log_message("OK", f"{username} key validation passed") # Log key validation
                        write_user_data(user_data)
                        return paramiko.AUTH_SUCCESSFUL
        except Exception as e:
            log_message("FAIL", f"Error reading authorized keys for {username}: {str(e)}")

        log_message("FAIL", f"{username} key validation failed") # Log key validation
        write_user_data(user_data)
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return 'publickey'

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

def handle_client(client_socket, server_key_path):
    global client_address # Make client_address accessible to the Server class
    client_address = client_socket.getpeername()
    log_message("INFO", f"Connection accepted from {client_address}")

    try:
        transport = paramiko.Transport(client_socket)
        transport.load_server_moduli()
        transport.add_server_key(paramiko.RSAKey(filename=server_key_path))
        server = Server()
        transport.start_server(server=server)

        channel = transport.accept()
        if channel is not None:
            if transport.is_authenticated():
                channel.send("\nValidated key\n")
            else:
                channel.send("\nINVALID KEY\n")
            time.sleep(1) # Adding a delay to allow the client to receive the message
            channel.close()
    except Exception as e:
        log_message("FAIL", f"Exception handling client: {str(e)}")
    finally:
        transport.close()

def start_server():
    server_key_path = generate_temp_key()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', 2222))
    server_socket.listen(5)
    log_message("INFO", "Server listening on port 2222...")

    while True:
        client_socket, _ = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket, server_key_path)).start()

if __name__ == '__main__':
    start_server()

