import chardet
import ipaddress
import re
import socket
import subprocess


def hostname_to_ip(name):
    try:
        host = socket.gethostbyname(name)
    except socket.gaierror as err:
        print(f'Cannot resolve hostname: {name} {err}')
        return None
    else:
        return host


def host_ping(host_list):
    for host in host_list:
        ip = hostname_to_ip(host)
        ip = str(ipaddress.ip_address(ip))
        with subprocess.Popen(
                ['ping', ip], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ) as process:
            out = process.stdout.read()
            codepage = chardet.detect(out)
            out = out.decode(codepage['encoding']).encode('utf-8')
            result = re.search(r'(\d+)(% потерь)|(\d+)(% packet loss)', out.decode('utf-8'))
            if not result[0].startswith('100'):
                print(f'{host} - Узел доступен')
            else:
                print(f'{host} - Узел недоступен')


if __name__ == '__main__':
    host_list = ['yandex.com', '10.0.0.3']
    host_ping(host_list)
