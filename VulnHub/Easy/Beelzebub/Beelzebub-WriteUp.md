Some background before scanning, in the old tesemony, Beelzebub is king of the devils,  
 In theological sources, Beelzebub is another name for Satan.

Step 1 : NMAP

nmap -v -sV -sS -p- 10.0.0.30

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 20:d1:ed:84:cc:68:a5:a7:86:f0:da:b8:92:3f:d9:67 (RSA)
|   256 78:89:b3:a2:75:12:76:92:2a:f9:8d:27:c1:08:a7:b9 (ECDSA)
|_  256 b8:f4:d6:61:cf:16:90:c5:07:18:99:b0:7c:70:fd:c0 (ED25519)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-title: Apache2 Ubuntu Default Page: It works
|_http-server-header: Apache/2.4.29 (Ubuntu)
------------------------------------------------------------------------------------------------------------------------------------
Step 2 : HTTP

When we go to http://10.0.0.30/, we get Apache2's Default Page.
This means to suggest there is no content on this site, but let's use dirsearch just to make sure.

dirsearch -u http://10.0.0.30/:
Going into http://10.0.0.30/index.php and we a 403 error code.
Inspecting with the dev tools to the site's source code and we see a comment:

<!--My heart was encrypted, "beelzebub" somehow hacked and decoded it.-md5-->                              
                                                                                                           
I got stuck on this part for long time, I searched beelzebub's heart, and started searching demonic history,                                                                                                          
found a book, I was really lost, but then I tried to enrypt the string "beelzebub".                        
d18e1e22becbd915b45e0e655429d487, I tried putting it in the url --> http://10.0.0.30/d18e1e22becbd915b45e0e655429d487 and use dirsearch on it.                                                                        
                                                                                                           
dirsearch http://10.0.0.30/d18e1e22becbd915b45e0e655429d487:

And we a site that is built on Word Press. Going into http://10.0.0.30/d18e1e22becbd915b45e0e655429d487/wp-content/uploads/,
and we have a file named Talk To VALAK. (Valak is that scary ghost nun).
It has an input field. Entering ' to test for and sql injection doesn't work, but trying XSS by entering
<h1> "Hello "World" </h1> or <script> alert(1) </script> works!!!
But it doesn't seem like we need to use XSS right now.
Using Burp Suite to capture the request, we can see this header:

Cookie: Cookie=b7d0eff31b9cde9a862dc157bb33ec2a; Password=M4k3Ad3a1

Decrypting that cookie and we get --> krampus

Now that we have a username and a password we can log in via ssh.

------------------------------------------------------------------------------------------------------------------------------------
Step 3: SSH

Using the creditnals we found we log into the machine.
Going into /home/krampus/Desktop we have a user.txt file, it reads:
aq12uu909a0q921a2819b05568a992m9
I guess another hash. Trying to decrypt it does not seem to work.
#Listing the hidden files in the krampus folder and we find a file named .Serv-U-Tray.conf.
#Searching online what is Serv-U-Tray, it is a simple, affordable, easy to use FTP server software.
Looking at the .bash_history file to trace any helpful steps we find that the user downloaded a file.

wget https://www.exploit-db.com/download/47009

Download that file to the machine and we find out that it is a .c file, compling it running 
grants us a shell, using whoami and we are the root user.
Going into the root folder to find the root.txt:
8955qpasq8qq807879p75e1rr24cr1a5

And with that we have completed the CTF.
------------------------------------------------------------------------------------------------------------------------------------
This was a pretty east CTF, made look somewhere I never thought something would be, thinking outside of the box a little.