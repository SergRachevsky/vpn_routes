import os
import re
from datetime import datetime

import dns.resolver
from ipaddress import IPv4Network

fn_domains_to_unblock = '/opt/git/vpn_routes/domains_to_unblock.txt'
fn_DEFAULT = '/opt/git/vpn_routes/DEFAULT'
#fn_DEFAULT = '/etc/openvpn/routes/DEFAULT'

#------------------------------------------------------------
# get_a_records()
#------------------------------------------------------------
def get_a_records(domain):

  addresses = []
  a_records = dns.resolver.resolve(domain , 'A')
  for a_record in a_records:
    a_record = str(a_record)
    addresses.append(a_record)

  return addresses
#------------------------------------------------------------
# get_netblocks()
#------------------------------------------------------------
def get_netblocks(domain):

  # 1. среди всех TXT-records оставить только с "spf1"
  # 2. если есть "redirect/include", то сделать дополнительный запрос
  # 3. все записи с "ip4:<netblock>" добавляем в список netblocks

  netblocks = []
  # print ("Testing domain", domain, "for SPF record...")
  txt_records = dns.resolver.resolve(domain , 'TXT')
  for txt_record in txt_records:
    txt_record = str(txt_record)
    # print(f"= txt_record: {txt_record}")
    
    if 'spf1' in txt_record:

      # да, нашли SPF-запись, будем дальше работать именно с ней
      spf_records = re.findall('(?:include:|redirect=)(_[a-zA-Z0-9\.-]+)', txt_record)
      # print(f"  - spf_records: {spf_records}")
      for spf_record in spf_records:

        # делаем запрос по значению SPF-записи
        # здесь могут быть как записи ip4, так и include/redirect
        result = dns.resolver.resolve(spf_record , 'TXT')
        for item in result:
          # print(f"        - result item: {item}")

          # если include/redirect, то делаем дополнительные запросы
          include_list = re.findall('(?:include:|redirect=)(_[a-zA-Z0-9\.-]+)', str(item))
          # print(f"          - include2_list: {include_list}")
          for include_item in include_list:
            # print(f"            - include2_item: {include_item}")
            
            result2 = dns.resolver.resolve(include_item , 'TXT')
            for item2 in result2:
              result2_list = re.findall('ip4:([0-9\./]+)', str(item2))
              # print(f"              - result2_list: {result2_list}")
              netblocks += result2_list
          
          # если ip4, то просто добавляем найденные значения в список netblocks
          ip4_list = re.findall('ip4:([0-9\./]+)', str(item))
          netblocks += ip4_list

      # если ip4, то просто добавляем найденные значения в список netblocks
      ip4_list = re.findall('ip4:([0-9\./]+)', str(txt_record))
      netblocks += ip4_list


  # print(f"* netblocks: {netblocks}")
  # exit()
  return netblocks

#==================================================================================
# main
#==================================================================================

# domain = "  ssd"
# print(f"* domain: '{domain}'")

# if domain.strip():
#   print("1")
# else:
#   print("2")
# exit()




ts = datetime.now().strftime("%Y.%m.%d_%H-%M-%S")

with open(fn_domains_to_unblock) as f:
    domains = f.read().splitlines()


if len(domains) > 0:
  if os.path.isfile(fn_DEFAULT):
    os.rename(fn_DEFAULT, f"{fn_DEFAULT}.backup.{ts}")


with open(fn_DEFAULT, 'w') as f:
  for domain in domains:

    if domain.strip(): 
  
      print(f"* domain: '{domain}'")
      f.write(f"\n# {domain}\n")

      a_records = get_a_records(domain)
      print(f"  - a_records: {a_records}")
      for a_record in a_records:
        f.write(f"push \"route {IPv4Network(a_record).network_address} {IPv4Network(a_record).netmask}\"\n")

      netblocks = get_netblocks(domain)
      print(f"  - netblocks: {netblocks}")
      for netblock in netblocks:
        f.write(f"push \"route {IPv4Network(netblock).network_address} {IPv4Network(netblock).netmask}\"\n")


exit()

