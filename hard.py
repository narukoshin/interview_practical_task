import subprocess
import re

# Getting all IP addresses from the log files
# Sort command is mandatory for the uniq command to work
# Without sort, it will read all the results.
GetAllIps   = subprocess.check_output("awk '{print $1}' *.log | sort | uniq", shell=True)

# Converting it to the array
ip_list_raw = GetAllIps.decode('utf-8').split()

# Creating a new list
m = {}

for ip in ip_list_raw:
    # Checking the location
    DoLookUp = subprocess.check_output(["geoiplookup", ip]).decode('utf-8')

    # Checking if the location is Latvia
    if "Latvia" in DoLookUp:
        # Getting additional information about the IP address
        try:
            Email = subprocess.check_output("whois "+ip+" | grep abuse-mailbox | grep -oE '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,6}'", shell=True).decode('utf-8')
        except subprocess.CalledProcessError:
            Email = subprocess.check_output("whois "+ip+" | grep -oE '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,6}'", shell=True).decode('utf-8')
        # Removing new lines
        Email = Email.replace("\n", "")
        # Getting domain/provider name
        DomainName = re.search(r"(\@(.*)\.[a-zA-Z]{2,})", Email).group(2)
        # Adding to the list if there's already provider created
        if DomainName in m:
            # Adding IP addresses to the existing provider.
            g = m[DomainName]["IPs"]
            g.append(ip)
        else:
            # Creating a new provider in the list
            m[DomainName] = {"Abuse": Email, "IPs": [ip]}
        

# Printing all the info
for providerName in m:
    # Printing info about providers
    print(providerName.upper(), m[providerName]["Abuse"])
    print("\n".join(m[providerName]["IPs"]))
    print("\n")