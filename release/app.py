import os
import ast
import time
import json
import random
import hashlib
from datetime import datetime
import builtins

from core.qrcode import generate_qr_ascii
from core.encryption import get_ssn, generate_keypair, generate_keystream, encrypt, decrypt_with_priv, decrypt_with_pub, sign, check_integrity

ASCII = """

 ▄▄▄       ███▄    █ ▄▄▄█████▓ ██▓▓█████▄  ▒█████  ▄▄▄█████▓▓█████ 
▒████▄     ██ ▀█   █ ▓  ██▒ ▓▒▓██▒▒██▀ ██▌▒██▒  ██▒▓  ██▒ ▓▒▓█   ▀ 
▒██  ▀█▄  ▓██  ▀█ ██▒▒ ▓██░ ▒░▒██▒░██   █▌▒██░  ██▒▒ ▓██░ ▒░▒███   
░██▄▄▄▄██ ▓██▒  ▐▌██▒░ ▓██▓ ░ ░██░░▓█▄   ▌▒██   ██░░ ▓██▓ ░ ▒▓█  ▄ 
 ▓█   ▓██▒▒██░   ▓██░  ▒██▒ ░ ░██░░▒████▓ ░ ████▓▒░  ▒██▒ ░ ░▒████▒
 ▒▒   ▓▒█░░ ▒░   ▒ ▒   ▒ ░░   ░▓   ▒▒▓  ▒ ░ ▒░▒░▒░   ▒ ░░   ░░ ▒░ ░
  ▒   ▒▒ ░░ ░░   ░ ▒░    ░     ▒ ░ ░ ▒  ▒   ░ ▒ ▒░     ░     ░ ░  ░
  ░   ▒      ░   ░ ░   ░       ▒ ░ ░ ░  ░ ░ ░ ░ ▒    ░         ░   
      ░  ░         ░           ░     ░        ░ ░              ░  ░
"""

# ---- file paths ----

keypairs_file = "data/keypairs.json"
messages_file = "data/messages.json"
contacts_file = "data/contacts.json"

configuration_file = "data/conf.config"
user_config_file = "data/user.config"

# ---- helpers ----

timestamp = datetime.now().strftime("[%Y-%m-%d - %H:%M:%S]")

def random_num():
    return random.randint(0, 90000000)

# ---- default configurations ----


DEFAULT_CONFIG = {
    "storing_messages": True,
    "number_of_saved_messages": 10,
    "storing_keypairs": True,
    "number_of_saved_keypairs": 10,
    "storing_contacts": True,
    "number_of_saved_contacts": 10
}

DEFAULT_USER_CONFIG = {
    "username": f"user{random_num()}",
    "bio": f""
}




# ---- parsers ----

class ConfigurationParser:
    def __init__(self, filepath):
        self.filepath = filepath
        self.config = {}
        self.load()

    def load(self):
        # Check if file exists
        if not os.path.exists(self.filepath):
            print(f"{timestamp} Configuration file not found, creating one with defaults...")
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            self.config = DEFAULT_CONFIG.copy()
            self.save()
            return

        # Read the file
        with open(self.filepath, 'r') as f:
            lines = f.readlines()

        # If file is empty, treat as corrupted
        if not lines:
            print(f"{timestamp} Configuration file found but empty, filling with defaults...")
            self.config = DEFAULT_CONFIG.copy()
            self.save()
            return

        # Try parsing each line
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                try:
                    self.config[key] = ast.literal_eval(value)
                except Exception:
                    print(f"{timestamp} Warning: Could not parse line: '{line}'. Using default if available.")
                    # fallback to default if exists
                    if key in DEFAULT_CONFIG:
                        self.config[key] = DEFAULT_CONFIG[key]

        # Make sure any missing defaults are added
        for key, value in DEFAULT_CONFIG.items():
            self.config.setdefault(key, value)


    def save(self):
        with open(self.filepath, 'w') as f:
            for key, value in self.config.items():
                f.write(f"{key} = {repr(value)}\n")

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save()

    def delete(self, key):
        if key in self.config:
            del self.config[key]
            self.save()

