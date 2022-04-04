import re
import dns.resolver


fn_domains_to_unblock = 'domains_to_unblock.txt'

#------------------------------------------------------------
# get_netblocks()
#------------------------------------------------------------
def get_netblocks(spf_records):

  # 1. среди всех TXT-records оставить только с "spf1"
  # 2. если есть "redirect/include", то сделать дополнительный запрос
  # 3. все записи с "ip4:<netblock>" добавляем в список netblocks

  netblocks = []
  print ("Testing domain", domain, "for SPF record...")
  txt_records = dns.resolver.resolve(domain , 'TXT')
  for txt_record in txt_records:
    txt_record = str(txt_record)
    # print(f"= txt_record: {txt_record}")
    
    if 'spf1' in txt_record:

      # да, нашли SPF-запись, будем дальше работать именно с ней
      spf_records = re.findall('(?:include:|redirect=)(_[a-zA-Z0-9\.-]+)', txt_record)
      print(f"  - spf_records: {spf_records}")
      for spf_record in spf_records:

        # делаем запрос по значению SPF-записи
        # здесь могут быть как записи ip4, так и include/redirect
        result = dns.resolver.resolve(spf_record , 'TXT')
        for item in result:
          print(f"        - result item: {item}")

          # если include/redirect, то делаем дополнительные запросы
          include_list = re.findall('(?:include:|redirect=)(_[a-zA-Z0-9\.-]+)', str(item))
          print(f"          - include2_list: {include_list}")
          for include_item in include_list:
            print(f"            - include2_item: {include_item}")
            
            result2 = dns.resolver.resolve(include_item , 'TXT')
            for item2 in result2:
              result2_list = re.findall('ip4:([0-9\./]+)', str(item2))
              print(f"              - result2_list: {result2_list}")
              netblocks += result2_list
          
          # если ip4, то просто добавляем найденные значения в список netblocks
          ip4_list = re.findall('ip4:([0-9\./]+)', str(item))
          netblocks += ip4_list

  # print(f"* netblocks: {netblocks}")
  return netblocks

#==================================================================================
# main
#==================================================================================
domain = "google.com"
domain = "yandex.ru"


with open(fn_domains_to_unblock) as f:
    domains = f.read().splitlines()

print(f"* domains: {domains}")


exit()

netblocks = get_netblocks(domain)
print(f"* netblocks: {netblocks}")

