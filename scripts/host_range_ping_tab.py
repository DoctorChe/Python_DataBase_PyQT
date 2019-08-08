import chardet
import ipaddress
import re
import subprocess
from tabulate import tabulate


def host_range_ping_tab(ip_start, ip_end):
    ip_start, ip_end = list(map(lambda x: str(ipaddress.ip_address(x)), [ip_start, ip_end]))
    start_base = re.match(r'\d+.\d+.\d+.', ip_start)[0]
    end_base = re.match(r'\d+.\d+.\d+.', ip_end)[0]
    if start_base == end_base:
        start_range = int(re.search(r'\d+$', ip_start)[0])
        end_range = int(re.search(r'\d+$', ip_end)[0])
        ip_range = (f'{start_base}{x}' for x in range(start_range, end_range + 1))
        reachable = []
        unreachable = []
        for ip in ip_range:
            ip = str(ipaddress.ip_address(ip))
            with subprocess.Popen(['ping', ip], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE) as process:
                out = process.stdout.read()
                codepage = chardet.detect(out)
                out = out.decode(codepage['encoding']).encode('utf-8')
                result = re.search(r'(\d+)(% потерь)|(\d+)(% packet loss)', out.decode('utf-8'))
                if result[0].startswith('100'):
                    unreachable.append(ip)
                else:
                    reachable.append(ip)
        print(tabulate({"Reachable": reachable, "Unreachable": unreachable}, headers="keys", tablefmt="grid"))


if __name__ == '__main__':
    ip_start = "10.0.1.0"
    ip_end = "10.0.1.4"
    host_range_ping_tab(ip_start, ip_end)
