import nmap
import struct
import socket
import tornado.httpclient
from scapy.all import *
import time

class netstatus():

    MEDIA_CENTER_MAC = "1c:6f:65:c9:bd:0a"
    MEDIA_CENTER_IP = "192.168.1.50"
    SHUTDOWN_PORT = 8886
    SHUTDOWN_USER = "romain"
    SHUTDOWN_PASSWORD = "aqw"
    SHUTDOWN_MSG = "shutdown"

    def find_listening_devices(self, port):
        nm = nmap.PortScanner()
        nm.scan(hosts='192.168.1.0/24', arguments="-p" + str(port) +"  --open")
        for x in nm.all_hosts():
            yield x

    def get_connected_devices(self):
        nm = nmap.PortScanner()
        nm.scan(hosts='192.168.1.0/24', arguments='-sn')
        for x in nm.all_hosts():
            yield (x, nm[x]['hostname'])

    def get_hdw_and_ip(self):
        alive,dead=srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst="192.168.0.0/24"), timeout=2, verbose=0)
        for i in range(0,len(alive)):
            yield (alive[i][1].hwsrc, alive[i][1].psrc)

    def is_hdw_on_network(self, adr):
        for hdw_adr, ip in self.get_hdw_and_ip():
            if hdw_adr == adr:
                return True, ip
        return False, None

    def ping_addr(self, ip):
        import os
        response = os.system("ping -c 1 -w2 " + ip + " > /dev/null 2>&1")
        return response == 0

    def wake_on_lan(self, macaddress):
        """ Switches on remote computers using WOL. """
        # Check macaddress format and try to compensate.                                                                                                                                                           
        if len(macaddress) == 12:
            pass
        elif len(macaddress) == 12 + 5:
            sep = macaddress[2]
            macaddress = macaddress.replace(sep, '')
        else:
            raise ValueError('Incorrect MAC address format')
        # Pad the synchronization stream.                                                                                                                                                                          
        data = ''.join(['FFFFFFFFFFFF', macaddress * 20])
        send_data = ''
        # Split up the hex values and pack.                                                                                                                                                                        
        for i in range(0, len(data), 2):
            send_data = ''.join([send_data,
                                 struct.pack('B', int(data[i: i + 2], 16))])
        # Broadcast it to the LAN.                                                                                                                                                                                 
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(send_data, ('<broadcast>', 7))

    def shutdown(self, ip):
        http_client = tornado.httpclient.HTTPClient()
        try:
            response = http_client.fetch("http://" + ip + ":" + str(netstatus.SHUTDOWN_PORT) + "/?user=" + netstatus.SHUTDOWN_USER + "&password=" + netstatus.SHUTDOWN_PASSWORD + "&action=" + netstatus.SHUTDOWN_MSG)
            http_client.close()
            return "Done"
        except tornado.httpclient.HTTPError as e:
            # HTTPError is raised for non-200 responses; the response
            # can be found in e.response.
            http_client.close()
            return "Error: OB" + str(e)
        except Exception as e:
            # Other errors are possible, such as IOError.
            http_client.close()
            print("Error: " + str(e))



if __name__ == "__main__":
    #netstatus().find_listening_devices(8886)
    #nm = nmap.PortScanner()
    #nm.scan(hosts='192.168.1.0/24', arguments='-sn')
    #for x in nm.all_hosts():
    #    print(nm[x])
    nm = netstatus()
    while True:
        print(nm.is_hdw_on_network("78:02:f8:35:78:d9"))
        time.sleep(2)
