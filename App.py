import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import re

# Annahme: Diese Module existieren im selben Verzeichnis oder im Python-Pfad
# from style import init_style
# from lib.functions import center_window


# --- Platzhalter für die externen Funktionen, damit das Skript lauffähig ist ---
def init_style():
    pass


def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)
    window.geometry(f"{width}x{height}+{int(x)}+{int(y)}")


# --- Ende der Platzhalter ---


# FINAL: SKU-Liste exakt an die erlaubten Größen aus dem Screenshot angepasst.
SKU_MAP = {
    "francecentral": ["Standard_B1s", "Standard_B2ms", "Standard_D2s_v3"],
    "canadacentral": ["Standard_B1s", "Standard_B2ms", "Standard_D2s_v3"],
    "northeurope": ["Standard_B1s", "Standard_B2ms", "Standard_D2s_v3"],
}


class App(tk.Tk):
    def __init__(self, master=None):
        super().__init__(master)

        self.width = 700
        self.height = 920
        self.withdraw()

        self.title("Azure VM Script Generator")
        # self.iconbitmap(r"./favicon.ico")

        init_style()
        self.vars = {}
        self.vars["use_existing_rg"] = tk.BooleanVar(value=False)
        self._create_widgets()

    def _create_widgets(self):
        self.input_frame = ttk.Frame(self, padding="10")
        self.input_frame.pack(fill="x", expand=False)

        rg_check = ttk.Checkbutton(
            self.input_frame,
            text="Vorhandene Ressourcengruppe nutzen?",
            variable=self.vars["use_existing_rg"],
        )
        rg_check.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=(5, 10))

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

        for i, (row, label_text, var_name, widget_type, options) in enumerate(
            widgets_to_create
        ):
            label = ttk.Label(self.input_frame, text=label_text)
            label.grid(row=row, column=0, sticky="w", padx=5, pady=5)

            if widget_type in ["entry", "combobox"]:
                self.vars[var_name] = tk.StringVar()

            if widget_type == "entry":
                widget = ttk.Entry(
                    self.input_frame,
                    textvariable=self.vars[var_name],
                    width=40,
                    **options,
                )
            elif widget_type == "combobox":
                widget = ttk.Combobox(
                    self.input_frame,
                    textvariable=self.vars[var_name],
                    state="readonly",
                    width=38,
                    **options,
                )
                if var_name == "location":
                    self.region_combobox = widget
                elif var_name == "vm_sku":
                    self.sku_combobox = widget

            widget.grid(row=row, column=1, sticky="ew", padx=5, pady=5)

        pw_hint = ttk.Label(
            self.input_frame,
            text="Info: Das Passwort muss komplex sein...",
            foreground="grey",
        )
        pw_hint.grid(row=7, column=0, columnspan=2, sticky="w", padx=5)

        ttk.Separator(self.input_frame, orient="horizontal").grid(
            row=15, columnspan=2, sticky="ew", pady=15
        )

        self.region_combobox.bind("<<ComboboxSelected>>", self._update_skus)

        generate_button = ttk.Button(
            self, text="PowerShell-Skript generieren", command=self._generate_script
        )
        generate_button.pack(pady=10)

        output_frame = ttk.Frame(self, padding="10")
        output_frame.pack(fill="both", expand=True)
        self.output_text = tk.Text(
            output_frame, wrap="word", height=20, width=80, state="disabled"
        )
        scrollbar = ttk.Scrollbar(output_frame, command=self.output_text.yview)
        self.output_text.config(yscrollcommand=scrollbar.set)
        self.output_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _update_skus(self, event=None):
        selected_region = self.vars["location"].get()
        sku_list = SKU_MAP.get(selected_region, [])
        self.sku_combobox["values"] = sku_list
        self.vars["vm_sku"].set("")

    def _validate_inputs(self):
        for var_name, var_obj in self.vars.items():
            if isinstance(var_obj, tk.BooleanVar):
                continue
            if not var_obj.get():
                messagebox.showerror(
                    "Fehler", f"Das Feld für '{var_name}' darf nicht leer sein."
                )
                return False

        cidr_pattern = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}$")
        if not cidr_pattern.match(self.vars["address_prefix"].get()):
            messagebox.showerror(
                "Fehler",
                "Der VNet-Adress-Präfix ist keine gültige CIDR-Notation (z.B. 10.0.0.0/16).",
            )
            return False
        if not cidr_pattern.match(self.vars["subnet_prefix"].get()):
            messagebox.showerror(
                "Fehler",
                "Der Subnetz-Präfix ist keine gültige CIDR-Notation (z.B. 10.0.1.0/24).",
            )
            return False
        return True

    def _generate_script(self):
        if not self._validate_inputs():
            return

        params = {key: value.get() for key, value in self.vars.items()}

        rg_creation_script = f"New-AzResourceGroup -Name $rgName -Location $location"
        if params["use_existing_rg"]:
            rg_creation_script = f"# Ressourcengruppe wird nicht erstellt, da sie bereits existieren sollte."

        script_template = f"""
# PowerShell-Skript zur Erstellung einer Azure VM
# Dieses Skript in der Azure Cloud Shell ausführen.

# --- Variablen ---
$rgName = "{params['rg_name']}"
$location = "{params['location']}"
$vmName = "{params['vm_name']}"
$vmSize = "{params['vm_sku']}"
$adminUsername = "{params['admin_user']}"
$adminPassword = "{params['admin_pass']}"

$vnetName = "{params['vnet_name']}"
$subnetName = "{params['subnet_name']}"
$addressPrefix = "{params['address_prefix']}"
$subnetPrefix = "{params['subnet_prefix']}"

$publicIpName = "{params['public_ip_name']}"
$nsgName = "{params['nsg_name']}"
$nicName = "{params['nic_name']}"

$image = "MicrosoftWindowsServer:WindowsServer:2025-datacenter-azure-edition:latest"

# --- Skript-Ausführung ---
Write-Host "Erstelle oder überprüfe Ressourcengruppe..."
{rg_creation_script}

Write-Host "Erstelle Virtuelles Netzwerk (VNet) und Subnetz..."
$subnetConfig = New-AzVirtualNetworkSubnetConfig -Name $subnetName -AddressPrefix $subnetPrefix
$vnet = New-AzVirtualNetwork -Name $vnetName -ResourceGroupName $rgName -Location $location -AddressPrefix $addressPrefix -Subnet $subnetConfig

Write-Host "Erstelle Öffentliche IP-Adresse..."
$publicIp = New-AzPublicIpAddress -Name $publicIpName -ResourceGroupName $rgName -Location $location -AllocationMethod Static -Sku Standard

Write-Host "Erstelle Netzwerksicherheitsgruppe (NSG) und RDP-Regel..."
$nsgRule = New-AzNetworkSecurityRuleConfig -Name "RDP-Allow" -Protocol Tcp -Direction Inbound -Priority 1000 -SourceAddressPrefix "*" -SourcePortRange "*" -DestinationAddressPrefix "*" -DestinationPortRange 3389 -Access Allow
$nsg = New-AzNetworkSecurityGroup -Name $nsgName -ResourceGroupName $rgName -Location $location -SecurityRules $nsgRule

Write-Host "Erstelle Netzwerkkarte (NIC)..."
$nic = New-AzNetworkInterface -Name $nicName -ResourceGroupName $rgName -Location $location -SubnetId $vnet.Subnets[0].Id -PublicIpAddressId $publicIp.Id -NetworkSecurityGroupId $nsg.Id

Write-Host "Erstelle die Virtuelle Maschine (dies kann einige Minuten dauern)..."
$securePassword = ConvertTo-SecureString -String $adminPassword -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential($adminUsername, $securePassword)

# 1. Erstelle eine VM-Grundkonfiguration
$vmConfig = New-AzVMConfig -VMName $vmName -VMSize $vmSize

# 2. Füge Betriebssystem-Einstellungen hinzu
$vmConfig = Set-AzVMOperatingSystem -VM $vmConfig -Windows -ComputerName $vmName -Credential $credential
$vmConfig = Set-AzVMSourceImage -VM $vmConfig -PublisherName 'MicrosoftWindowsServer' -Offer 'WindowsServer' -Skus '2025-datacenter-azure-edition' -Version 'latest'

# 3. Füge die Netzwerkkarte explizit hinzu
$vmConfig = Add-AzVMNetworkInterface -VM $vmConfig -Id $nic.Id

# 4. Erstelle die VM aus der fertigen Konfiguration
New-AzVM -ResourceGroupName $rgName -Location $location -VM $vmConfig

Write-Host "VM-Erstellung abgeschlossen!"
"""

        self.output_text.config(state="normal")
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, script_template.strip())
        self.output_text.config(state="disabled")

    def run(self):
        center_window(self, self.width, self.height)
        self.deiconify()
        self.mainloop()
