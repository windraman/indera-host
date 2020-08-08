import os
from time import sleep

app_path = os.path.dirname(os.path.realpath(__file__)) + "/"
os.system('nohup python3 ' + app_path + 'server.py & ')

sleep(5)

exit(0)
