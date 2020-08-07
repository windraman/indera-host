from crontab import CronTab
import os
import sys
app_path = os.path.dirname(os.path.realpath(__file__)) + "/"

with CronTab(user=sys.argv[1]) as cron:
    job = cron.new(command='python3 '+app_path+'moderator.py')
    job.every_reboot()
    job = cron.new(command='python3 '+app_path+'send_ip.py')
    job.every_reboot()
    job = cron.new(command='python3 '+app_path+'moderator.py')
    job.minute.every(1)
    job = cron.new(command='python3 '+app_path+'send_ip.py')
    job.minute.every(3)
    job = cron.new(command='python3 '+app_path+'report_terjadwal.py')
    job.every(20).hours()
    for job in cron:
        print(job)
