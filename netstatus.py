import nmap

class netstatus():

    def get_connected_devices(self):
        nm = nmap.PortScanner()
        nm.scan(hosts='192.168.1.0/24', arguments='-sn')
        for x in nm.all_hosts():
            yield (x, nm[x]['hostname'])

if __name__ == "__main__":
    for add, name in netstatus().get_connected_devices():
        print add, name
