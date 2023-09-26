import xlrd
import ipaddress
import openpyxl
import re
import tempfile
import os
import pyexcel_xlsx
from flask import  request

def generate_router_config(file, config_type):
    
    workbook = xlrd.open_workbook(file_contents=file.read())
    # Le reste de votre code pour générer le script de configuration
    # Load IP PLAN sheet
    #sheet_IP_PLAN = workbook.sheet_by_name("IP PLAN")

    config_script = ""
            # Check the selected configuration type and generate corresponding configuration
    if config_type == 'default':
        
        sheet_IP_PLAN = workbook.sheet_by_name("IP PLAN")

                # Generate configuration for New Site Config
                # ... (your logic here)

        # Generate router configuration script dynamically
        header_row = [header.lower().replace(' ', '') for header in sheet_IP_PLAN.row_values(0)]

        router_name_col = header_row.index('router')
        site_name_col = header_row.index('radio_site_name')

        interface_col_x = header_row.index('interface')
        vlan_col_x_2G = header_row.index('vlan2g')
        ip_address_col_x_2G = header_row.index('2g')
        vlan_col_x_3G = header_row.index('vlan3g')
        ip_address_col_x_3G = header_row.index('3g')
        vlan_col_x_Management = header_row.index('vlanmanagement')
        ip_address_col_x_Management = header_row.index('management')
        vlan_col_x_4G = header_row.index('vlan4g')
        ip_address_col_x_4G = header_row.index('ip4g')

        vlan_cols = [vlan_col_x_2G, vlan_col_x_3G, vlan_col_x_Management, vlan_col_x_4G]
        ip_adresses_cols = [ip_address_col_x_2G, ip_address_col_x_3G, ip_address_col_x_Management, ip_address_col_x_4G]


        for row in range(2, sheet_IP_PLAN.nrows):
            router_name = sheet_IP_PLAN.cell_value(row, router_name_col)
            site_name = sheet_IP_PLAN.cell_value(row, site_name_col)
            
            interface = sheet_IP_PLAN.cell_value(row, interface_col_x)   
            config_script += f"""
            -------------
            Router_name: {router_name}
            -------------

            #
            interface {interface}
            description TO_{site_name}
            undo shutdown
            #
            """

            for vlan_col, ip_add_col in zip(vlan_cols, ip_adresses_cols):
                vlan = int(sheet_IP_PLAN.cell_value(row, vlan_col))
                ip_with_mask = sheet_IP_PLAN.cell_value(row, ip_add_col)
                ip_address, prefix_length = ip_with_mask.split('/')

                try:
                    ip_address_obj = ipaddress.IPv4Address(ip_address)
                except ipaddress.AddressValueError:
                    print(f"Invalid IP address in Row {row}: {ip_address}")
                    continue

                prefix_length = int(prefix_length)
                subnet_mask = '.'.join(['255'] * (prefix_length // 8) + [str(256 - (2 ** (8 - prefix_length % 8)))])
                subnet = ip_address.split('.')
                subnet[-1] = str(int(subnet[-1]) + 2)  # Increment the last octet by 2 to get the third address in the subnet
                interface_ip = '.'.join(subnet)

            #  print(f"Interface IP Address for Row {row}: {interface_ip} /{prefix_length} (Subnet Mask: {subnet_mask})")  
                
                if vlan in [10, 20, 30, 40, 50, 60, 70, 80]:
                    network_type = "2G"
                elif vlan in [11, 21, 31, 41, 51, 61, 71, 81]:
                    network_type = "3G"
                elif vlan in [13, 23, 33, 43, 53, 63, 73, 83]:
                    network_type = "4G"
                elif vlan in [12, 22, 32, 42, 52, 62, 72, 82]:
                    network_type = "Management"
                else:
                    network_type = "Unknown"

                config_script += f"""

                interface {interface}.{vlan}
                vlan-type dot1q {vlan}
                description {network_type}_{site_name}
                ip binding vpn-instance vpn_name({network_type})
                ip address {interface_ip} {subnet_mask}
                #
                """

        # Print the generated configuration script
        print(config_script)



        # Create a new file to store the configuration
        output_file = 'router_configuration.txt'

        # Open the file in write mode and write the configuration
        with open(output_file, 'w') as file:
            # Write the entire config_script to the file    
            file.write(config_script)

        # Configuration saved to 'router_configuration.txt' file
        print("Configuration saved to 'router_configuration.txt' file.")

        # Retourne le script de configuration généré sous forme de chaîne
        return config_script

    elif config_type == '4g_fdd':
        # Generate configuration for 4G FDD Config

        sheet_IP_PLAN = workbook.sheet_by_name("IP PLAN")   

        # Generate router configuration script dynamically
        header_row = [header.lower().replace(' ', '') for header in sheet_IP_PLAN.row_values(0)]

        router_name_col = header_row.index('router')
        site_name_col = header_row.index('radio_site_name')

        interface_col_x = header_row.index('interface')
        vlan_col_x_4G = header_row.index('vlan4g')
        ip_address_col_x_4G = header_row.index('ip4g')

        vlan_cols = [vlan_col_x_4G]
        ip_adresses_cols = [ip_address_col_x_4G]


        for row in range(2, sheet_IP_PLAN.nrows):
            router_name = sheet_IP_PLAN.cell_value(row, router_name_col)
            site_name = sheet_IP_PLAN.cell_value(row, site_name_col)
            
            interface = sheet_IP_PLAN.cell_value(row, interface_col_x)   
            config_script += f"""
            -------------
            Router_name: {router_name}
            -------------

            #
            interface {interface}
            description TO_{site_name}
            undo shutdown
            #
            """

            for vlan_col, ip_add_col in zip(vlan_cols, ip_adresses_cols):
                vlan = int(sheet_IP_PLAN.cell_value(row, vlan_col))
                ip_with_mask = sheet_IP_PLAN.cell_value(row, ip_add_col)
                ip_address, prefix_length = ip_with_mask.split('/')

                try:
                    ip_address_obj = ipaddress.IPv4Address(ip_address)
                except ipaddress.AddressValueError:
                    print(f"Invalid IP address in Row {row}: {ip_address}")
                    continue

                prefix_length = int(prefix_length)
                subnet_mask = '.'.join(['255'] * (prefix_length // 8) + [str(256 - (2 ** (8 - prefix_length % 8)))])
                subnet = ip_address.split('.')
                subnet[-1] = str(int(subnet[-1]) + 2)  # Increment the last octet by 2 to get the third address in the subnet
                interface_ip = '.'.join(subnet)

            #  print(f"Interface IP Address for Row {row}: {interface_ip} /{prefix_length} (Subnet Mask: {subnet_mask})")  
                network_type = "4G"

                config_script += f"""

                interface {interface}.{vlan}
                vlan-type dot1q {vlan}
                description {network_type}_{site_name}
                ip binding vpn-instance vpn_name({network_type})
                ip address {interface_ip} {subnet_mask}
                #
                """

        # Print the generated configuration script
        print(config_script)

        # Create a new file to store the configuration
        output_file = 'router_configuration.txt'

        # Open the file in write mode and write the configuration
        with open(output_file, 'w') as file:
            # Write the entire config_script to the file    
            file.write(config_script)

        # Configuration saved to 'router_configuration.txt' file
        print("Configuration saved to 'router_configuration.txt' file.")

        # Retourne le script de configuration généré sous forme de chaîne
        return config_script



    elif config_type == '4g_tdd_trans':
            # Generate configuration for 4G TDD Config (Trans dédié)

        sheet_IP_PLAN = workbook.sheet_by_name("IP PLAN")

        # Generate router configuration script dynamically
        header_row = [header.lower().replace(' ', '') for header in sheet_IP_PLAN.row_values(0)]

        router_name_col = header_row.index('router')
        site_name_col = header_row.index('radio_site_name')

        interface_col_x = header_row.index('interface')
        vlan_col_x_Management = header_row.index('vlanmanagement')
        ip_address_col_x_Management = header_row.index('management')
        vlan_col_x_4G = header_row.index('vlan4g')
        ip_address_col_x_4G = header_row.index('ip4g')

        vlan_cols = [vlan_col_x_Management, vlan_col_x_4G]
        ip_adresses_cols = [ip_address_col_x_Management, ip_address_col_x_4G]


        for row in range(2, sheet_IP_PLAN.nrows):
            router_name = sheet_IP_PLAN.cell_value(row, router_name_col)
            site_name = sheet_IP_PLAN.cell_value(row, site_name_col)
            
            interface = sheet_IP_PLAN.cell_value(row, interface_col_x)   
            config_script += f"""
            -------------
            Router_name: {router_name}
            -------------

            #
            interface {interface}
            description TO_{site_name}
            undo shutdown
            #
            """

            for vlan_col, ip_add_col in zip(vlan_cols, ip_adresses_cols):
                vlan = int(sheet_IP_PLAN.cell_value(row, vlan_col))
                ip_with_mask = sheet_IP_PLAN.cell_value(row, ip_add_col)
                ip_address, prefix_length = ip_with_mask.split('/')

                try:
                    ip_address_obj = ipaddress.IPv4Address(ip_address)
                except ipaddress.AddressValueError:
                    print(f"Invalid IP address in Row {row}: {ip_address}")
                    continue

                prefix_length = int(prefix_length)
                subnet_mask = '.'.join(['255'] * (prefix_length // 8) + [str(256 - (2 ** (8 - prefix_length % 8)))])
                subnet = ip_address.split('.')
                #subnet[-1] = str(int(subnet[-1]) + 2)  # Increment the last octet by 2 to get the third address in the subnet
                interface_ip = '.'.join(subnet)

            #  print(f"Interface IP Address for Row {row}: {interface_ip} /{prefix_length} (Subnet Mask: {subnet_mask})")  
                
                if vlan in [13, 23, 33, 43, 53, 63, 73, 83]:
                    network_type = "4G"
                elif vlan in [12, 22, 32, 42, 52, 62, 72, 82]:
                    network_type = "Management"
                else:
                    network_type = "Unknown"

                config_script += f"""

                interface {interface}.{vlan}
                vlan-type dot1q {vlan}
                description {network_type}_{site_name}
                ip binding vpn-instance vpn_name({network_type})
                ip address {interface_ip} {subnet_mask}
                #
                """

        # Print the generated configuration script
        print(config_script)



        # Create a new file to store the configuration
        output_file = 'router_configuration.txt'

        # Open the file in write mode and write the configuration
        with open(output_file, 'w') as file:
            # Write the entire config_script to the file    
            file.write(config_script)

        # Configuration saved to 'router_configuration.txt' file
        print("Configuration saved to 'router_configuration.txt' file.")

        # Retourne le script de configuration généré sous forme de chaîne
        return config_script    

    elif config_type == '4g_tdd_co_trans':
        gw_address_4g = request.form.get('GW_address_4g')
        gw_address_management = request.form.get('GW_address_management')

        destination_sheet = workbook.sheet_by_index(0)  # Utilisez la première feuille (index 0)
        header_row = [header.lower().replace(' ', '') for header in destination_sheet.row_values(0)]

        router_name = []
        site_name = []
        destination_addresses_management = []
        destination_addresses_service_tdd = []

        # Parcourez les lignes de la feuille et extrayez les valeurs
        for row_index in range(2, destination_sheet.nrows):
            row_values = destination_sheet.row_values(row_index)
            router_name = row_values[0]  # Colonne "Router name"
            site_name = row_values[1]    # Colonne "site_name"
            destination_addresses_management = row_values[2]  # Colonne "management"
            destination_addresses_service_tdd = row_values[3]


            try:
                ip_address_obj = ipaddress.IPv4Address(destination_addresses_management)
            except ipaddress.AddressValueError:
                print(f"Invalid IP address: {destination_addresses_management}")
                continue
            try:
                ip_address_obj = ipaddress.IPv4Address(destination_addresses_service_tdd)
            except ipaddress.AddressValueError:
                print(f"Invalid IP address: {destination_addresses_management}")
                continue

        config_script += f"""
                ip route-static vpn-instance vpn_name(Management) {destination_addresses_management} 30 {gw_address_management} description {site_name}
                ip route-static vpn-instance vpn_name(4g_service_tdd) {destination_addresses_service_tdd} 30 {gw_address_4g} description {site_name}       
        """
        # Print the generated configuration script
        print(config_script)

        # Create a new file to store the configuration
        output_file = 'router_configuration.txt'

        # Open the file in write mode and write the configuration
        with open(output_file, 'w') as file:
            # Write the entire config_script to the file    
            file.write(config_script)

        # Configuration saved to 'router_configuration.txt' file
        print("Configuration saved to 'router_configuration.txt' file.")

        # Retourne le script de configuration généré sous forme de chaîne
        return config_script 










            # Generate configuration for 4G TDD Config (Co-trans)     

    #else:
            # Handle invalid configuration type
        #print("No selected configuration type")
    





