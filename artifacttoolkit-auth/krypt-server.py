import json
import socket
import threading
import time
from base64 import decodebytes
from datetime import datetime
from os.path import exists
import paramiko
from paramiko import RSAKey

# Logging function
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

# Load or create JSON data
try:
    with open("user_data.json", "r") as f:
        log_message("OK", f"Loaded user_data.json")
        user_data = json.load(f)
except FileNotFoundError:
    log_message("INFO", f"Created user_data.json")
    user_data = {}
    with open("user_data.json", "w") as f:
        json.dump(user_data, f)

def update_json_file(user_data):
    try:
        with open("user_data.json", "w") as f:
            json.dump(user_data, f)
    except Exception as e:
        log_message("FAIL", f"Failed to save JSON!")

def update_last_seen(username, user_data):
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")

    try:
        if username in user_data:
            user_data[username]['last_seen'] = current_time
            update_json_file(user_data)
    except Exception as e:
        log_message("FAIL", f"Failed to find user for LastSeen update!")

# JSON key auth
def verify_user_key(username, key, user_data):
    if username in user_data and 'public_keys' in user_data[username]:
        for stored_key_base64 in user_data[username]['public_keys']:
            try:
                stored_key_data = decodebytes(stored_key_base64.encode('utf-8'))
                stored_key = RSAKey(data=stored_key_data)
                if stored_key == key:
                    log_message("OK", f"{username} JSON key verification passed")
                    return True
            except Exception as e:
                log_message("FAIL", f"Error decoding stored JSON key for {username}: {str(e)}")
    log_message("FAIL", f"{username} JSON key verification failed")
    return False

def get_user_validated_status(username, user_data):
    try:
        return user_data[username]['validated']
    except KeyError:
        log_message("FAIL", f"Failed to parse validation status from JSON!")
        return None

# Invalidate all users by setting 'validated' to False
for username in user_data:
    log_message("INFO", f"Invalidating stale session for {username}")
    user_data[username]['validated'] = False
update_json_file(user_data)

# Server Class
class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()
        self.username = None
        self.logged = False

    # SSH key auth
    def check_auth_publickey(self, username, key):
        if not self.logged:
            self.username = username
            self.key = key
            log_message("INFO", f"{username} connected from {client_address[0]}")
            log_message("OK", f"{username} key validation passed")
            self.logged = True
        return paramiko.AUTH_SUCCESSFUL

    def get_allowed_auths(username):
        allowed_auths = 'publickey'
        return allowed_auths

    def check_channel_request(kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_exec_request(self, channel, command):
        cmd_str = command.decode('utf-8')
        if cmd_str == 'login':
            # Do they have an account?
            if self.username in user_data:
                update_last_seen('some_username', user_data)
                # Are they already validated?
                if get_user_validated_status(self.username, user_data):
                    log_message("INFO", f"{self.username} sent a redundant login request.")
                    response = "You are already logged in.\n"
                else:
                    # Do they have a public key?
                    if verify_user_key(self.username, self.key, user_data):
                        # Do key verification and update the last seen status
                        log_message("OK", f"Valid login by {self.username}")
                        user_data[self.username]['validated'] = True
                        update_json_file(user_data)
                        response = "You have been logged in\n"
                    else:
                        log_message("FAIL", f"{self.username} has no valid keys.")
                        response = "No valid keys found. Contact admin.\n"
            else:
                # Create a template for the user
                current_time = time.strftime("%Y-%m-%d %H:%M:%S")
                user_data[self.username] = {
                    'public_keys': [""],
                    'first_seen': current_time,
                    'last_seen': current_time,
                    'validated': False
                }
                update_json_file(user_data)
                log_message("OK", f"Account created for {self.username}, verification pending.")
                response = "Account created, verification pending. Please send public key to admin.\n"
        elif cmd_str == 'list-users':
            if get_user_validated_status(self.username, user_data):
                response = "Users:\n"
                response = "Users:\n" + "\n".join(user_data.keys())
                #send another response with all usernames in JSON
                log_message("OK", f"Command executed by {self.username}: {cmd_str}")
            else:
                response = "No."
                log_message("WARN", f"{self.username} tried to run {cmd_str} without authenticating.")
        elif cmd_str == 'list-keys':
            if get_user_validated_status(self.username, user_data):
                response = "Keys:\n\n".join(user_data[self.username]['public_keys'])
                #send another response with all of the user's keys from the JSON
                log_message("OK", f"Command executed by {self.username}: {cmd_str}")
            else:
                response = "No."
                log_message("WARN", f"{self.username} tried to run {cmd_str} without authenticating.")
        elif cmd_str == 'purge-keys':
            if get_user_validated_status(self.username, user_data):
                response = "Keys purged.\n"
                #wipe the user's keys from JSON
                user_data[self.username]['public_keys'] = [""]
                update_json_file(user_data)
                log_message("OK", f"Command executed by {self.username}: {cmd_str}")
            else:
                response = "No."
                log_message("WARN", f"{self.username} tried to run {cmd_str} without authenticating.")
        elif cmd_str == 'help':
            if get_user_validated_status(self.username, user_data):
                response = "Supported commands:\n\nlogin: authenticate to gain access to services.\nlist-users: show registered and pending users.\nlist-keys:list your keys.\npurge-keys:wipe your keys.\nhelp: this message."
                #send another response with all of the user's keys from the JSON
                log_message("OK", f"Command executed by {self.username}: {cmd_str}")
            else:
                response = "No."
                log_message("WARN", f"{self.username} tried to run {cmd_str} without authenticating.")
        else:
            if get_user_validated_status(self.username, user_data):
                response = f"{cmd_str} command not found.\n"
                #send another response with all of the user's keys from the JSON
                log_message("FAIL", f"Invalid command from {self.username}: {cmd_str}")
            else:
                response = "No."
                log_message("WARN", f"{self.username} tried to run {cmd_str} without authenticating.")

        channel.send(response)
        self.event.set()
        return True

def handle_client(client_socket):
    global client_address
    client_address = client_socket.getpeername()
    log_message("INFO", f"Connection accepted from {client_address}")

    try:
        transport = paramiko.Transport(client_socket)
        transport.load_server_moduli()
        transport.add_server_key(paramiko.RSAKey(filename='temp_server_key'))
        server = Server()
        transport.start_server(server=server)

        channel = transport.accept()
        if channel is None:
            log_message("WARN", f"Potential password auth from {client_address[0]}")
        else:
            server.event.wait(10)
            channel.close()
    except Exception as e:
        log_message("FAIL", f"Exception handling client: {str(e)}")
    finally:
        transport.close()

if __name__ == '__main__':
    # Check if the server key exists; if not, create one
    server_key_path = 'temp_server_key'
    if not exists(server_key_path):
        log_message("INFO", "Server key not found, generating new key...")
        new_key = RSAKey.generate(bits=2048)
        new_key.write_private_key_file(server_key_path)
        log_message("OK", "New server key generated.")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', 2222))
    server_socket.listen(5)

    log_message("INFO", "Server listening on port 2222...")

    while True:
        client_socket, _ = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket,)).start()
