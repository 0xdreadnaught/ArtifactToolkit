"""
Krypt Server
Authentication gateway for ArtifactToolkit
"""

import json
import socket
import threading
import time
from base64 import decodebytes
from datetime import datetime
from os.path import exists
import paramiko
from paramiko import RSAKey

CLIENT_ADDRESS = None


def log_message(status, message):
    """Logging function."""
    status_colors = {
        "OK": "\033[92m",
        "FAIL": "\033[91m",
        "INFO": "\033[94m",
        "WARN": "\033[93m",
        "end": "\033[0m",
    }
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{status_colors[status]}{status}\033[0m] {message}")


def update_json_file(user_data):
    """Update JSON file."""
    try:
        with open("user_data.json", "w") as f:
            json.dump(user_data, f, indent=4)
    except Exception as exception:
        log_message("FAIL", "Failed to save JSON!")


# Load or create JSON data
try:
    with open("user_data.json", "r") as f:
        log_message("OK", "Loaded user_data.json")
        user_data = json.load(f)
        # Write JSON back to file to ensure formatting is in place
        update_json_file(user_data)
except FileNotFoundError:
    log_message("OK", "Created user_data.json")
    user_data = {}
    update_json_file(user_data)

# Invalidate all users by setting 'validated' to False
for username in user_data:
    log_message("INFO", f"Invalidating stale session for {username}")
    user_data[username]["validated"] = False
update_json_file(user_data)


def update_last_seen(username, user_data):
    """Update last seen time for a user."""
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        if username in user_data:
            user_data[username]["last_seen"] = current_time
            update_json_file(user_data)
    except Exception as exception:
        log_message("FAIL", "Failed to find user for LastSeen update!")


def verify_user_key(username, key, user_data):
    """Verify user key from JSON."""
    if username in user_data and "public_keys" in user_data[username]:
        for stored_key_base64 in user_data[username]["public_keys"]:
            try:
                stored_key_data = decodebytes(stored_key_base64.encode("utf-8"))
                stored_key = RSAKey(data=stored_key_data)
                if stored_key == key:
                    log_message("OK", f"{username} JSON key verification passed")
                    return True
            except Exception as exception:
                log_message(
                    "FAIL",
                    f"Error decoding stored JSON key for {username}: {str(exception)}",
                )
    log_message("FAIL", f"{username} JSON key verification failed")
    return False


def get_user_validated_status(username, user_data):
    """Get user validation status from JSON."""
    try:
        return user_data[username]["validated"]
    except KeyError:
        log_message("FAIL", "Failed to parse validation status from JSON!")
        return None


def setup_transport(client_socket):
    transport = paramiko.Transport(client_socket)
    transport.load_server_moduli()
    transport.add_server_key(paramiko.RSAKey(filename="temp_server_key"))
    return transport


def handle_channel(transport, server):
    channel = transport.accept()
    if channel is None:
        log_message("WARN", f"Potential password auth from {CLIENT_ADDRESS[0]}")
    else:
        server.event.wait(10)
        channel.close()


def handle_client(client_socket):
    global CLIENT_ADDRESS
    CLIENT_ADDRESS = client_socket.getpeername()
    log_message("INFO", f"Connection accepted from {CLIENT_ADDRESS}")

    try:
        transport = setup_transport(client_socket)
        server = Server()
        transport.start_server(server=server)
        handle_channel(transport, server)
    except Exception as exception:
        log_message("FAIL", f"Exception handling client: {str(exception)}")
    finally:
        transport.close()


