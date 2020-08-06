import sys
import subprocess
import pkg_resources

required = {'unidecode', 'requests', 'python-crontab'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

if missing:
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)
else:
    print('semua module tambahan terinstall')