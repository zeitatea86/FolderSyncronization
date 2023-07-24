import os, shutil, time, datetime, subprocess, hashlib
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
print(" 3. Please enter the time interval of synchronization: ")
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


#### Check the hash function of folders(path of folders and subfolders with files)

def hash_directory(path):
    digest = hashlib.sha1()
    for root, dirs, files in os.walk(path):
        for names in files:
            file_path = os.path.join(root, names)
            digest.update(hashlib.sha1(file_path[len(path):].encode()).digest())
            if os.path.isfile(file_path):
                with open(file_path, 'rb') as f_obj:
                    while True:
                        buf = f_obj.read(1024 * 1024)
                        if not buf:
                            break
                        digest.update(buf)
    return digest.hexdigest()



#### Content of source, replica and difference after modification:

content_original=[]                
content_backup=[]
difference=[]

# hash output of both folders (source and replica):

h1=hash_directory(source)
h2=hash_directory(replica)

while True:
    if h1!=h2:
        files_source = os.listdir(source)
        files_replica = os.listdir(replica)
        for f in files_source:
            content_original.append(f)
        for f in files_replica:
            content_backup.append(f)
        difference = [value for value in content_original  if value not in content_backup]
        diff2=set(content_backup)-set(content_original)
        shutil.rmtree(replica, ignore_errors=False, onerror=None)
        shutil.copytree(source, replica,dirs_exist_ok=True, ignore = shutil.ignore_patterns('logger', 'a'))
        time_current= datetime.datetime.now()
        x1=du(source)                #### Size of original folder
        x2=du(replica)               #### Size of backup folder
        if x1>x2:
            message=f'Files and directories {difference} added from '+ source +' and updated to ' + replica+ f' at {time_current}'
        else:
            message=f'Files and directories {diff2} deleted from '+ source +' and updated to ' + replica+ f' at {time_current}'
        print(h1,h2)
        print(message)
        print(message, file=logger) 

    else:
        time_current= datetime.datetime.now()
        #print(time_current)
        message=f'Folders are syncrhonized at {time_current}'
        print(message)
        print(message, file=logger)
    h1=hash_directory(source)
    h2=hash_directory(replica)
    time.sleep(int(interval))