class UserConfigParser():
    def __init__(self, filepath):
        self.filepath = filepath
        self.config = {}
        self.load()

    def load(self):
        # Check if file exists
        if not os.path.exists(self.filepath):
            print(f"{timestamp} User configuration file not found, creating one with defaults...")
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            self.config = DEFAULT_USER_CONFIG.copy()
            self.save()
            return

        # Read the file
        with open(self.filepath, 'r') as f:
            lines = f.readlines()

        # If file is empty, treat as corrupted
        if not lines:
            print(f"{timestamp} User configuration file found but empty, filling with defaults...")
            self.config = DEFAULT_USER_CONFIG.copy()
            self.save()
            return

        # Try parsing each line
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                try:
                    self.config[key] = ast.literal_eval(value)
                except Exception:
                    print(f"{timestamp} Warning: Could not parse line: '{line}'. Using default if available.")
                    # fallback to default if exists
                    if key in DEFAULT_USER_CONFIG:
                        self.config[key] = DEFAULT_USER_CONFIG[key]

        # Make sure any missing defaults are added
        for key, value in DEFAULT_USER_CONFIG.items():
            self.config.setdefault(key, value)


    def save(self):
        with open(self.filepath, 'w') as f:
            for key, value in self.config.items():
                f.write(f"{key} = {repr(value)}\n")

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save()

    def delete(self, key):
        if key in self.config:
            del self.config[key]
            self.save()

class KeypairParser:
    def __init__(self, filepath, limit=10):
        self.filepath = filepath
        self.limit = limit
        self.keypairs = []
        self.load()

    def load(self):
        if not os.path.exists(self.filepath):
            print(f"{timestamp} No keypair file found, creating a new one...")
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            self.save()
            return
        try:
            with open(self.filepath, "r") as f:
                self.keypairs = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            print(f"{timestamp} Keypair file corrupted or empty, resetting...")
            self.keypairs = []
            self.save()

    def save(self):
        with open(self.filepath, "w") as f:
            json.dump(self.keypairs[-self.limit:], f, indent=4)

    def append_keypair(self, keypair_dict):
        """Append a new keypair and trim the list if necessary."""
        self.keypairs.append(keypair_dict)
        self.save()

    def delete_keypair(self, index):
        if 0 <= index < len(self.keypairs):
            del self.keypairs[index]
            self.save()

    def get_all(self):
        return self.keypairs

class MessageParser:
    def __init__(self, filepath, limit=10):
        self.filepath = filepath
        self.limit = limit
        self.messages = []
        self.load()

    def load(self):
        if not os.path.exists(self.filepath):
            print(f"{timestamp} No message file found, creating a new one...")
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            self.save()
            return
        try:
            with open(self.filepath, "r") as f:
                self.messages = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            print(f"{timestamp} Message file corrupted or empty, resetting...")
            self.messages = []
            self.save()

    def save(self):
        with open(self.filepath, "w") as f:
            json.dump(self.messages[-self.limit:], f, indent=4)

    def append_message(self, msg_dict):
        """Append a message (dict: {content, sender_pk, receiver_pk, timestamp})."""
        self.messages.append(msg_dict)
        self.save()

    def delete_message(self, index):
        if 0 <= index < len(self.messages):
            del self.messages[index]
            self.save()

    def get_all(self):
        return self.messages

class ContactParser:
    def __init__(self, filepath, limit=10):
        self.filepath = filepath
        self.limit = limit
        self.contacts = []
        self.load()

    def load(self):
        if not os.path.exists(self.filepath):
            print(f"{timestamp} No contact file found, creating a new one...")
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            self.save()
            return
        try:
            with open(self.filepath, "r") as f:
                self.contacts = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            print(f"{timestamp} Contact file corrupted or empty, resetting...")
            self.contacts = []
            self.save()

    def save(self):
        with open(self.filepath, "w") as f:
            json.dump(self.contacts[-self.limit:], f, indent=4)

    def append_contact(self, contact_dict):
        """Append contact (dict: {name, public_key})."""
        self.contacts.append(contact_dict)
        self.save()

    def delete_contact(self, index):
        if 0 <= index < len(self.contacts):
            del self.contacts[index]
            self.save()

    def get_all(self):
        return self.contacts
# ---- loaders ----

