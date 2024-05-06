#!/bin/python3

import re
import csv
import os

os_path = os.path.dirname(os.path.abspath('cisco_config_parse.py'))

def find_config(folder):
    regex = ('.*.txt')
    list_files = os.listdir(folder)
    for file in list_files:
        match = re.finditer(regex, file)
        if match:
            for m in match:
                filename = m.group()
    return(filename)

def get_ip_from_cfg(confile):
    directory = os_path + '\\data_for_config'
    if not os.path.exists(directory):
        os.makedirs(directory)
    vrftable = os_path + '\\data_for_config\\vrf_create_table.csv'
    regex = ('ip vrf (\S+)\n'
    '(.*\n*)'
    ' rd (\S+)\n'
    ' route-target export (\S+)\n'
    ' route-target import (\S+)\n'
    )
    with open(confile) as a:
        match = re.finditer(regex, a.read())
    with open (vrftable,  "w", newline = '') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        #writer.writerow(["HOST A", "Lo0_Nokia", "name_vrf", "description_vrf", "rd", "rt_import",  "rt_export", "rt_i", "rt_e", "interface", "ip_address", "description", "vfi", "vpn_id"])
        writer.writerow(
            ["name_vrf", "description_vrf", "rd", "rt_import", "rt_export", "vpn_id"])
        if match:
            for m in match:
                vrf_name = m.group(1)
                rd = m.group(3)
                rt_import = m.group(4)
                description = m.group(2)
                if description:
                    description = re.search('description (.*)\n', m.group(2)).group(1)
                elif not description:description = m.group(1)
                vpn_id_in_rt_import = rt_import.split(":")[1]
                if len(vpn_id_in_rt_import) == 1:
                    vpn_id= "3000" + vpn_id_in_rt_import
                elif len(vpn_id_in_rt_import) == 2:
                    vpn_id= "300" + vpn_id_in_rt_import
                elif len(vpn_id_in_rt_import) == 3:
                    vpn_id= "30" + vpn_id_in_rt_import
                elif len(vpn_id_in_rt_import) == 4:
                    vpn_id= "3" + vpn_id_in_rt_import
                writer.writerow([vrf_name] + [description] + [rd] + [rt_import] + [" "] + [vpn_id])

def get_vpn_name_vpn_id(confile):
    regex = ('ip vrf (\S+)\n'
    '(.*\n*)'
    ' rd (\S+)\n'
    ' route-target export (\S+)\n'
    ' route-target import (\S+)\n'
    )
    result = {}
    with open(confile) as a:
        match = re.finditer(regex, a.read())
        if match:
            for m in match:
                vrf_name = m.group(1)
                rt_import = m.group(4)
                vpn_id_in_rt_import = rt_import.split(":")[1]
                if len(vpn_id_in_rt_import) == 1:
                    vpn_id= "3000" + vpn_id_in_rt_import
                elif len(vpn_id_in_rt_import) == 2:
                    vpn_id= "300" + vpn_id_in_rt_import
                elif len(vpn_id_in_rt_import) == 3:
                    vpn_id= "30" + vpn_id_in_rt_import
                elif len(vpn_id_in_rt_import) == 4:
                    vpn_id= "3" + vpn_id_in_rt_import
                result[vrf_name] = vpn_id
            return result

def ip_forwarding_vrf(filename):
    directory = os_path + '\\data_for_config'
    if not os.path.exists(directory):
        os.makedirs(directory)
    vrf_interfaces_table = os_path + '\\data_for_config\\vrf_interfaces_table.csv'
    regex = ('interface (\S+)\n'
             '(.*\n*)'
             ' ip vrf forwarding (\S+)\n'
             '.*\n*'
             'ip address (.*)\n'
             '(.*)')
    #vrf_interfaces_table = os_path + '\\data_for_config\\vrftable.csv'
    with open(filename) as a:
        match = re.finditer(regex, a.read())
    with open (vrf_interfaces_table, "w", newline = '') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["vpn_id","name_vrf","interface_vlan","ip_address", "ip_adress_secondary", "description"])
        if  match:
            for m in match:
                interface = m.group(1)
                if "description" in m.group(2):
                    description = re.search('description (.*)\n', m.group(2)).group(1)
                vrf = m.group(3)
                vpn_id = get_vpn_name_vpn_id(filename)[vrf]
                if "secondary" in m.group(4):
                    ip_address_secondary = re.search('ip address (/S+ /S+) secondary', m.group(4))
                    ip_address = m.group(5)
                    writer.writerow([vpn_id] + [vrf] + [interface] + [ip_address] + [ip_address_secondary] + [description])

