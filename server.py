import socket,os,sys
import hashlib,re,subprocess
from datetime import datetime
import time;

port = 50000;
host="";
new_ports=[50002,50001,50003];

dir1=str(sys.argv[1]);
if(os.path.isdir(dir1)):
    pass;
else:
    print "ENTER CORRECT DIRECTORY NAME,THIS DIR DOESN'T EXISTS";
    exit(0);

#print "server\n";
###SERVER CODE init
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host,port));##CHECK FOR ERROR
s.listen(5);##CHANGE FOR ACCEPTED REQUESTS
print 'Server is Listening to',host,":",port;

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

def cal_perm(temp):
    user=0;grp=0;oth=0;
    if(temp[1]=='r'):
        user+=4;
    if(temp[2]=='w'):
        user+=2;
    if(temp[3]=='x'):
        user+=1;
    if(temp[4]=='r'):
        grp+=4;
    if(temp[5]=='w'):
        grp+=2;
    if(temp[6]=='x'):
        grp+=1;
    if(temp[7]=='r'):
        oth+=4;
    if(temp[8]=='w'):
        oth+=2;
    if(temp[9]=='x'):
        oth+=1;
    return '0'+str(user)+str(grp)+str(oth);


#subprocess.call(['chmod','0644','testing1'])

if not os.path.exists(dir1):
    print "no such directory"
    exit(0)
elif not os.access(dir1, os.W_OK):
    print "No permissions to access the directory."
    exit(0)
else:
    os.chdir(dir1)

