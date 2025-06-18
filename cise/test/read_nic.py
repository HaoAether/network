import netifaces as nif

# print(nif.interfaces())

nic = nif.ifaddresses("ens18")

nic_mac = nic[nif.AF_LINK][0]['addr']
nic_ip =  nic[nif.AF_INET][0]['addr']

print(nic_mac, nic_ip)