def ip_mask(ip_address):
    if " 255.255.255.252" in ip_address:
        ip_address = ip_address.replace(" 255.255.255.252", "/30")
    elif " 255.255.255.255" in ip_address:
        ip_address = ip_address.replace(" 255.255.255.255", "/32")
    elif " 255.255.255.248" in ip_address:
        ip_address = ip_address.replace(" 255.255.255.248", "/29")
    elif " 255.255.255.240" in ip_address:
        ip_address = ip_address.replace(" 255.255.255.240", "/28")
    elif " 255.255.255.0" in ip_address:
        ip_address = ip_address.replace(" 255.255.255.0", "/24")
    elif " 255.255.254.0" in ip_address:
        ip_address = ip_address.replace(" 255.255.254.0", "/23")
    elif " 255.255.255.192" in ip_address:
        ip_address = ip_address.replace(" 255.255.255.192", "/26")
    elif " 255.255.0.0" in ip_address:
        ip_address = ip_address.replace(" 255.255.0.0", "/16")
    elif " 255.255.224.0" in ip_address:
        ip_address = ip_address.replace(" 255.255.224.0", "/19")
    elif " 255.255.248.0" in ip_address:
        ip_address = ip_address.replace(" 255.255.248.0", "/21")
    elif " 255.255.252.0" in ip_address:
        ip_address = ip_address.replace(" 255.255.252.0", "/22")
    elif " 255.255.240.0" in ip_address:
        ip_address = ip_address.replace(" 255.255.240.0", "/20")
    elif " 255.255.255.224" in ip_address:
        ip_address = ip_address.replace(" 255.255.255.224", "/27")
    elif " 255.255.192.0" in ip_address:
        ip_address = ip_address.replace(" 255.255.192.0", "/18")
    elif " 255.255.255.128" in ip_address:
        ip_address = ip_address.replace(" 255.255.255.128", "/25")
    return ip_address

def interfaces_vrf(filename):
    directory = os_path + '\\data_for_config'
    if not os.path.exists(directory):
        os.makedirs(directory)
    vrf_interfaces_table = os_path + '\\data_for_config\\vrf_interfaces_table.csv'
    with open (vrf_interfaces_table, "w", newline = '') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["vpn_id","name_vrf","interface_vlan","ip_address", "ip_address_secondary", "description"])
        with open(filename) as a:
            content = a.read()
            diff_list = content.split("\n")
            for n, line in enumerate(diff_list):
                if "Vlan" in line:
                    if "ip vrf forwarding" in diff_list[n+2]:
                        interface = re.search('interface (.*)',line).group(1)
                        vrf = re.search('ip vrf forwarding (.*)', diff_list[n+2]).group(1)
                        vpn_id = get_vpn_name_vpn_id(filename)[vrf]
                        if "description" in diff_list[n + 1]:
                            description = re.search('description (.*)', diff_list[n+1]).group(1)
                        else:
                            description = ""
                        writer.writerow([vpn_id] + [vrf] + [interface] + [ip_address] + [ip_address_secondary] + [description])
                    if "ip vrf forwarding" in diff_list[n+1]:
                        interface = re.search('interface (.*)',line).group(1)
                        vrf = re.search('ip vrf forwarding (.*)', diff_list[n+1]).group(1)
                        vpn_id = get_vpn_name_vpn_id(filename)[vrf]
                        description = ""
                        writer.writerow([vpn_id] + [vrf] + [interface] + [ip_address] + [ip_address_secondary] + [description])
                    elif "ip vrf forwarding" in diff_list[n+3]:
                        print(line)
                        ip_address = []
                        interface = re.search('interface (.*)',line).group(1)
                        vrf = re.search('ip vrf forwarding (.*)', diff_list[n+3]).group(1)
                        vpn_id = get_vpn_name_vpn_id(filename)[vrf]
                        if "description" in diff_list[n + 1]:
                            description = re.search('description (.*)', diff_list[n+1]).group(1)
                        else:
                            description = ""
                        if "ip address" in diff_list[n+4]:
                            if "secondary" in diff_list[n+4]:
                                ip_address_secondary = ip_mask(re.search('ip address (.*) secondary', diff_list[n+4]).group(1))
                            else:
                                ip_address.append(ip_mask(re.search('ip address (.*)', diff_list[n+4]).group(1)))
                                ip_address_secondary = ""
                        if "ip address" in diff_list[n+5]:
                            if "secondary" in diff_list[n+5]:
                                ip_address_secondary = ip_mask(re.search('ip address (.*) secondary', diff_list[n+5]).group(1))
                            else:
                                ip_address.append(ip_mask(re.search('ip address (.*)', diff_list[n+5]).group(1)))
                                ip_address_secondary = ""
                        writer.writerow([vpn_id] + [vrf] + [interface] + [ip_address] + [ip_address_secondary] + [description])
                    elif "ip vrf forwarding" in diff_list[n+4]:
                        interface = re.search('interface (.*)',line).group(1)
                        vrf = re.search('ip vrf forwarding (.*)', diff_list[n+4]).group(1)
                        vpn_id = get_vpn_name_vpn_id(filename)[vrf]
                        if "description" in diff_list[n + 1]:
                            description = re.search('description (.*)', diff_list[n+1]).group(1)
                        else:
                            description = ""
                        if "service-policy" in diff_list[n+1]:
                            service_policy = re.search('service-policy (.*)', diff_list[n+1]).group(1)
                        elif "service-policy" in diff_list[n+2]:
                            service_policy = re.search('service-policy (.*)', diff_list[n + 2]).group(1)
                        else:
                            service_policy = ""
                        writer.writerow([vpn_id] + [vrf] + [interface] + [ip_address] + [ip_address_secondary] + [description])

