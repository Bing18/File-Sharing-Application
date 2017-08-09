import socket,os,sys
import hashlib,subprocess
from datetime import datetime

port = 50000;
host="";

dir1=str(sys.argv[1]);
try:
    log=open("action_log.log","a+");
except:
    print "not able to open log file";
    exit(0);
def create_client():
    c=socket.socket(socket.AF_INET, socket.SOCK_STREAM);
    c.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        c.connect((host, port));
    except:
        print "No available server found on given address";
        c.close()
        exit(0)

    return c;

def filehash(filepath, blocksize=4096):
    sha = hashlib.sha256()
    with open(filepath, 'rb') as fp:
        while 1:
            data = fp.read(blocksize)
            if data:
                sha.update(data)
            else:
                break
    return sha.hexdigest()



if not os.path.exists(dir1):
    print "no such directory"
    exit(0)
elif not os.access(dir1, os.W_OK):
    print "No permissions to access the directory."
    exit(0)
else:
    os.chdir(dir1)


count=0;
time = datetime.now().strftime("%I:%M%p %B %d, %Y")
log.write("@@@@@Connected to 127.0.0.1 " + "at " + time + " @@@@@\nCommands Sent:\n");

###CHECKING FILES SYNC
time=1;
dict_1={};
dict_2={};
dict_arr=[];
dict_dir={};
hash_arr=[];


def Auto_Sync():
    ##########
    #GET OPPOSITE VALUES
    c=create_client();
    c.send("hash check_down");

    ###get_dirs
    process_msg_arr=c.recv(4096).split();
    if(process_msg_arr[0]=="sent"):
        c.send("recieved msg");##MSG2
        rem=int(process_msg_arr[1]);
        data_1=""
        while rem:
            temp=c.recv(1024);
            rem-=len(temp);
            data_1+=temp;
        c.send("Recieved Data");##MSG3
        dict_arr=data_1.split();
        for i in range(0,len(dict_arr),3):
            dict_dir[dict_arr[i]]=float(dict_arr[i+2]);

    else:
        c.send("Failed socket");##MSG2
        print "Socket operation Failed due to wrong arguments or loss of data";
    #print dict_dir;

    process_msg_arr=c.recv(4096).split();
    if(process_msg_arr[0]=="sent"):
        c.send("recieved msg");##MSG2
        rem=int(process_msg_arr[1]);
        data_1=""
        while rem:
            temp=c.recv(1024);
            rem-=len(temp);
            data_1+=temp;
        c.send("Recieved Data");##MSG3
        hash_arr=data_1.split();
        for i in range(0,len(hash_arr),3):
            dict_1[hash_arr[i]]=float(hash_arr[i+2]);
    else:
        c.send("Failed socket");##MSG2
        print "Socket operation Failed due to wrong arguments or loss of data";
    c.close();

    #GET CURR VALUES
    files=[];
    subdirs=[];
    for root, dirs, filenames in os.walk(dir1):
        for subdir in dirs:
            subdirs.append(os.path.relpath(os.path.join(root, subdir), dir1))
        for f in filenames:
            files.append(os.path.relpath(os.path.join(root,f),dir1));
    for given_file in files:
        dict_2[given_file]=os.path.getmtime(given_file);

    os.chdir(dir1);
    for m in dict_dir.keys():
        if m not in subdirs:
            print "New "+m+" directory is Added";
            os.makedirs(m);


    #COMPARE TWO VALUES:
    #print dict_1;
    #print dict_2;
    rem1=len(dict_1);
    rem2=len(dict_2);
    for k in dict_1.keys():
        if k in dict_2.keys():
            if dict_1[k]>=dict_2[k]:
                print k + " is updated in other side";
                c=create_client();
                c.send("download TCP "+k);
                file_perms=c.recv(4);
                process_msg_arr=c.recv(1024).split();
                if(process_msg_arr[0]=="sent"):
                    given_file=k.strip();
                    c.send("recieved msg");##MSG2
                    rem=int(process_msg_arr[1]);
                    new_c=socket.socket(socket.AF_INET, socket.SOCK_STREAM);
                    new_c.connect((host,rem));##CHECK FOR ERRORS
                    down_arr=new_c.recv(1024).split();
                    c.send("Recieved Data");

                    with open(given_file, 'wb') as fs1:
                        while True:
                            info = new_c.recv(1024)
                            if not info:
                                break
                            fs1.write(info)
                    fs1.close();
                    new_c.send("SUCESS");
                    subprocess.call(['chmod',file_perms,k])
                    ##print("yes1");
                    ###VERIFICATION
                    if filehash(os.path.join(dir1,down_arr[0])) == down_arr[7]:
                        print("File UPDATED  and Verified");
                    else:
                        print("Some data not recieved");
                    #print("yes2");
                    dict_2[k]=down_arr[7];
                    new_c.close();
                    c.close();
        else:
            ##DOWNLOAD file k
            print k + " is Added in other side";
            c=create_client();
            c.send("download TCP "+k);
            file_perms=c.recv(4);
            process_msg_arr=c.recv(1024).split();
            if(process_msg_arr[0]=="sent"):
                given_file=k.strip();
                c.send("recieved msg");##MSG2
                rem=int(process_msg_arr[1]);
                new_c=socket.socket(socket.AF_INET, socket.SOCK_STREAM);
                new_c.connect((host,rem));##CHECK FOR ERRORS
                down_arr=new_c.recv(1024).split();
                c.send("Recieved Data");

                with open(given_file, 'wb') as fs1:
                    while True:
                        info = new_c.recv(1024)
                        if not info:
                            break
                        fs1.write(info)
                fs1.close();
                new_c.send("SUCESS");
                subprocess.call(['chmod',file_perms,k])
                ##print("yes1");
                ###VERIFICATION
                if filehash(os.path.join(dir1,down_arr[0])) == down_arr[7]:
                    print("New File ADDED  and Verified");
                else:
                    print("Some data not recieved");
                #print("yes2");
                dict_2[k]=down_arr[7];
                new_c.close();
                c.close();


    ##########



