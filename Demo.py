import schedule
import sys
import os
import time
import psutil

def CreateLog(FolderName):
    Border = "-"*60
    Ret = False

    Ret = os.path.exists(FolderName)
    
    if(Ret == True):
        Ret = os.path.isdir(FolderName)
        if(Ret == False):
            print("Unable to create folder")
            return
        
    else:
        os.mkdir(FolderName)
        print("Directory for log file get succesfully created")

    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    Filename = os.path.join(FolderName, "Surveillance%s.log" %timestamp)
    print("Log file gets created with name : ",Filename)

    fobj = open(Filename, "w")

    fobj.write(Border+"\n")
    fobj.write("---------- Automated Platform Surveillance System ----------\n")
    fobj.write(Border+"\n")
    fobj.write("Log file created at : "+time.ctime()+"\n")
    fobj.write(Border+"\n")
    fobj.write("--------------------- System Report ------------------------\n")
    fobj.write("CPU usage : %s %%\n" %psutil.cpu_percent())
    fobj.write(Border+"\n")

    # RAM info
    mem = psutil.virtual_memory()
    fobj.write("RAM usage : %s %%\n" %mem.percent)
    fobj.write(Border+"\n")

    # Disk report
    fobj.write("Disk Usage Report : \n")
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            fobj.write("%s  ->  %s %% used\n" %(part.mountpoint, usage.percent))
        except:
            pass
    fobj.write(Border+"\n")

    # Network info
    net = psutil.net_io_counters()
    fobj.write("Network Usage Report : \n")
    fobj.write("Sent : %.2f MB\n" %(net.bytes_sent / (1024 * 1024)))
    fobj.write("Recv : %.2f MB\n" %(net.bytes_recv / (1024 * 1024)))
    fobj.write(Border+"\n")
    # Process Report
    Data = ProcessScan()

    for info in Data:
        fobj.write("PID : %s\n" %info.get("pid"))
        fobj.write("Process Name : %s\n" %info.get("name"))
        fobj.write("Process UserName : %s\n" %info.get("username"))
        fobj.write("Status : %s\n" %info.get("status"))
        fobj.write("Start time : %s\n" %info.get("create_time"))
        fobj.write("CPU %% : %.2f\n" %info.get("cpu_percent"))
        fobj.write("Memory %% : %.2f\n" %info.get("memory_percent"))

        mem = info.get("rss_memory")
        fobj.write(f"Memory (RSS) : {mem / (1024 ** 2):.2f} MB\n")

        mem = info.get("vms_memory")
        fobj.write(f"Memory (VMS) : {mem / (1024 ** 2):.2f} MB\n")
        
        fobj.write("Thread count : %s\n" %info.get("num_threads"))

        count = len(info.get("open_files"))
        fobj.write("Open files Count : "+str(count)+"\n")
        fobj.write(Border+"\n")
    
    fobj.write("---------------------- End of Log File ---------------------\n")
    fobj.write(Border+"\n")

    fobj.close()


def ProcessScan():
    listprocess = []

    # Warm up for actual cpu percent
    for proc in psutil.process_iter():
        try:
            proc.cpu_percent()
        except:
            pass
        
    time.sleep(0.2)

    for proc in psutil.process_iter():
        try:
            info = proc.as_dict(attrs=["pid", "name", "username", "status", "create_time", "num_threads", "memory_info"])

            try:
                info["create_time"] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(info["create_time"]))
            except:
                info["create_time"] = "NA"

            info["cpu_percent"] = proc.cpu_percent(None)
            info["memory_percent"] = proc.memory_percent()
            info["open_files"] = proc.open_files()
            mem = info["memory_info"].rss 
            info["rss_memory"] = mem

            mem = info["memory_info"].vms 
            info["vms_memory"] = mem

            listprocess.append(info)
        
        except(psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

        
    return listprocess

def main():
    Border = "-"*55

    print(Border)
    print("------ Automated Platform Surveillance System --------")
    print(Border)

    if(len(sys.argv) == 2):

        if(sys.argv[1] == "--h" or sys.argv[1] == "--H"):
            print("This script is used to : ")
            print("1 : Create automatic logs")
            print("2 : Executes periodically")
            print("3 : Sends mail with the log")
            print("4 : Store information about processess")
            print("5 : Store information about CPU")
            print("6 : Store information about RAM usage")
            print("7 : Store the information about secondary storage")

        elif(sys.argv[1] == "--u" or sys.argv[1] == "--U"):
            print("Use the automation script as")
            print("ScriptName.py TimeInterval DirectoryName ")
            print("TimeInterval : Time in minutes for periodic scheduling")
            print("DirectoryName : Name of directory to create auto logs")

        else:
            print("Unable to proceed  as there is no such option")
            print("Please use --h or --u to get more details")


    # python demo.py 5 Marvellous
    elif(len(sys.argv) == 3):
        print("Inside project logic")
        print("Time interval : ",sys.argv[1])
        print("Directory Name : ",sys.argv[2])

        # apply the schedular
        schedule.every(int(sys.argv[1])).minutes.do(CreateLog, sys.argv[2])

        print("Platform Surveillance System started successfully")
        print("Directory created with name : ",sys.argv[2])
        print("Time interval in minutes: ",sys.argv[1])
        print("Press CTRL + C to stop the execution")

        # wait till abort
        while(True):
            schedule.run_pending()
            time.sleep(1)

    else:
        print("Invalid number of command line arguments")
        print("Unable to proceed  as there is no such option")
        print("Please use --h or --u to get more details")


    print(Border)
    print("----------- Thank you for using our script ------------")
    print(Border)

if __name__ == "__main__":
    main()