def interface_l2_vfi(filename):
    regex = ('interface (\S+)\n'
             ' (.*\n*){2,4}'
             ' xconnect vfi (\S+)\n')
    result_vfi = {}
    with open(filename) as a:
        match = re.finditer(regex, a.read())
        for m in match:
                interface_name = m.group(1)
                l2vpn = m.group(3)
                result_vfi[l2vpn] =interface_name
        return (result_vfi)

def l2vfi(filename):
    directory = os_path + '\\data_for_config'
    if not os.path.exists(directory):
        os.makedirs(directory)
    l2vfi_table = os_path + '\\data_for_config\\l2vfi_table.csv'
    dict_vfi = {}
    dict_correct = {}
    with open(l2vfi_table, "w", newline='') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["interface_vlan", "vfi_id", "vfi_name", "neighbor"])
    with open(filename) as a:
        for line in a:
            if "l2 vfi" in line:
                vfi_name = re.search('l2 vfi (\S+) manual \n', line).group(1)
            elif "vpn id" in line:
                vpn = re.search(' vpn id (\S+)\n', line).group(1)
            elif "neighbor" in line:
                if "encapsulation mpls" in  line:
                    neighbor_l2_vfi = re.search(' neighbor (\S+) encapsulation mpls\n', line).group(1)
                dict_vfi[vfi_name] = neighbor_l2_vfi
    for key, value in interface_l2_vfi(filename).items():
            if key == vfi_name:
                interface = key
                dict_correct[key] = interface_l2_vfi(filename)[vfi_name]
            else:
                pass
    with open(l2vfi_table, "a", newline='') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow([dict_correct[interface]] + [vpn] + [interface] + [neighbor_l2_vfi])

def xconnect_service_instance(filename):
    directory = os_path + '\\data_for_config'
    if not os.path.exists(directory):
        os.makedirs(directory)
    l2xconnect_table = os_path + '\\data_for_config\\l2xconnect_table.csv'
    regex = (' service instance \d+ \S+\n'
             '  description (.*)\n'
             '  encapsulation dot1q (\S+) second-dot1q (\S+)\n*'
             '  .*\n*'
             '  xconnect (\S+) (\S+) encapsulation mpls\n'
             )
    with open(filename) as a:
        match = re.finditer(regex, a.read())
        for m in match:
            description = m.group(1)
            dot1q = m.group(2)
            second_dot1q = m.group(3)
            id = m.group(5)
            neighbor = m.group(4)
            neighbor_interface = ""
            neighbor_type = ""
            status = ""
            with (open(l2xconnect_table, "a", newline='') as f):
                writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
                writer.writerow([""] + [""] + [""] + [dot1q] + [second_dot1q] + [id] + [description] + [neighbor] + [status] + [""] + [""] + [neighbor_interface] + [neighbor_type])

