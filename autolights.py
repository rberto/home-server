# Will check if tel just connected or disconnect
# will on this event  turn the lights on or off depending also
# on the time of day.
from netstatus import netstatus
from oweatherm import ToulouseWeather
from actions import actions
import time


def log(msg):
    print(time.strftime("%d/%m/%Y %H:%M:%S"), msg)

phone_addr = "78:02:f8:35:78:d9"

ns = netstatus()
wea = ToulouseWeather()
act = actions()

on_network, ip = ns.is_hdw_on_network(phone_addr)
log("phone IP" + str(ip))
log("status initialized: " + str(on_network))

while True:
    try:
        time.sleep(15)
        on_network_new, ip_new = ns.is_hdw_on_network(phone_addr)
        event = False
        if on_network_new == on_network:
            continue

        if not on_network_new:
            log("Detected phone disconnection")
            start_time = time.time()
            while time.time() < (start_time + 5*60) and not on_network_new:
                if ns.ping_addr(ip):
                    on_network_new = True
                    log("False detection of disconnect by ping")
                if not on_network_new:
                    time.sleep(15)
                    log("checking for arp again")
                    on_network_new, ip_new = ns.is_hdw_on_network(phone_addr)
                    log(on_network_new)

            if not on_network_new:
                log("Disconnection confirmed!")
                on_network = on_network_new
                event = True
            else:
                log("False detection of disconnection")

        else:
            log("Detected phone connection")
            on_network = on_network_new
            ip = ip_new
            event = True

        if event:
            is_day = wea.is_day()
            if on_network and not is_day:
                log("lights on")
                act.lights_on()
            elif not on_network:
                log("lights off")
                act.lights_off()

    except KeyboardInterrupt:
        quit()
    except:
        pass
