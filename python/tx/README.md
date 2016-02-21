## TX.py

### Introduction

The main purpose of this script is transfering one file at a time 
from its small database.

For instance, imagine that you have a tool like rtorrent 
that downloads periodically football matchs of your favourite team. 
After the file is completed, you would run this small script with 
the name of the file and after a while you will have.

### Dependences

In order to work, it needs rsync and sqlite3 installed.

### Configuration


#### SSH rsync and ssh client

This script needs ssh passwordless communication between the server
where it runs and the destination server / box, so set up a ssh 
passwordless key and install it in the server where tx.py will run.

For example. In the receiver/destination side:

    home$ ssh-keygen -t rsa -f ./key

Do not put any password, press enter twice. Next thing is to authorize
that password:

    home$ cat ./key.pub >> ~/.ssh/authorized_keys && rm -i ./key.pub

Copy the private key to the host where the script will run.

For example: 

    home$ scp key server_name:~/.ssh

Go to the server and put correct permissions on the file

ssh server_name

    server$ mv  ~/.ssh/key  ~/.ssh/home_name_key
    server$ chmod 600 ~/.ssh/home_name_key

Configure ssh client to automate the use of the private key

    server$ vi ~/.ssh/config

Type something like:

```
--------------- CUT AND PASTE --------------
Host            	home_name
Hostname        	some_real_ip_or_hostname
User            	authorised_user
Compression     	no
StrictHostKeyChecking 	no
IdentityFile   		 ~/.ssh/home_name_key
--------------- CUT AND PASTE --------------
```

To know if rsync will work, you should transfer a file:

rsync --rsh=ssh local_file home_name:remote_path

Where local file is self explanatory, home_name must be same
as written in Host field of previous .ssh/config file.
Remote path must exist and the user must have write rights to it.

#### rtorrent configuration

Put the script is some directory, for example ~/bin, and make it
executable.

     server$ mkdir ~/bin && cp tx.py ~/bin && chmod 755 ~/bin/tx.py

Edit .rtorrent.rc and configure a new event for every downloaded file:

  server$ vi .rtorrent.rc

```
--------------- CUT AND PASTE --------------
system.method.set_key = event.download.finished,transfer_home,"execute=~/bin/tx.py,$d.get_name="
--------------- CUT AND PASTE --------------
```

#### tx.py configuration


We will need a configuration file for tx.py named tx.ini. The first time we run tx.py
it will create a tx.ini skeleton just in case we do not have configured it yet.


For example:

    server$ vi ~/bin/tx.ini

```
--------------- CUT AND PASTE --------------
[server]
address = remote_host
bandwith = 700
localpath = /path/where/rtorrent/puts/files/
remotepath = /remote/path/with/rigths/
timeout    = 1800
max_attempts = 5
disabled = no
log = yes
notify = yes
emailserver = localhost
destaddress = user@domain.com
--------------- CUT AND PASTE --------------
```

Beware of the format. This script is very basic and it does not
make compliance checks.

Explanation of fields:

*address : Host as in .ssh/config host field.
*bandwith: Kbytes / second that rsync will use.
*localpath: where rtorrent files are put and ended with slash
*remotepath: path in home server with permission and ended with slash
*timeout: after this time in seconds the transfer is considered stalled
and will be tried again if max attempts have not been reached.
*max_attempts: Maximum number of tries before a transfer is considered failed.
*disable: to disable this script.
*log: if yes, it will log to tx.log everything.
*notify: if you have a mail server it will send you an email in case a transfer has failed.
*emailserver: if notify : yes, the mail server
*destaddress: email address in case notify and email server are configured.


#### Manual invocation

*If you want to transfer a file with this program just type:

    server$ ./bin/tx.py 'Name of file'

Please only write the name of the file because the directory is already
taken into account in the configuration file.

*If you want to resume a transfer, for example after a power outage or
a inexpected server reboot simply type:

    server$ ./bin/tx.py

The script will open the small database 'tx.db' and will know if it has
to resume file transfering.

*If you want to know how long the queue is make a small query to the database:
```   
   server$ sqlite3 ~/bin/tx.db
   sqlite> SELECT * FROM files;
```

#### Disclaimer

This little script is useful to its creator, so it probably will have some (a lot)
bugs, please take that into account and if you want something to be changed
send me a pull request.

I hope this little piece of software is valuable to someone.