def ssh_to_neighbor_xconnect(id,neighbor):
    pass

def ssh_to_neighbor_xconnect(device,command):
    with ConnectHandler(**device) as ssh:
        ssh.enable()
        result = ssh.send_command(command)
    return (result)

def collect_command(neighbor,id):
    devices = {
        "device_type": "cisco_ios_telnet",
        "username": "admin",
        "password": "admin123",
        "ip": neighbor}
    show_version = "show version"
    commands = ("show mpls l2transport vc" + " " + id + " "  + "detail")
    result_show_version = ssh_to_neighbor_xconnect(devices, show_version)
    if "Cisco" in result_show_version:
        result = ssh_to_neighbor_xconnect(devices,commands)
    if "Eth" in result:
        interface = re.search('Eth (\S+ \S+) ', result).group(1)
        neighbor_type = "Cisco"
        status = re.search('line protocol (\S+),', result).group(1)
    return (interface, neighbor_type, status)

def xconnect(filename):
    directory = os_path + '\\data_for_config'
    if not os.path.exists(directory):
        os.makedirs(directory)
    l2xconnect_table0 = os_path + '\\data_for_config\\l2xconnect_table0.csv'
    with (open(l2xconnect_table0, "w", newline='') as f):
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["hostname_nokia", "loopback_nokia", "interface_xconnect", "dot1q", "second-dot1q","xconnect_id", "description", "neighbor", "service_policy", "status", "sdp", "neighbor_hostname", "neighbor_interface", "neighbor_type"])
        with open(filename) as a:
            content = a.read()
            diff_list = content.split("\n")
            for n, line in enumerate(diff_list):
                if "xconnect" in line and not "vfi" in line:
                    if "interface" in diff_list[n-9]:
                        interface = re.search('interface (.*)', diff_list[n-9]).group(1)
                        if "description" in diff_list[n - 8]:
                            description = re.search('description (.*)', diff_list[n-8]).group(1)
                        else:
                            description = ""
                        neighbor = re.search('xconnect (.*) (.*) encapsulation mpls', line).group(1)
                        id = re.search('xconnect (.*) (.*) encapsulation mpls', line).group(2)
                        if "service-policy" in diff_list[n+1]:
                            service_policy = re.search('service-policy (.*)', diff_list[n+1]).group(1)
                        elif "service-policy" in diff_list[n+2]:
                            service_policy = re.search('service-policy (.*)', diff_list[n + 2]).group(1)
                        else:
                            service_policy = ""
                        writer.writerow([""] + [""] + [interface] + [""] + [""] + [id] + [description] + [neighbor] + [service_policy]+[""] + [""] + [""] + [""] + [""])
                    elif "interface" in diff_list[n-8] and not "!" in diff_list[n-5]:
                        interface = re.search('interface (.*)', diff_list[n-8]).group(1)
                        if "description" in diff_list[n - 7]:
                            description = re.search('description (.*)', diff_list[n-7]).group(1)
                        else:
                            description = ""
                        neighbor = re.search('xconnect (.*) (.*) encapsulation mpls', line).group(1)
                        id = re.search('xconnect (.*) (.*) encapsulation mpls', line).group(2)
                        if "service-policy" in diff_list[n+1]:
                            service_policy = re.search('service-policy (.*)', diff_list[n+1]).group(1)
                        elif "service-policy" in diff_list[n+2]:
                            service_policy = re.search('service-policy (.*)', diff_list[n + 2]).group(1)
                        else:
                            service_policy = ""
                        writer.writerow([""] + [""] + [interface] + [""] + [""] + [id] + [description] + [neighbor] + [service_policy]+[""] + [""] + [""] + [""] + [""])
                    elif "interface" in diff_list[n-7]:
                        interface = re.search('interface (.*)', diff_list[n-7]).group(1)
                        if "description" in diff_list[n - 6]:
                            description = re.search('description (.*)', diff_list[n-6]).group(1)
                        else:
                            description = ""
                        neighbor = re.search('xconnect (.*) (.*) encapsulation mpls', line).group(1)
                        id = re.search('xconnect (.*) (.*) encapsulation mpls', line).group(2)
                        if "service-policy" in diff_list[n+1]:
                            service_policy = re.search('service-policy (.*)', diff_list[n+1]).group(1)
                        elif "service-policy" in diff_list[n+2]:
                            service_policy = re.search('service-policy (.*)', diff_list[n + 2]).group(1)
                        else:
                            service_policy = ""
                        writer.writerow([""] + [""] + [interface] + [""] + [""] + [id] + [description] + [neighbor] + [service_policy]+[""] + [""] + [""] + [""] + [""])
                    elif "interface" in diff_list[n-14] and not "!" in diff_list[n-6] and not "!" in diff_list[n-7]:
                        interface = re.search('interface (.*)', diff_list[n-14]).group(1)
                        if "description" in diff_list[n - 13]:
                            description = re.search('description (.*)', diff_list[n-13]).group(1)
                        else:
                            description = ""
                        neighbor = re.search('xconnect (.*) (.*) encapsulation mpls', line).group(1)
                        id = re.search('xconnect (.*) (.*) encapsulation mpls', line).group(2)
                        if "service-policy" in diff_list[n+1]:
                            service_policy = re.search('service-policy (.*)', diff_list[n+1]).group(1)
                        elif "service-policy" in diff_list[n+2]:
                            service_policy = re.search('service-policy (.*)', diff_list[n + 2]).group(1)
                        else:
                            service_policy = ""
                        writer.writerow([""] + [""] + [interface] + [""] + [""] + [id] + [description] + [neighbor] + [service_policy]+[""] + [""] + [""] + [""] + [""])
                    elif "interface" in diff_list[n-5]:
                        interface = re.search('interface (.*)', diff_list[n-5]).group(1)
                        if "description" in diff_list[n - 4]:
                            description = re.search('description (.*)', diff_list[n-4]).group(1)
                        else:
                            description = ""
                        neighbor = re.search('xconnect (.*) (.*) encapsulation mpls', line).group(1)
                        id = re.search('xconnect (.*) (.*) encapsulation mpls', line).group(2)
                        if "service-policy" in diff_list[n+1]:
                            service_policy = re.search('service-policy (.*)', diff_list[n+1]).group(1)
                        elif "service-policy" in diff_list[n+2]:
                            service_policy = re.search('service-policy (.*)', diff_list[n + 2]).group(1)
                        else:
                            service_policy = ""
                        writer.writerow([""] + [""] + [interface] + [""] + [""] + [id] + [description] + [neighbor] + [service_policy]+[""] + [""] + [""] + [""] + [""])
                    elif "interface" in diff_list[n-6]:
                        interface = re.search('interface (.*)', diff_list[n-6]).group(1)
                        if "description" in diff_list[n - 5]:
                            description = re.search('description (.*)', diff_list[n-5]).group(1)
                        else:
                            description = ""
                        neighbor = re.search('xconnect (.*) (.*) encapsulation mpls', line).group(1)
                        id = re.search('xconnect (.*) (.*) encapsulation mpls', line).group(2)
                        if "service-policy" in diff_list[n+1]:
                            service_policy = re.search('service-policy (.*)', diff_list[n+1]).group(1)
                        elif "service-policy" in diff_list[n+2]:
                            service_policy = re.search('service-policy (.*)', diff_list[n + 2]).group(1)
                        else:
                            service_policy = ""
                        writer.writerow([""] + [""] + [interface] + [""] + [""] + [id] + [description] + [neighbor] + [service_policy]+[""] + [""] + [""] + [""] + [""])
                    elif "interface" in diff_list[n-4]:
                        interface = re.search('interface (.*)', diff_list[n-4]).group(1)
                        if "description" in diff_list[n-3]:
                            description = re.search('description (.*)', diff_list[n-3]).group(1)
                        else:
                            description = ""
                        neighbor = re.search('xconnect (.*) (.*) encapsulation mpls', line).group(1)
                        id = re.search('xconnect (.*) (.*) encapsulation mpls', line).group(2)
                        if "service-policy" in diff_list[n+1]:
                            service_policy = re.search('service-policy (.*)', diff_list[n+1]).group(1)
                        elif "service-policy" in diff_list[n+2]:
                            service_policy = re.search('service-policy (.*)', diff_list[n + 2]).group(1)
                        else:
                            service_policy = ""
                        writer.writerow([""] + [""] + [interface] + [""] + [""] + [id] + [description] + [neighbor] + [service_policy]+[""] + [""] + [""] + [""] + [""])
                    elif "service instance" in diff_list[n - 4]:
                        if "description" in diff_list[n - 3]:
                            description = re.search('description (.*)', diff_list[n - 3]).group(1)
                        else:
                            description = ""
                        neighbor = re.search('xconnect (.*) (.*) encapsulation mpls', line).group(1)
                        id = re.search('xconnect (.*) (.*) encapsulation mpls', line).group(2)
                        if "second" in diff_list[n-2]:
                            dot1q = re.search('encapsulation dot1q (.*) second-dot1q (.*)', diff_list[n-2]).group(1)
                            second_dot1q = re.search('encapsulation dot1q (.*) second-dot1q (.*)', diff_list[n-2]).group(2)
                        else:
                            dot1q = re.search('encapsulation dot1q (.*)', diff_list[n - 2]).group(1)
                            second_dot1q = ""
                        if "service-policy" in diff_list[n + 1]:
                            service_policy = re.search('service-policy (.*)', diff_list[n + 1]).group(1)
                        elif "service-policy" in diff_list[n + 2]:
                            service_policy = re.search('service-policy (.*)', diff_list[n + 2]).group(1)
                        else:
                            service_policy = ""
                        writer.writerow([""] + [""] + [""] + [dot1q] + [second_dot1q] + [id] + [description] + [neighbor] + [service_policy] + [""] + [""] + [""] + [""] + [""])

