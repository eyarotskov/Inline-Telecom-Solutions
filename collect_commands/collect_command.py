import yaml
from netmiko import ConnectHandler
import os

os_path = os.path.dirname(os.path.abspath('collect_commands.py'))

def send_show_command(device, commands,limit=3):
        with ConnectHandler(**device) as ssh:
            ssh.enable()
            result = ssh.send_command(commands)
        return (result)

def collect_command():
    with open(os_path + "/devices.yaml") as f:
        devices = yaml.safe_load(f)
        with open(os_path + "\\commands.txt", "r") as a:
            commands = a.read().splitlines()
            for dev in devices:
                folder = os_path + "\\" + dev['host']
                if not os.path.exists(folder):
                    folder = os.makedirs(os_path +   "\\" + dev['host'])
                for command in commands:
                    with open(str(folder) + "\\" + command +  ".txt", "w") as a:
                        a.write(dev['host'] + ">" +command + "\n" + str(send_show_command(dev, command) + "\n" +dev['host'] + ">"))
                    with open(str(folder) + command + dev['host'] + ".txt", "w") as a:
                        a.write(dev['host'] + ">" + command + "\n" + str(send_show_command(dev, command) + "\n" +dev['host'] + ">"))

if __name__ == "__main__":
    collect_command()