while True:
    conn,addr=s.accept();
    print 'Got Connection from',addr;
    command_from_client = conn.recv(1024);
    print command_from_client;
    arr1=command_from_client.split();
    if arr1[0]=="index":

        if len(arr1)==2 and arr1[1]=="longlist":

            files = [f for f in os.listdir(dir1) if os.path.isfile(f)];
            subdirs=[f for f in os.listdir(dir1) if os.path.isdir(f)];
            data_to_client="";
            for f in files:
                file_type="F";
                stat = os.stat(f);
                size = str(stat.st_size);
                modified_time = time.ctime(stat.st_mtime);
                temp='   '.join([f,size,modified_time,file_type]);
                data_to_client+=temp+'\n';
            for f in subdirs:
                file_type="D";
                stat = os.stat(f);
                size = str(stat.st_size);
                modified_time = time.ctime(stat.st_mtime);
                temp='   '.join([f,size,modified_time,file_type]);
                data_to_client+=temp+'\n';
            rem=len(data_to_client);
            conn.send("sent "+str(len(data_to_client)));
            rem=conn.recv(1024);
            print rem;
            conn.sendall(data_to_client);
            rem=conn.recv(1024);
            print rem;

        elif len(arr1)==10 and arr1[1]=="shortlist":

            files = [f for f in os.listdir(dir1) if os.path.isfile(f)];
            subdirs=[f for f in os.listdir(dir1) if os.path.isdir(f)];
            data_to_client="";
            #time.strptime("28 12 2001 11:11:11", '%d %m %Y %H:%M:%S')
            ts1=time.mktime(time.strptime(' '.join(arr1[2:6]), '%d %m %Y %H:%M:%S'))
            ts2=time.mktime(time.strptime(' '.join(arr1[6:10]), '%d %m %Y %H:%M:%S'))
            #print files;
            #print subdirs;
            for f in files:
                file_type="F";
                stat = os.stat(f);
                size = str(stat.st_size);
                modified_time = time.ctime(stat.st_mtime);
                temp='';
                if ts1<os.path.getmtime(f)<ts2:
                    temp='   '.join([f,size,modified_time,file_type]);
                    data_to_client+=temp+'\n';
            #print data_to_client;
            for f in subdirs:
                file_type="D";
                stat = os.stat(f);
                size = str(stat.st_size);
                modified_time = time.ctime(stat.st_mtime);
                temp='';
                if ts1<os.path.getmtime(f)<ts2:
                    temp='   '.join([f,size,modified_time,file_type]);
                    data_to_client+=temp+'\n';
            rem=len(data_to_client);
            conn.send("sent "+str(len(data_to_client)));
            rem=conn.recv(1024);
            print rem;
            conn.sendall(data_to_client);
            rem=conn.recv(1024);
            print rem;

        elif len(arr1)>=3 and arr1[1]=="regex":

            files = [f for f in os.listdir(dir1) if os.path.isfile(f)];
            subdirs=[f for f in os.listdir(dir1) if os.path.isdir(f)];
            data_to_client="";
            compiled_regex=re.compile(' '.join(arr1[2:]).strip());
            for f in files:
                file_type="F";
                stat = os.stat(f);
                size = str(stat.st_size);
                modified_time = time.ctime(stat.st_mtime);
                temp='';
                if compiled_regex.match(f):
                    temp='   '.join([f,size,modified_time,file_type]);
                    data_to_client+=temp+'\n';
            #print data_to_client;
            for f in subdirs:
                file_type="D";
                stat = os.stat(f);
                size = str(stat.st_size);
                modified_time = time.ctime(stat.st_mtime);
                temp='';
                if compiled_regex.match(f):
                    temp='   '.join([f,size,modified_time,file_type]);
                    data_to_client+=temp+'\n';
            rem=len(data_to_client);
            conn.send("sent "+str(len(data_to_client)));
            rem=conn.recv(1024);
            print rem;
            conn.sendall(data_to_client);
            rem=conn.recv(1024);
            print rem;

        else:
            print("WATCH OUT, give correct arguments for Index command");
            conn.send("not_sent");
            rem=conn.recv(1024);
            print rem;
            rem=conn.recv(1024);
            print rem;
    elif arr1[0]=="hash":
        if len(arr1)==3 and arr1[1]=="verify":

            given_file=' '.join(arr1[2:]).strip();
            data_to_client="";
            if os.path.isfile(given_file):
                hash_val=filehash(os.path.join(dir1, given_file));
                mod_t = time.ctime(os.path.getmtime(given_file))
                data_to_client=hash_val+' '+mod_t;
                rem=len(data_to_client);
                conn.send("sent "+str(len(data_to_client)));
                rem=conn.recv(1024);
                print rem;
                conn.send(data_to_client);
                rem=conn.recv(1024);
                print rem;
            else:
                print("WATCH OUT, give correct arguments for hash command");
                conn.send("not_sent");
                rem=conn.recv(1024);
                print rem;
                rem=conn.recv(1024);
                print rem;
        elif len(arr1)==2 and arr1[1]=="checkall":
            files = [f for f in os.listdir(dir1) if os.path.isfile(f)];
            #subdirs=[f for f in os.listdir(dir1) if os.path.isdir(f)];
            #files=list(set(files) | set(subdirs));

            data_to_client="";
            for given_file in files:
                    hash_val=filehash(os.path.join(dir1, given_file));
                    mod_t = time.ctime(os.path.getmtime(given_file));
                    data_to_client+=given_file+' '+hash_val+' '+mod_t+'\n';
            rem=len(data_to_client);
            conn.send("sent "+str(len(data_to_client)));
            rem=conn.recv(1024);
            print rem;
            conn.send(data_to_client);
            rem=conn.recv(1024);
            print rem;
        elif len(arr1)==2 and arr1[1]=="check_down":
            files=[];
            subdirs=[];
            for root, dirs, filenames in os.walk(dir1):
                for subdir in dirs:
                    subdirs.append(os.path.relpath(os.path.join(root, subdir), dir1))
                for f in filenames:
                    files.append(os.path.relpath(os.path.join(root,f),dir1));
            data_to_client='';
            dirs_to_client='';
            for given_file in subdirs:
                    hash_val='0';
                    mod_t = str(os.path.getmtime(given_file));
                    dirs_to_client+=given_file+' '+hash_val+' '+mod_t+'\n';
            rem=len(dirs_to_client);
            conn.send("sent "+str(len(dirs_to_client)));
            rem=conn.recv(1024);
            print rem;
            conn.send(dirs_to_client);
            rem=conn.recv(1024);
            print rem;


            for given_file in files:
                    hash_val=filehash(os.path.join(dir1, given_file));
                    mod_t = str(os.path.getmtime(given_file));
                    data_to_client+=given_file+' '+hash_val+' '+mod_t+'\n';

            rem=len(data_to_client);
            conn.send("sent "+str(len(data_to_client)));
            rem=conn.recv(1024);
            print rem;
            conn.send(data_to_client);
            rem=conn.recv(1024);
            print rem;


        else:
            print("WATCH OUT, give correct arguments for hash command");
            conn.send("not_sent");
            rem=conn.recv(1024);
            print rem;
            rem=conn.recv(1024);
            print rem;
    elif arr1[0]=="download":
        if len(arr1)==3 and arr1[1]=="TCP":

            given_file=' '.join(arr1[2:]).strip();
            if os.path.isfile(given_file):
                temp_arr=subprocess.check_output('ls -l| sed \'1 d\'| awk \'{print $1" "$5" " $6" " $7" "$8" " $9}\'',shell=True).split('\n');
                val='0664';flag=0;
                for i in range(len(temp_arr)-1):
                    each=temp_arr[i].split(' ');
                    if(each[5]==given_file):
                        val=cal_perm(each[0]);
                        flag=1;
                if flag==0:
                    temp_file=given_file.split('/');
                    temp_dir='/'.join(temp_file[:-1]);
                    os.chdir(temp_dir);
                    temp_arr_1=subprocess.check_output('ls -l| sed \'1 d\'| awk \'{print $1" "$5" " $6" " $7" "$8" " $9}\'',shell=True).split('\n');
                    for i in range(len(temp_arr_1)-1):
                        each=temp_arr_1[i].split(' ');
                        if(each[5]==temp_file[-1]):
                            val=cal_perm(each[0]);
                            #print val;


                os.chdir(dir1);
                conn.send(val);
                hash_val=filehash(os.path.join(dir1, given_file));
                mod_t = time.ctime(os.path.getmtime(given_file));
                stat=os.stat(given_file);
                size=str(stat.st_size);
                if len(new_ports)==0:
                    print "No available ports for download";
                    continue;
                new_port=new_ports.pop();
                new_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
                new_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                new_sock.bind((host,new_port));##CHECK FOR ERROR
                new_sock.listen(1);##CHANGE FOR ACCEPTED REQUESTS
                conn.send("sent "+str(new_port));
                rem=conn.recv(1024);
                print rem;
                new_conn,new_addr=new_sock.accept();
                data_to_client=given_file+' '+size+' '+mod_t+' '+hash_val+'\n';
                new_conn.send(data_to_client);
                rem=conn.recv(1);
                #print rem;

                with open(given_file, "rb") as fs:
                    for chunk in iter(lambda: fs.read(4096), b""):
                        new_conn.send(chunk);
                print ("DONE SENDING");
                fs.close();
                #new_conn.send("BYE");
                #new_conn.recv(1024);#CHANGE BASED ON CLIENT FINAL MSG
                new_conn.close();
                new_sock.close();
                new_ports.append(new_port);

            else:
                print("WATCH OUT, give correct arguments for download command");
                conn.send("not_sent");
                rem=conn.recv(1024);
                print rem;
                rem=conn.recv(1024);
                print rem;

        elif len(arr1)==3 and arr1[1]=="UDP":

            try:
                given_file=' '.join(arr1[2:]).strip()
                if not os.path.isfile(given_file):
                    print("WATCH OUT, give correct arguments for download command");
                    conn.send("not_sent");
                    rem=conn.recv(1024);
                    print rem;
                    rem=conn.recv(1024);
                    print rem;
                else:
                    temp_arr=subprocess.check_output('ls -l| sed \'1 d\'| awk \'{print $1" "$5" " $6" " $7" "$8" " $9}\'',shell=True).split('\n');
                    val='0664';flag=0;
                    for i in range(len(temp_arr)-1):
                        each=temp_arr[i].split(' ');
                        if(each[5]==given_file):
                            val=cal_perm(each[0]);
                            flag=1;
                    if flag==0:
                        temp_file=given_file.split('/');
                        temp_dir='/'.join(temp_file[:-1]);
                        os.chdir(temp_dir);
                        temp_arr_1=subprocess.check_output('ls -l| sed \'1 d\'| awk \'{print $1" "$5" " $6" " $7" "$8" " $9}\'',shell=True).split('\n');
                        for i in range(len(temp_arr_1)-1):
                            each=temp_arr_1[i].split(' ');
                            if(each[5]==temp_file[-1]):
                                val=cal_perm(each[0]);
                                print val;
                    os.chdir(dir1);
                    conn.send(val);
                    stat = os.stat(given_file)
                    size = str(stat.st_size)
                    mod_t = time.ctime(stat.st_mtime)
                    hashval=filehash(os.path.join(dir1, given_file));
                    f=open(given_file, 'rb')
                    if not len(new_ports):
                        print("no ports available ",repr(addr))
                        raise(IndexError)
                    new_port=new_ports.pop()
                    new_sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    new_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    new_sock.bind((host, new_port))
                    conn.send(("sent "+str(new_port)))
                    conn.recv(1)
                    conn.send((given_file+' '+size+' '+mod_t+' '+hashval+'\n'))
                    data, (taddr, destinport) = new_sock.recvfrom(1024)
                    print("taddr destin",taddr,destinport)
                    with open(given_file, "rb") as f:
                        for chunk in iter(lambda: f.read(4096), b""):
                            #print(chunk)
                            new_sock.sendto(chunk, (taddr, destinport))
                    #print("File sent!")
                    new_sock.close()
                    new_ports.append(new_port)
            except IndexError:
                print("Invalid command",repr(data),"recieved from",repr(addr))
                conn.send("not_send")
                conn.recv("socket operation failed");



        else:
            print("WATCH OUT, give correct arguments for download command");
            conn.send("not_sent");
            rem=conn.recv(1024);
            print rem;
            rem=conn.recv(1024);
            print rem;
    else:
        print("WATCH OUT, give correct command");
        conn.send("not_sent");
        rem=conn.recv(1024);
        print rem;
        rem=conn.recv(1024);
        print rem;
    conn.close();
