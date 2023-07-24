
import os, shutil, datetime, subprocess, time
from sys import platform


print("""      " 1. Please enter the folder (path) for which you want to create a backup synch folder: "
      " 2. Please enter the folder (path) where the backup folder should be saved: "
      " 3. Please enter the time interval of synchronization: "
      " 4. Please enter the log file (path) where the logs will be saved: "
      " 5. Press ctrl+c for exiting the program. """)

print(" 1. Please enter the folder (path) for which you want to create a backup synch folder: ")
source_input=input()
print(" 2. Please enter the folder (path) where the backup folder should be saved: ")
replica_input=input()
print(" 3. Please enter the time (in seconds) interval of synchronization: ")
interval_input=input()
print(" 4. Please enter the log file (path) where the logs will be saved: ")
loggerfile=input()


logger = open(loggerfile, 'a')
source = source_input
replica= replica_input
interval= int(interval_input)

files_source = os.listdir(source)
files_replica = os.listdir(replica)


#### Check the size of folders based on OS system

def du(path):
    if platform == "linux" or platform == "linux2":
        #Linux
        return subprocess.check_output(['du','-sh', path]).split()[0].decode('utf-8')
    elif platform == "darwin":
        # OS X
        pass
    elif platform == "win32":
        # Windows
        command='"{0:N3} KB" -f ((gci –force ' + path + ' –Recurse -ErrorAction SilentlyContinue| measure Length -s).sum / 1Kb)'
        p = subprocess.Popen(["powershell.exe", command], stdout=subprocess.PIPE)
        output = p.stdout.read()
        return int(output.split()[0].decode('utf-8').replace(".","").replace(",",""))


x1=du(source)                #### Size of original folder
x2=du(replica)               #### Size of backup folder


#### Content of source, replica and difference after modification

content_original=[]                
content_backup=[]
difference=[]

#### Loop for checking the modifications inside folders, within time interval provided in seconds:

while True:

    #### Case 1 : file addition in original folder:

    if x1>x2:
        files_source = os.listdir(source)
        files_replica = os.listdir(replica)
        for f in files_source:
            content_original.append(f)
        for f in files_replica:
            content_backup.append(f)
        difference = [value for value in content_original if value not in content_backup]

        shutil.rmtree(replica, ignore_errors=False, onerror=None)
        shutil.copytree(source, replica,dirs_exist_ok=True, ignore = shutil.ignore_patterns('logger', 'a'))
        time_current= datetime.datetime.now()
        message=f'Files and directories {difference} added from '+ source +' and updated to ' + replica+ f' at {time_current}'
        print(message)
        print(message, file=logger) 

    #### Case 2 : file deletion in original folder

    elif x1<x2:
        files_source = os.listdir(source)
        files_replica = os.listdir(replica)
        for f in files_source:
            content_original.append(f)
        for f in files_replica:
            content_backup.append(f)
        diff2=set(content_backup)-set(content_original)
        difference = [value for value in content_original if value not in content_backup]
        shutil.rmtree(replica, ignore_errors=False, onerror=None)
        shutil.copytree(source, replica,dirs_exist_ok=True, ignore = shutil.ignore_patterns('logger', 'a'))
        time_current= datetime.datetime.now()
        message=f'Files and directories {diff2} deleted from '+ source +' and updated to ' + replica+ f' at {time_current}'
        print(message)
        print(message, file=logger)
        content_original=[]                
        content_backup=[]
        difference=[]

    #### Case 3: no modification performed

    else:
        time_current= datetime.datetime.now()
        message=f'Folders are syncrhonized at {time_current}'
        print(message)
        print(message, file=logger) 
    time.sleep(interval)
    x1=du(source)                
    x2=du(replica) 
logger.close()