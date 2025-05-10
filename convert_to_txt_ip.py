import ipaddress
with open("DEFAULT") as f_in, open("DEFAULT_CIDR", "w") as f_out:
    for line in f_in:
        if "route" in line:
            parts = line.split()
            ip = parts[2]
            mask = parts[3].strip('"')
            net = ipaddress.IPv4Network(f"{ip}/{mask}", strict=False)
            f_out.write(f"{net}\n")
