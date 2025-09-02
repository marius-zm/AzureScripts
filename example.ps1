# PowerShell-Skript zur Erstellung einer Azure VM
# Dieses Skript in der Azure Cloud Shell ausführen.

# --- Variablen ---
$rgName = "tn_marius_meyer"
$location = "francecentral"
$vmName = "testserver"
$vmSize = "Standard_D2s_v3"
$adminUsername = "adminuser"
$adminPassword = "passw0rd123!"

$vnetName = "francevnet"
$subnetName = "default"
$addressPrefix = "10.0.0.0/16"
$subnetPrefix = "10.0.0.0/24"

$publicIpName = "francePIP"
$nsgName = "franceNSG"
$nicName = "serverNIC"

$image = "MicrosoftWindowsServer:WindowsServer:2025-datacenter-azure-edition:latest"

# --- Skript-Ausführung ---
Write-Host "Erstelle oder überprüfe Ressourcengruppe..."
# Ressourcengruppe wird nicht erstellt, da sie bereits existieren sollte.

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
