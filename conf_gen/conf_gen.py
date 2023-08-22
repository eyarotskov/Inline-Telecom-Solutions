import os
from jinja2 import Environment, FileSystemLoader
import yaml

os_path = os.path.dirname(os.path.abspath('conf_gen.py'))

def create_directory():
    directory_nokia = os_path + '\\config_for_nokia'
    directory_show_cisco = os_path + '\\show_commands_for_cisco'
    directory_config_cisco = os_path + '\\config_for_cisco'
    if not os.path.exists(directory_nokia):
        os.makedirs(directory_nokia)
    elif not os.path.exists(directory_show_cisco):
        os.makedirs(directory_show_cisco)
    elif not os.path.exists(directory_config_cisco):
        os.makedirs(directory_config_cisco)

def generate_config(template,data_dict):
    templ_dir, templ_file = os.path.split(template)
    env = Environment(loader=FileSystemLoader(templ_dir), trim_blocks=True, lstrip_blocks=True)
    templ = env.get_template(templ_file)
    return templ.render(data_dict)

def vprn_nokia(template_file_nokia, data_file, vprn):
    dictionary = {}
    if os.path.exists(vprn):
        os.remove(vprn)
    with open(data_file) as f:
        for row in f:
            if not "vpn_id" in row:
                name_vrf = (row.split(";")[0])
                description = (row.split(";")[1])
                rd = (row.split(";")[2])
                rt_import = (row.split(";")[3])
                vpn_id = (row.split(";")[5].replace('\n', ""))
                dictionary['name_vrf'] = name_vrf
                dictionary['description'] = description
                dictionary['rd'] = rd
                dictionary['rt_import'] = rt_import
                dictionary['vpn_id'] = vpn_id
                config_nokia = generate_config(template_file_nokia,dictionary)
                with open (vprn, "a") as a:
                    a.write(config_nokia)

def show_vrf_cisco(template_file_show_cisco ,data_file, show_cisco):
    dictionary = {}
    if os.path.exists(show_cisco):
        os.remove(show_cisco)
    with open(data_file) as f:
        for row in f:
            if not "vpn_id" in row:
                name_vrf = (row.split(";")[0])
                dictionary['name_vrf'] = name_vrf
                show_commands_cisco = generate_config(template_file_show_cisco, dictionary)
                with open (show_cisco, "a") as a:
                    a.write(show_commands_cisco)


if __name__ == "__main__":
    data_file = os_path + "\\data_for_config\\vrf_create_table.csv"
    template_file_nokia = os_path +"\\templates\\vprn_create1.txt"
    template_file_show_cisco = os_path + "\\templates\\show_vrf.txt"
    vprn = os_path + "\\config_for_nokia\\vprn.txt"
    show_cisco = os_path + "\\show_commands_for_cisco\\show_ip_route_vrf.txt"
    create_directory()
    vprn_nokia(template_file_nokia,data_file,vprn)
    show_vrf_cisco(template_file_show_cisco,data_file,show_cisco)
