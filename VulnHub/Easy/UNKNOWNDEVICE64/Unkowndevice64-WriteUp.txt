Step 1: NMAP

PORT      STATE SERVICE VERSION
1337/tcp  open  ssh     OpenSSH 7.7 (protocol 2.0)
31337/tcp open  http    SimpleHTTPServer 0.6 (Python 2.7.14)

We have 2 services, http and ssh, both of them are not on their usual ports.
------------------------------------------------------------------------------------------------------------------------------------
Step 2: HTTP

dirsearch http://10.0.0.34:31337

We find nothing.

Using dev tools in http://10.0.0.34:31337 we see a comment:

<!-- key_is_h1dd3n.jpg -->

I tried going to http://10.0.0.34:31337/h1dd3n.jpg but nothing showed up, turns out you need
to to go to http://10.0.0.34:31337/key_is_h1dd3n.jpg.

curl http://10.0.0.34:31337/key_is_h1dd3n.jpg --output key_is_h1dd3n.jpg

After downloading the file to our local machine, we can try extract date of the image.

Using "strings key_is_h1dd3n.jpg" we get nothing, aswell as trying to view the exif date.
I searched how to get hidden information from pictures and I found out there is a comamnd named "steghide"
that allows to extract hidden files from pictures.

steghide extract -sf key_is_h1dd3n.jpg

We need to enter a passphrase, tried a couple of options, but it was the marked word on the site, "h1dd3n".
We get a text file. Reading it and we get a BRAINF*CK code.

++++++++++[>+>+++>+++++++>++++++++++<<<<-]>>>>+++++++++++++++++.-----------------.<----------------.--.++++++.---------.>-----------------------.<<+++.++.>+++++.--.++++++++++++.>++++++++++++++++++++++++++++++++++++++++.-----------------.

Executing it and we get a username and password ---> ud64:1M!#64@ud
------------------------------------------------------------------------------------------------------------------------------------
Step 2: SSH

Now that we have a username and password wae can connet to the machine via ssh.

ssh ud64@10.0.0.34 -p 1337

And we have access. Trying to run commands like: ls, cd ,wheris,sudo does not seem to work.
Viewing the used shell we see we are running a restirced shell.
Viewing the PATH variable: /home/ud64/prog
Trying to change it says the variable is a read only file.
Pressing "tab" to view the commands we can run, we can run the vi text editor.

:!/bin/bash

Opening a new not restricted shell, we can change the PATH variable to /usr/bin and be able to run commands.
Using sudo -l to view what commands we can run as root, we can run 
the file "/usr/bin/sysud64".
Opening the help menu, it seems the file is running a file called strace.
Strace is a "system call tracer", it shows what kernel functions are being called as a result of your program.

Running the command with sudo and passing vi as a paramter it opens vi, opening a new bash shell and viewing what is the current user and we are the root user!! 
Going to /root we have the flag.txt file.

And with the CTF is finished.