def load_client_config():
    print(f"{timestamp} Initialising configuration parser...")
    cfg = ConfigurationParser(configuration_file)

    print(f"{timestamp} Loading configuration...")
    print("\n")
    storing_messages = cfg.get("storing_messages")
    storing_keypairs = cfg.get("storing_keypairs")
    storing_contacts = cfg.get("storing_contacts")

    if storing_keypairs == True:
        print(f"{timestamp} Storing keypairs is turned on")
        print(f"{timestamp} Initialising Keypair parser")
        kpk = KeypairParser(keypairs_file)
        print(f"{timestamp} Keypair parser intitialised")
        number_of_stored_keypairs = cfg.get("number_of_saved_keypairs")
        print(f"{timestamp} Storing the last {number_of_stored_keypairs} used keypairs.")
        print("\n")
    else:
        print(f"{timestamp} Storing keypairs is turned off")
        print("\n")

    if storing_messages == True:
        print(f"{timestamp} Storing messages is turned on")
        print(f"{timestamp} Initialising Message parser")
        msg = MessageParser(messages_file)
        print(f"{timestamp} Message parser intitialised")
        number_of_stored_messages = cfg.get("number_of_saved_messages")
        print(f"{timestamp} Storing the last {number_of_stored_messages} sent messages.")
        print("\n")
    else:
        print(f"{timestamp} Storing messages is turned off")
        print("\n")

    if storing_contacts == True:
        print(f"{timestamp} Storing contacts is turned on")
        print(f"{timestamp} Initialising Contact parser")
        ctb = ContactParser(contacts_file)
        print(f"{timestamp} Contact parser intitialised")
        number_of_stored_contacts = cfg.get("number_of_saved_contacts")
        print(f"{timestamp} Storing the last {number_of_stored_contacts} contacts.")
        print("\n")
    else:
        print(f"{timestamp} Storing contacts is turned off")
        print("\n")



def load_user_config():
    print(f"{timestamp} Initialising user configuration parser...")
    ucfg = UserConfigParser(user_config_file)

    print(f"{timestamp} Loading user configuration...")
    print(f"{timestamp} Loading username...")
    print("\n")
    client_username = ucfg.get("username")

    
    print(f"{timestamp} Welcome to Antidote {client_username}")


# ---- cli ----


def cli():
    ucfg = UserConfigParser(user_config_file)
    client_username = ucfg.get("username")

    user_input = input(f"${client_username}: ")

    cli_commands = {
        "help": "returns all commands",
        "npair": "generates a new kepair",
        "econf": "edit client configuration",
        "euconf": "edit user configuration",
        "dcrypt": "decrypts a message",
        "tmsg": "makes a test message"
    }

    if user_input == "tmsg":
        test_message()
    elif user_input == "npair":
        print(f"{timestamp} Generating new keypair..")
        seed, public_key, private_key, valid_status = new_keypair()
        user_input = input("Show keypair? (y/n): ")
        if user_input == "y" or "Y" or "yes" or "YES":
            print("\nKeypair:")
            print(f"    seed: {seed}")
            print(f"    public key: {public_key}")
            print(f"    private key: {private_key}")
            print(f"    valid status: {valid_status}")
            print("\n")

        cli()
    elif user_input == "help":
        print(cli_commands)
        cli()

    else:
        print(f"\nunknown command: '{user_input}' | use 'help' to see all commands")
        cli()






# ---- helpers 2 ----

def new_keypair():
    seed, public_key, private_key, valid_status = generate_keypair()
    
    cfg = ConfigurationParser(configuration_file)
    storing_keypairs = cfg.get("storing_keypairs")

    if storing_keypairs == True:
        save_keypair(seed, public_key, private_key, valid_status)
        print(f"Keypair saved, keypair ssn: {get_ssn(public_key)}")

    return seed, public_key, private_key, valid_status
            

def save_keypair(seed, public_key, private_key, valid_status):
    kpk = KeypairParser(keypairs_file)

    # convert bytes to hex string if necessary
    if isinstance(seed, bytes):
        seed = seed.hex()
    if isinstance(public_key, bytes):
        public_key = public_key.hex()
    if isinstance(private_key, bytes):
        private_key = private_key.hex()

    keypair_data = {
        "seed": seed,
        "public_key": public_key,
        "private_key": private_key,
        "valid": bool(valid_status)  # make sure it's bool (boolymon)
    }

    kpk.append_keypair(keypair_data)
    print("[+] Keypair saved successfully.")



def save_contact(public_key):
    ssn = get_ssn(public_key)
    ctb = ContactParser(contacts_file)
    
    new_contact = {
        "name": ssn,
        "public_key": public_key
    }

    ctb.append_contact(new_contact)

