import re
import csv
import os

os_path = os.path.dirname(os.path.abspath('conf+parse.py'))

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
    result = []
    vrf_result = []
    with open(confile) as a:
        match = re.finditer(regex, a.read())
    with open (vrftable,  "w", newline = '') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            ["name_vrf", "description_vrf", "rd", "rt_import", "vpn_id"])
        if match:
            for m in match:
                #print(match)
                vrf_name = m.group(1)
                rd = m.group(3)
                rt_import = m.group(4)
                description = m.group(2)
                if description:
                    description = re.search('description (.*)\n', m.group(2)).group(1)
                elif not description:description = m.group(1)
                vpn_id_in_rt_import = rt_import.split(":")[1]
                print(vpn_id_in_rt_import)
                if len(vpn_id_in_rt_import) == 1:
                    vpn_id= "3000" + vpn_id_in_rt_import
                elif len(vpn_id_in_rt_import) == 2:
                    vpn_id= "300" + vpn_id_in_rt_import
                elif len(vpn_id_in_rt_import) == 3:
                    vpn_id= "30" + vpn_id_in_rt_import
                elif len(vpn_id_in_rt_import) == 4:
                    vpn_id= "3" + vpn_id_in_rt_import
                writer.writerow([vrf_name] + [description] + [rd] + [rt_import] + [vpn_id])

def ip_forwarding_vrf(filename):
    regex = ('interface (\S+)\n'
             '(.*\n*)'
             ' ip vrf forwarding (\S+)\n'
             '.*\n*'
             'ip address (\S+ \S+)\n')
    vrf_interfaces_table = os_path + '\\data_for_config\\vrftable.csv'
    with open(filename) as a:
        result = []
        match = re.finditer(regex, a.read())
    with open (vrf_interfaces_table, "w", newline = '') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["vpn_id","name_vrf","interface_vlan"])
        if  match:
            for m in match:
                inter = m.group(1)
                if "description" in m.group(2):
                    inter_description = re.search('description (.*)\n', m.group(2)).group(1)
                vrf = m.group(3)
                ip_mask = m.group(4)
                result.append(m.groups())
                writer.writerow([" "] + [" "] + [vrf] + [" "] + [" "] + [" "] + [" "] + [" "] + [" "] + [inter] + [ip_mask] + [inter_description])

def l2_vfi(filename, table):
    get_ip_from_cfg(filename)
    ip_forwarding_vrf(filename)
    with open (table,  "a", newline = '') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
    with open(filename) as a:
        regex = ('l2 vfi (\S+) manual \n'
                 '.*\n*'
                 ' vpn id (\S+)\n'
                 '.*\n*'
                 ' neighbor (\S+) encapsulation mpls\n')
        rresult = []
        for line in a:
            if "l2 vfi" in line:
                vfi_name = re.search('l2 vfi (\S+) manual \n', line).group(1)
            elif "vpn id" in line:
                vpn = re.search(' vpn id (\S+)\n', line).group(1)
            elif "neighbor" in line:
                if "encapsulation mpls" in  line:
                    neighbor_l2_vfi = re.search(' neighbor (\S+) encapsulation mpls\n', line).group(1)
                    rresult.append(vfi_name + vpn + neighbor_l2_vfi)
                    with open (table,  "a", newline = '') as f:
                        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
                        writer.writerow([" "] + [" "] + [" "] + [" "] + [" "] + [" "] + [" "] + [" "] + [" "] + [" "] + [" "] + [" "] + [vfi_name] + [vpn] + [neighbor_l2_vfi])

def interface_l2(filename,table):
    with open(filename) as a:
        regex = ('interface (\S+)\n'
                 '(.*\n*)'
                 ' ip vrf forwarding (\S+)\n'
                 '.*\n*'
                 'ip address (\S+ \S+)\n')
        result = []
        match = re.finditer(regex, a.read())
    with open (table,  "a", newline = '') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        if  match:
            for m in match:
            inter = m.group(1)
            if "description" in m.group(2):
            inter_description = re.search('description (.*)\n', m.group(2)).group(1)
            vrf = m.group(3)
            ip_mask = m.group(4)
            result.append(m.groups())
            writer.writerow([" "] + [" "] + [vrf] + [" "] + [" "] + [" "] + [" "] + [" "] + [" "] + [inter] + [ip_mask] + [inter_description])


def l2_epipe(filename):
    with open(filename) as a:
        regex = ('interface (\S+)\n'
                 ' description (.*)\n'
                 ' .*\n*'
                 ' .*\n*'
                 ' .*\n*'
                 ' xconnect (\S+) (\S+) encapsulation mpls\n')
        result = []
        match = re.finditer(regex, a.read())
    with open (table,  "a", newline = '') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        if  match:
            for m in match:
              inter_xconnect = m.group(1)
              vrf_xconnect = m.group(2)
              ip_mask_xconnect = m.group(3)
              vc_id_xconnect = m.group(4)
              result.append(m.groups())
              writer.writerow([" "] + [" "] + [" "] + [" "] + [" "] + [" "] + [" "] + [" "] + [" "] + [inter_xconnect] + [vrf_xconnect]+ [vrf_xconnect] + [" "] + [ip_mask_xconnect] + [vc_id_xconnect])

if __name__ == "__main__":
    filename = find_config(folder)
    get_ip_from_cfg(filename)
    l2_vfi(filename)
    l2_epipe(filename)
    ip_forwarding_vrf(filename)
    service_instance(filename)  
