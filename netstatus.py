import nmap
import struct
import socket

class netstatus():

    MEDIA_CENTER_MAC = "1c:6f:65:c9:bd:0a"

    def get_connected_devices(self):
        nm = nmap.PortScanner()
        nm.scan(hosts='192.168.1.0/24', arguments='-sn')
        for x in nm.all_hosts():
            yield (x, nm[x]['hostname'])

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


if __name__ == "__main__":

    netstatus().wake_on_lan(netstatus.MEDIA_CENTER_MAC)
    for add, name in netstatus().get_connected_devices():
        print add, name
