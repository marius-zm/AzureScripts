Für die Locations werden nur drei von den für uns auswählbaren Locations 
in einem Dictionary als Key gespeichert. Als Value wird eine Liste mitgegeben,
die nur die uns zugänglichen SKUs beinhaltet.

Per Schleife werden die Widgets über folgende Liste erstellt:

widgets_to_create = [
            (1, "Ressourcengruppe:", "rg_name", "entry", {}),
            (2, "VM-Name:", "vm_name", "entry", {}),
            (3, "Region:", "location", "combobox", {"values": list(SKU_MAP.keys())}),
            (4, "VM-Größe (SKU):", "vm_sku", "combobox", {"values": []}),
            (5, "Admin-Benutzer:", "admin_user", "entry", {}),
            (6, "Admin-Passwort:", "admin_pass", "entry", {"show": "*"}),
            (8, "VNet-Name:", "vnet_name", "entry", {}),
            (9, "VNet-Adress-Präfix (CIDR):", "address_prefix", "entry", {}),
            (10, "Subnetz-Präfix (CIDR):", "subnet_prefix", "entry", {}),
            (11, "Subnetz-Name:", "subnet_name", "entry", {}),
            (12, "Öffentliche IP-Name:", "public_ip_name", "entry", {}),
            (13, "NSG-Name:", "nsg_name", "entry", {}),
            (14, "Netzwerkkarten-Name (NIC):", "nic_name", "entry", {}),
        ]

self.vars = {} speichert die vom Benutzer ausgewählten Werte für die jeweiligen
Inputs. Diese werden dann durchloopt und in dem Template-Skript dynamisch hinzugefügt.