while True:
    #command Prompt
    Auto_Sync();

    cmd=raw_input("Prompt> ");
    arr=cmd.split();
    count+=1;
    log.write(str(count) + ". " + cmd+"\n");
    #c=create_client();

    while len(arr)>0 and arr[0] !="quit" and arr[0] !="exit":

        c=create_client();
        c.send(cmd);#MSG1
        if(arr[0]=="download"):
            if len(arr)==3 and os.path.isfile(arr[2]):
                file_perms=c.recv(4);
            process_msg_arr=c.recv(1024).split();
            if(process_msg_arr[0]=="sent"):
                if(arr[1]=="TCP"):
                    given_file=' '.join(arr[2:]).strip();
                    c.send("recieved msg");##MSG2
                    rem=int(process_msg_arr[1]);
                    new_c=socket.socket(socket.AF_INET, socket.SOCK_STREAM);
                    #new_c.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    new_c.connect((host,rem));##CHECK FOR ERRORS
                    down_arr=new_c.recv(1024).split();
                    print ("Filename:-",down_arr[0]);
                    print("size:-",down_arr[1]);
                    print("modified time:-",' '.join(down_arr[2:7]));
                    print("md5 hash:-",down_arr[7])
                    c.send("Recieved Data");

                    with open(given_file, 'wb') as fs1:
						while True:
							info = new_c.recv(1024)
							if not info:
								break
							fs1.write(info)
                    fs1.close();
                    subprocess.call(['chmod',file_perms,given_file])
                    new_c.send("SUCESS");
                    ##print("yes1");
                    ###VERIFICATION
                    if filehash(os.path.join(dir1,down_arr[0])) == down_arr[7]:
                        print("File Recieved and Verified");
                    else:
                        print("Some data not recieved");
                    #print("yes2");
                    new_c.close();
                    #print("yes3");

                elif arr[1] == "UDP":
                    filesocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
                    print("connecting to UDP port",process_msg_arr[1])
                    c.send(("b"))
                    fileread = c.recv(1024).split()
                    print("Filename:",fileread[0]);
                    print("Size:",fileread[1]);
                    print("Modified time:",fileread[2:7]);
                    print("MD5 hash:",fileread[7]);
                    readsize = int(fileread[1])
                    sizeread = 0
                    filesocket.sendto("b", (host, int(process_msg_arr[1])));
                    #temp_perms=file_perms;
                    subprocess.call(['chmod','0777',fileread[0]])
                    with open(fileread[0], 'wb') as f:
                        #print("File opened")
                        while True:
                            #print("Receiving Data")
                            if (sizeread>=readsize):
                                break;
                            info, udpaddr = filesocket.recvfrom(4096)
                            #print(info)
                            sizeread += len(info)
                            f.write(info)
                            if not info:
                                break
                    f.close();
                    subprocess.call(['chmod',file_perms,fileread[0]])
                    ###VERIFICATION
                    if filehash(os.path.join(dir1,fileread[0])) == fileread[7]:
                        print("File Recieved and Verified");
                    else:
                        print("Some data not recieved");
                    #print("yes2");
                    filesocket.close();
                    #print("yes3");

                else:
                    print("Watch out!!!, give correct arguments for download command.");

            else:
                c.send("Failed Socket");
                print ("Download Failed due to wrong arguments");
        else:
            process_msg_arr=c.recv(4096).split();
            if(process_msg_arr[0]=="sent"):
                c.send("recieved msg");##MSG2
                rem=int(process_msg_arr[1]);
                data_1=""
                while rem:
                    temp=c.recv(1024);
                    rem-=len(temp);
                    data_1+=temp;
                c.send("Recieved Data");##MSG3
                print(data_1);
            else:
                c.send("Failed socket");##MSG2
                print "Socket operation Failed due to wrong arguments or loss of data";

        c.close();
        Auto_Sync();

        cmd=raw_input("Prompt> ");
        arr=cmd.split();
        time= (time +1)%2;
        count+=1;
        log.write(str(count) + ". " + cmd+"\n");

    print ("Ok,Bye");
    timel = datetime.now().strftime("%I:%M%p %B %d, %Y")
    log.write("@@@@@Connection Closed at " + timel + " @@@@@\n")
    log.close()

    break;
exit(0);