def dictionary_dot1q_from_bridge_domain():
    directory = os_path + '\\data_for_config'
    if not os.path.exists(directory):
        os.makedirs(directory)
    l2xconnect_table = os_path + '\\data_for_config\\service_instance_table.csv'
    filename = find_config(os_path)
    dictionary = {}
    with (open(l2xconnect_table, "w", newline='') as f):
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow([ "description","interface_vlan", "dot1q", "second-dot1q", "split-horizon", "service-policy 1", "service-policy 2"])
        with open(filename) as a:
            content = a.read()
            diff_list = content.split("\n")
            description = ""
            second_dot1q = ""
            interface_vlan = ""
            split_horizon = ""
            service_policy = ""
            for n, line in enumerate(diff_list):
                if "service instance" in line:
                    if "bridge-domain" in diff_list[n+5] and not "shutdown" in diff_list[n+4]:
                        print(diff_list[n+4])
                        description = re.search('description (.*)', diff_list[n+1]).group(1)
                        if "second" in diff_list[n + 2]:
                            dot1q = re.search('encapsulation dot1q (\S+) second-dot1q (.*)', diff_list[n + 2]).group(1)
                            second_dot1q = re.search('encapsulation dot1q (\S+) second-dot1q (.*)', diff_list[n + 2]).group(2)
                        else:
                            dot1q = re.search('encapsulation dot1q (\S+)', diff_list[n + 2]).group(1)
                            second_dot1q = ""
                        interface_vlan = re.search('bridge-domain (\S+).*', diff_list[n + 5]).group(1)
                        split_horizon = re.search('bridge-domain (\S+)(.*)', diff_list[n + 5]).group(2)
                        service_policy_1 = re.search('service-policy (.*)', diff_list[n + 4]).group(1)
                        writer.writerow([description] + [interface_vlan] + [dot1q] + [second_dot1q] + [split_horizon] + [service_policy_1])
                    elif "bridge-domain" in diff_list[n+4] and not "shutdown" in diff_list[n+3] and "description" in diff_list[n+1]:
                        print(diff_list[n+3])
                        description = re.search('description (.*)', diff_list[n+1]).group(1)
                        if "second" in diff_list[n + 2]:
                            dot1q = re.search('encapsulation dot1q (\S+) second-dot1q (.*)', diff_list[n + 2]).group(1)
                            second_dot1q = re.search('encapsulation dot1q (\S+) second-dot1q (.*)', diff_list[n + 2]).group(2)
                        else:
                            dot1q = re.search('encapsulation dot1q (\S+)', diff_list[n + 2]).group(1)
                            second_dot1q = ""
                        interface_vlan = re.search('bridge-domain (\S+).*', diff_list[n + 4]).group(1)
                        split_horizon = re.search('bridge-domain (\S+)(.*)', diff_list[n + 4]).group(2)
                        if "service-policy" in diff_list[n+3]:
                            service_policy_1 = re.search('service-policy (.*)', diff_list[n + 3]).group(1)
                        else:
                            service_policy_1 = ""
                        writer.writerow([description] + [interface_vlan] + [dot1q] + [second_dot1q] + [split_horizon] + [service_policy_1])
                    elif "bridge-domain" in diff_list[n+3] and not "shutdown" in diff_list[n+2] and not "description" in diff_list[n+1]:
                        #print(diff_list[n+3])
                        #description = re.search('description (.*)', diff_list[n+1]).group(1)
                        if "second" in diff_list[n + 1]:
                            dot1q = re.search('encapsulation dot1q (\S+) second-dot1q (.*)', diff_list[n + 1]).group(1)
                            second_dot1q = re.search('encapsulation dot1q (\S+) second-dot1q (.*)', diff_list[n + 1]).group(2)
                        else:
                            dot1q = re.search('encapsulation dot1q (\S+)', diff_list[n + 1]).group(1)
                            second_dot1q = ""
                        interface_vlan = re.search('bridge-domain (\S+).*', diff_list[n + 3]).group(1)
                        split_horizon = re.search('bridge-domain (\S+)(.*)', diff_list[n + 3]).group(2)
                        if "service-policy" in diff_list[n+2]:
                            service_policy_1 = re.search('service-policy (.*)', diff_list[n + 2]).group(1)
                        else:
                            service_policy_1 = ""
                        writer.writerow([description] + [interface_vlan] + [dot1q] + [second_dot1q] + [split_horizon] + [service_policy_1])
                    elif "bridge-domain" in diff_list[n+2] and not "shutdown" in diff_list[n+1] and not "description" in diff_list[n+1]:
                        #print(diff_list[n+3])
                        #description = re.search('description (.*)', diff_list[n+1]).group(1)
                        if "second" in diff_list[n + 1]:
                            dot1q = re.search('encapsulation dot1q (\S+) second-dot1q (.*)', diff_list[n + 1]).group(1)
                            second_dot1q = re.search('encapsulation dot1q (\S+) second-dot1q (.*)', diff_list[n + 1]).group(2)
                        else:
                            dot1q = re.search('encapsulation dot1q (\S+)', diff_list[n + 1]).group(1)
                            second_dot1q = ""
                        interface_vlan = re.search('bridge-domain (\S+).*', diff_list[n + 2]).group(1)
                        split_horizon = re.search('bridge-domain (\S+)(.*)', diff_list[n + 2]).group(2)
                        if "service-policy" in diff_list[n+1]:
                            service_policy_1 = re.search('service-policy (.*)', diff_list[n + 1]).group(1)
                        else:
                            service_policy_1 = ""
                        writer.writerow([description] + [interface_vlan] + [dot1q] + [second_dot1q] + [split_horizon] + [service_policy_1])
                    elif "bridge-domain" in diff_list[n+6] and not "shutdown" in diff_list[n+5]:
                        #print(diff_list[n+4])
                        description = re.search('description (.*)', diff_list[n+1]).group(1)
                        if "second" in diff_list[n + 2]:
                            dot1q = re.search('encapsulation dot1q (\S+) second-dot1q (.*)', diff_list[n + 2]).group(1)
                            second_dot1q = re.search('encapsulation dot1q (\S+) second-dot1q (.*)', diff_list[n + 2]).group(2)
                        else:
                            dot1q = re.search('encapsulation dot1q (\S+)', diff_list[n + 2]).group(1)
                            second_dot1q = ""
                        interface_vlan = re.search('bridge-domain (\S+).*', diff_list[n + 6]).group(1)
                        split_horizon = re.search('bridge-domain (\S+)(.*)', diff_list[n + 6]).group(2)
                        service_policy_1 = re.search('service-policy (.*)', diff_list[n + 5]).group(1)
                        service_policy_2 = re.search('service-policy (.*)', diff_list[n + 4]).group(1)
                        writer.writerow([description] + [interface_vlan] + [dot1q] + [second_dot1q] + [split_horizon] + [service_policy_1] + [service_policy_2])
        return dictionary
                        
def function(folder):
    filename = find_config(folder)
    get_ip_from_cfg(filename)
    interface_l2_vfi(filename)
    l2vfi(filename)
    xconnect(filename)
    xconnect_service_instance(filename)
    dictionary_dot1q_from_bridge_domain()
    interfaces_vrf(filename)
    get_vpn_name_vpn_id(filename)

function(os_path)
