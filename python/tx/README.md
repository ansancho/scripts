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

    $ ssh-keygen -t rsa -f ./key

Do not put any password, press enter twice. Next thing is to authorize
that password:

    $ cat ./key.pub >> ~/.ssh/authorized_keys && rm -i ./key.pub

Copy the private key to the host where the script will run.

For example: 

    $ scp key server_name:~/.ssh

Go to the server and put correct permissions on the file

ssh server_name

    # mv  ~/.ssh/key  ~/.ssh/home_name_key
    # chmod 600 ~/.ssh/home_name_key

Configure ssh client to automate the use of the private key

    # vi ~/.ssh/config

Type something like:

```
-----------------------------------------------
Host            	home_name
Hostname        	some_real_ip_or_hostname
User            	authorised_user
Compression     	no
StrictHostKeyChecking 	no
IdentityFile   		 ~/.ssh/home_name_key
-----------------------------------------------
```

To know if rsync will work, you should transfer a file:

rsync --rsh=ssh local_file home_name:remote_path

Where local file is self explanatory, home_name must be same
as written in Host field of previous .ssh/config file.
Remote path must exist and the user must have write rights to it.


