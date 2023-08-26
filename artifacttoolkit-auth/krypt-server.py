# Updated SSH server script to reflect the new user authentication and authorization logic
import json
import paramiko
import socket
import threading
from os.path import exists
from datetime import datetime
import time

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

def read_user_data():
    try:
        with open("user_data.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def write_user_data(data):
    with open("user_data.json", "w") as f:
        json.dump(data, f)

class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()
        self.username = None

    def check_auth_publickey(self, username, key):
        log_message("INFO", f"check_auth_publickey called for {username}")
        self.username = username
        user_data = read_user_data()
        key_base64 = key.get_base64()
        
        if username not in user_data:
            user_data[username] = {
                "pubkeys": [""],
                "first_seen": str(datetime.utcnow()),
                "last_seen": str(datetime.utcnow())
            }
            write_user_data(user_data)
            log_message("WARN", f"User {username} not found. Template created. Account pending.")
            return paramiko.AUTH_FAILED
        
        if key_base64 in user_data[username]['pubkeys']:
            log_message("OK", f"{username} key validation passed")
            return paramiko.AUTH_SUCCESSFUL
        
        log_message("FAIL", f"{username} key validation failed")
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return 'publickey'
        
    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_exec_request(self, channel, command):
        cmd_str = command.decode('utf-8')
        user_data = read_user_data()

        if self.username not in user_data:
            channel.send("Your account is pending. Please wait for admin approval.\n")
            self.event.set()
            return True

        if cmd_str == 'login':
            channel.send("Login command detected\n")
        elif cmd_str == 'list-keys':
            channel.send(", ".join(user_data[self.username]['pubkeys']) + "\n")
        elif cmd_str == 'purge-keys':
            user_data[self.username]['pubkeys'] = []
            write_user_data(user_data)
            channel.send("All keys purged\n")
        else:
            channel.send(f"{cmd_str} command not found.\n")
        
        self.event.set()
        return True

def handle_client(client_socket):
    client_address = client_socket.getpeername()
    log_message("INFO", f"Connection accepted from {client_address}")

    try:
        transport = paramiko.Transport(client_socket)
        transport.load_server_moduli()
        transport.add_server_key(paramiko.RSAKey(filename="temp_server_key"))
        server = Server()
        transport.start_server(server=server)
        
        channel = transport.accept()
        if channel is not None:
            if transport.is_authenticated():
                channel.send("Validated key\n")
                server.event.wait(10)
            else:
                channel.send("INVALID KEY or ACCOUNT PENDING\n")
            time.sleep(1)
            channel.close()
    except Exception as e:
        log_message("FAIL", f"Exception handling client: {str(e)}")
    finally:
        transport.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', 2222))
    server_socket.listen(5)
    log_message("INFO", "Server listening on port 2222...")

    while True:
        client_socket, _ = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket,)).start()

if __name__ == '__main__':
    start_server()

