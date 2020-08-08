from crontab import CronTab
import os
import sys
app_path = os.path.dirname(os.path.realpath(__file__)) + "/"

def notExist(cron,line):
    if any(line in str(job) for job in cron):
        print("job exist")
        return False
    else:
        return True

#with CronTab(user=sys.argv[1]) as cron:
with CronTab(user="pi") as cron:
    if(notExist(cron,'@reboot python3 '+app_path+'moderator.py')):
        job = cron.new(command='python3 '+app_path+'moderator.py')
        job.every_reboot()  
        print("created")      
    
    if(notExist(cron,'@reboot python3 '+app_path+'send_ip.py')):
        job = cron.new(command='python3 '+app_path+'send_ip.py')
        job.every_reboot()  
        print("created")    
        
    if notExist(cron,'* * * * * python3 '+app_path+'moderator.py'):
        job = cron.new(command='python3 '+app_path+'moderator.py')
        job.minute.every(1)
        print('created')    
            
    if notExist(cron,'*/3 * * * * python3 '+app_path+'send_ip.py'):
        job = cron.new(command='python3 '+app_path+'send_ip.py')
        job.minute.every(3)
        print('created')
        
    if notExist(cron,'* 7 * * * python3 '+app_path+'report_terjadwal.py'):
        job = cron.new(command='python3 '+app_path+'report_terjadwal.py')
        job.hours.on(7)
        print('created')
        
    for job in cron:
        print(job)