class Server(paramiko.ServerInterface):
    """Server Class."""

    def __init__(self):
        self.event = threading.Event()
        self.username = None
        self.logged = False

    def check_auth_publickey(self, username, key):
        """SSH key auth."""
        if not self.logged:
            self.username = username
            self.key = key
            log_message("INFO", f"{username} connected from {CLIENT_ADDRESS[0]}")
            log_message("OK", f"{username} key validation passed")
            self.logged = True
        return paramiko.AUTH_SUCCESSFUL

    def get_allowed_auths(self, username):
        """Get allowed auths."""
        return "publickey"

    def check_channel_request(self, kind, chanid):
        """Check channel request."""
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_exec_request(self, channel, command):
        """Check channel exec request."""
        cmd_str = command.decode("utf-8")
        command_handlers = {
            "login": self.handle_login,
            "list-users": self.handle_list_users,
            "list-keys": self.handle_list_keys,
            "prune-keys": self.handle_prune_keys,
            "purge-keys": self.handle_purge_keys,
            "help": self.handle_help,
        }

        if cmd_str in command_handlers:
            command_handlers[cmd_str](channel)
        else:
            channel.send(f"{cmd_str} command not found.\n")
            log_message("FAIL", f"Invalid command from {self.username}: {cmd_str}")

        self.event.set()
        return True

    def handle_login(self, channel):
        """Handle login command."""
        if self.username in user_data:
            update_last_seen(self.username, user_data)
            if get_user_validated_status(self.username, user_data):
                log_message("INFO", f"{self.username} sent a redundant login request.")
                response = "You are already logged in.\n"
            else:
                if verify_user_key(self.username, self.key, user_data):
                    log_message("OK", f"Valid login by {self.username}")
                    user_data[self.username]["validated"] = True
                    update_json_file(user_data)
                    response = "You have been logged in.\n"
                else:
                    log_message("FAIL", f"{self.username} has no valid keys.")
                    response = "No valid keys found. Contact admin.\n"
        else:
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            user_data[self.username] = {
                "public_keys": [""],
                "first_seen": current_time,
                "last_seen": current_time,
                "validated": False,
            }
            update_json_file(user_data)
            log_message(
                "OK", f"Account created for {self.username}, verification pending."
            )
            response = "Account created, verification pending. Please send public key to admin.\n"

        channel.send(response)

    def handle_list_users(self, channel):
        """Handle list-users command."""
        if get_user_validated_status(self.username, user_data):
            response = "Users:\n"
            for user in user_data.keys():
                response += f"\t{user}\n"
            response += "\n"
            log_message("OK", f"Command executed by {self.username}: list-users")
        else:
            response = "No."
            log_message(
                "WARN",
                f"{self.username} tried to run list-users without authenticating.",
            )

        channel.send(response)

    def handle_list_keys(self, channel):
        """Handle list-keys command."""
        if get_user_validated_status(self.username, user_data):
            response = "Keys:\n"
            current_key_base64 = self.key.get_base64()
            for index, key in enumerate(user_data[self.username]["public_keys"]):
                if key == current_key_base64:
                    response += f"\t{index} (active) {key}\n"
                else:
                    response += f"\t{index} {key}\n"
            response += "\n"
            log_message("OK", f"Command executed by {self.username}: list-keys")
        else:
            response = "No."
            log_message(
                "WARN",
                f"{self.username} tried to run list-keys without authenticating.",
            )

        channel.send(response)

    def handle_prune_keys(self, channel):
        """Handle prune-keys command."""
        if get_user_validated_status(self.username, user_data):
            # Keep only the key used for the current session
            current_key_base64 = self.key.get_base64()
            user_data[self.username]["public_keys"] = [current_key_base64]
            update_json_file(user_data)
            response = "Keys pruned, only the current key is retained.\n"
            log_message("OK", f"Command executed by {self.username}: prune-keys")
        else:
            response = "No."
            log_message(
                "WARN",
                f"{self.username} tried to run prune-keys without authenticating.",
            )

        channel.send(response)

    def handle_purge_keys(self, channel):
        """Handle purge-keys command."""
        if get_user_validated_status(self.username, user_data):
            user_data[self.username]["public_keys"] = [""]
            update_json_file(user_data)
            response = "Keys purged.\n"
            log_message("OK", f"Command executed by {self.username}: purge-keys")
        else:
            response = "No."
            log_message(
                "WARN",
                f"{self.username} tried to run purge-keys without authenticating.",
            )

        channel.send(response)

    def handle_help(self, channel):
        """Handle help command."""
        if get_user_validated_status(self.username, user_data):
            response = (
                "\nSupported commands:\n\n"
                "\tlogin: \t\tAuthenticate to gain access to services.\n"
                "\tlist-users: \tShow registered and pending users.\n"
                "\tlist-keys: \tList your public keys.\n"
                "\tpurge-keys: \tWipe all your public keys.\n"
                "\tprune-keys: \tRemove all public keys except the one used for the current session.\n"
                "\thelp: \t\tDisplay this help message.\n\n"
            )
            log_message("OK", f"Command executed by {self.username}: help")
        else:
            response = "No."
            log_message(
                "WARN", f"{self.username} tried to run help without authenticating."
            )

        channel.send(response)


if __name__ == "__main__":
    # Check if the server key exists; if not, create one
    SERVER_KEY_PATH = "temp_server_key"
    if not exists(SERVER_KEY_PATH):
        log_message("INFO", "Server key not found, generating new key...")
        new_key = RSAKey.generate(bits=2048)
        new_key.write_private_key_file(SERVER_KEY_PATH)
        log_message("OK", "New server key generated.")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", 2222))
    server_socket.listen(5)

    log_message("INFO", "Server listening on port 2222...")

    while True:
        client_socket, _ = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket,)).start()
