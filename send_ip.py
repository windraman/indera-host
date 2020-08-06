import socket
import fcntl
import struct
import requests
import json
import os
import db_handler
app_path = os.path.dirname(os.path.realpath(__file__)) + "/"
url = "http://wahyu.top/public/api/update_modul"

def getHandler(url):
    res = []
    try:
        res = requests.get(url,timeout=7.0)
    except requests.ConnectionError as e:
        wlogs(app_path+"logs/send_ip.log","OOPS!! Connection Error. Make sure you are connected to Internet. Technical Details given below.")
        print(str(e))
    except requests.Timeout as e:
        wlogs(app_path+"logs/send_ip.log","OOPS!! Timeout Error")
        print(str(e))
    except requests.RequestException as e:
        wlogs(app_path+"logs/send_ip.log","OOPS!! General Error")
        print(str(e))
        
    return res

jresp = db_handler.readme(True)
jmodul = jresp['modul']
modulslug = jmodul['slug']

def get_ip_address(ifname):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', bytes(ifname[:15], 'utf-8'))
        )[20:24])
    except OSError:
        return 0
        

local_ip = get_ip_address('wlan0')
if local_ip == 0:
    local_ip = get_ip_address('eth0')
    print('not connected')
    if local_ip == 0:
        print('not connected')
    else:
        respip = getHandler(url + "?slug=" + modulslug + "&local_ip=" + local_ip)
        print(respip.content)
else:
    respip = getHandler(url + "?slug=" + modulslug + "&local_ip=" + local_ip)
    print(respip.content)