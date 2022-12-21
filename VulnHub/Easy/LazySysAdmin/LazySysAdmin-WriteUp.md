LazySysAdmin WriteUP

Step 1: NMAP
nmap -sS -T4 -sV -p- 10.0.0.31

PORT     STATE SERVICE     VERSION
22/tcp   open  ssh         OpenSSH 6.6.1p1 Ubuntu 2ubuntu2.8 (Ubuntu Linux; protocol 2.0)
80/tcp   open  http        Apache httpd 2.4.7 ((Ubuntu))
139/tcp  open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
445/tcp  open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
3306/tcp open  mysql       MySQL (unauthorized)
6667/tcp open  irc         InspIRCd

Service Info: Hosts: LAZYSYSADMIN, Admin.local;
------------------------------------------------------------------------------------------------------------------------------
Step 2: SAMBA
Using smbmap to see the open shares in port 445:

        Disk                                                    Permissions     Comment
        ----                                                    -----------     -------
        print$                                                  NO ACCESS       Printer Drivers
        share$                                                  READ ONLY       Sumshare
        IPC$                                                    NO ACCESS       IPC Service (Web server)

We have 3 shares, and we can see that we can only read the "share" share, we don't 
have access to the other ones, we will probebly need a username and password to view those.

smbclient -H '\\\\10.0.0.31\\share$'

We have some files, but only a couple have an intrest to us, deets.txt, robots.txt and todolist.txt.

deets.txt:
CBF Remembering all these passwords.

Remember to remove this file and update your password after we push out the server.

Password 12345

root@kali ~/D/C/L/

robots.txt:
User-agent: *
Disallow: /old/
Disallow: /test/
Disallow: /TR2/
Disallow: /Backnode_files/

todolist.txt:
Prevent users from being able to view to web root using the local file browser

Now we have a password and some useful info to enumerate HTTP.
We also have the wordpress folder on the SAMABA service, viewing it and we have the wp-config.php file.

/** MySQL database username */
define('DB_USER', 'Admin');

/** MySQL database password */
define('DB_PASSWORD', 'TogieMYSQL12345^^');

username:"Admin"
password:"TogieMYSQL12345^^"

Now we have the username and password for wordpress admin account.

I think we are ready to view the site on port 80.

------------------------------------------------------------------------------------------------------------------------------
Step 3: HTTP

Viewing the site, it doesn't have any hyperlinks or anything intersting. Viewing the source code of the site and we don't have 
any comments or anything intersting aswell.
So let's see if it has any intersting directories.

dirsearch -u http://10.0.0.31:

[08:16:21] 200 -  737B  - /apache/                                          
[08:16:28] 200 -   35KB - /index.html                                           
[08:16:30] 200 -   76KB - /info.php                                                          
[08:16:33] 200 -  731B  - /old/                                                
[08:16:35] 200 -    8KB - /phpmyadmin/                                      
[08:16:35] 200 -    8KB - /phpmyadmin/index.php                             
[08:16:36] 200 -   92B  - /robots.txt                                                                                       
[08:16:39] 200 -  733B  - /test/                                                               
[08:16:42] 200 -  729B  - /wp/                                              
[08:16:43] 200 -    3KB - /wordpress/wp-login.php                           
[08:16:43] 200 -   10KB - /wordpress/

We already viewed the robots.txt file from the SAMBA service, the directories listed do not contain anything.
Going into http://10.0.0.31/wordpress/ we have a wordpress site.

Let's see if any info we can get about this site.

wpscan -v -e ap,vt,cb,u --url http://10.0.0.31/wordpress

Not showing us something we don't already know.
Going to http://10.0.0.31/wordpress/wp-login.php and using the found creditnrals from the wp-config.php file 
we gain access to the admin panel.

Now is the part where we upload a reverse shell to site and connect to the machine.

I found on github a reverse shell script in php
https://github.com/pentestmonkey/php-reverse-shell
and uploded it to the 404.php page.
Listening on my local host and going to 
http://10.0.0.31/wordpress/wp-content/themes/twentyfifteen/404.php and get a reverse shell.
------------------------------------------------------------------------------------------------------------------------------
Step 4: PRIVILIGE ESCILATION

whoami: www-data
Now that we access to the machine let's see what we can do with this user.
It seems we don't any any permissions with the current user.
Looking at /etc/passwd to search for any other users, we find a user named "togie".
Now all we need is a password, going back to the deets.txt file found on the SAMBA service we found this 
password:"12345", let's see if works. And we have access to the togie user.
Using "sudo -l":

User togie may run the following commands on LazySysAdmin:
    (ALL : ALL) ALL

switching to the root user and we can grab the proof.txt file:

WX6k7NJtA8gfk*w5J3&T@*Ga6!0o5UP89hMVEQ#PT9851


Well done :)

Hope you learn't a few things along the way.

Regards,

Togie Mcdogie




Enjoy some random strings

WX6k7NJtA8gfk*w5J3&T@*Ga6!0o5UP89hMVEQ#PT9851
2d2v#X6x9%D6!DDf4xC1ds6YdOEjug3otDmc1$#slTET7
pf%&1nRpaj^68ZeV2St9GkdoDkj48Fl$MI97Zt2nebt02
bhO!5Je65B6Z0bhZhQ3W64wL65wonnQ$@yw%Zhy0U19pu
------------------------------------------------------------------------------------------------------------------------------
And with that we have finished the CTF.