def see_all_contacts():
    for c in contacts.get_all():
        print(f"{c['name']} -> {c['public_key']}")




def save_message(message_sender_public_key, message_receiver_public_key, message):

    msg = MessageParser(messages_file)

    message_obj = {
        "content": message,
        "sender_public_key": message_sender_public_key,
        "receiver_public_key": message_receiver_public_key,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    msg.append_message(message_obj)


def get_all_messages():
    for m in msg.get_all():
        print(f"[{m['timestamp']}] {m['content']}")



def random_content(word_count=30):
    syllables = ["ka", "ri", "do", "ma", "se", "to", "lu", "ven", "chi", "gra", "lo", "fa"]
    words = ["".join(random.choices(syllables, k=random.randint(2, 4))) for _ in range(word_count)]
    return " ".join(words).capitalize() + "."



# ---- tmsg ----

def test_message():
    print("\ndemo conversation: (CTRL+C to stop)\n")
    print("Generating keypair A (user 1)")
    seed_A, public_key_A, private_key_A, valid_status_A = new_keypair()
    print("Generating keypair B (user 2)")
    seed_B, public_key_B, private_key_B, valid_status_B = new_keypair()
    print("Keypairs generated...\n")

    print("Keypair A:")
    print(f"    seed: {seed_A}")
    print(f"    public key: {public_key_A}")
    print(f"    private key: {private_key_A}")
    print(f"    valid status: {valid_status_A}")
    print("\n")

    print("Keypair B:")
    print(f"    seed: {seed_B}")
    print(f"    public key: {public_key_B}")
    print(f"    private key: {private_key_B}")
    print(f"    valid status: {valid_status_B}")
    print("\n")

    print("Generating random message content...\n")
    random_words = random_content()
    print(f"Message content:\n{random_words}\n")
    
    print("Shaping message:")
    print(f"    Sender: {private_key_A}")
    print(f"    Receiver: {public_key_B}")
    print(f"    Content: {random_words}")

    encrypted_message = shape(public_key_A, public_key_B, random_words)

    print("Decrypting message with sender public key:")
    print(f"    Message receiver public key: {public_key_B}")
    print(f"    Message encrypted hex: {encrypted_message}")
    dm = decrypt_with_pub(encrypted_message, public_key_B)
    print(f"Decrypted message: {dm}")

    if dm == random_words:
        print("\nEncryption and decryption is valid\n")
        print("Performing handshake...")
    else:
        print("Error.")

    # perform handshake so both user A and B knew each other's public keys, repeat again forever
    cli()



# --- output section ---

def shape(message_sender_public_key, message_receiver_public_key, message):
    top_marking = "\n========== BEGIN ANI MESSAGE ==========\n\n"
    bottom_marking = "\n\n  ==========  END MESSAGE  =========="

    encrypted_message = encrypt(message_sender_public_key, message_receiver_public_key, message)
    timestamp = time.strftime("%d:%m:%Y %H:%M:%S")
    message_timestamp = f"\n\nSender's clock timezone: {timestamp}"
    
    integrity_of_message = check_integrity(message)
    integrity = f"\nMessage integrity: {integrity_of_message}"

    message_sender = message_sender_public_key
    ssn = f"\nSender SSN: {get_ssn(message_sender_public_key)}"

    message_signature, content_signature = sign(message_sender_public_key, message_receiver_public_key, message)
    signature1 = f"\nMessage signature: {message_signature}"
    signature2 = f"\nContent signature: {content_signature}\n"

    signature2_qr = generate_qr_ascii(content_signature, return_string=True)
    output_message = f"{top_marking}{encrypted_message}{bottom_marking}{message_timestamp}{integrity}{ssn}{signature1}{signature2}{signature2_qr}"
    
    cfg = ConfigurationParser(configuration_file)
    storing_messages = cfg.get("storing_messages")
    storing_contacts = cfg.get("storing_contacts")

    if storing_contacts == True:
        save_contact(message_receiver_public_key)

    if storing_messages == True:
        save_message(message_sender_public_key, message_receiver_public_key, message)

    
    print(output_message)

    return encrypted_message



    
# ---- init ----

def main():
    print(ASCII)
    load_client_config()
    load_user_config()
    try:
        cli()
    except KeyboardInterrupt:
        print(f"\n{timestamp} closing antidote")

if __name__ == "__main__":
    main()