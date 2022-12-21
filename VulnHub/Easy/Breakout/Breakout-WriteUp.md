Step 1: NMAP

nmap -sS -sV -T4 -p- 10.0.0.32

PORT      STATE SERVICE     VERSION
80/tcp    open  http        Apache httpd 2.4.51 ((Debian))
139/tcp   open  netbios-ssn Samba smbd 4.6.2
445/tcp   open  netbios-ssn Samba smbd 4.6.2
10000/tcp open  http        MiniServ 1.981 (Webmin httpd)
20000/tcp open  http        MiniServ 1.830 (Webmin httpd)

We have 3 interesting services, SMB, Apache and Webmin running on HTTP.

Searching what Webmin is, we find out that Webmin allows the user to configure operating system internals,
such as users, services or configuration files.
----------------------------------------------------------------------------------------------------------------------------
Step 2: ENUM4LINUX

enum4linux -a 10.0.0.32

We find out a few things that may have interst us. We find two shares on SMB: 
print$ and IPC$, but it stats:
"Reconnecting with SMB1 for workgroup listing.
protocol negotiation failed: NT_STATUS_INVALID_NETWORK_RESPONSE
Unable to connect with SMB1 -- no workgroup available
", taht means we can't enumrate SMB and get the content from the shares.

We also find our a username, "cyber", let's see where is helps us down the road.
----------------------------------------------------------------------------------------------------------------------------
Step 2: HTTP:80

dirsearch -u http://10.0.0.32

We only find:
/index.html
/manual/index.html

Going to http://10.0.0.32/index.html and we have the landing page of the apache service. Using the dev tools 
to see the source code of the site, we find a comment:

<!--
don't worry no one will get here, it's safe to share with you my access. Its encrypted :)

++++++++++[>+>+++>+++++++>++++++++++<<<<-]>>++++++++++++++++.++++.>>+++++++++++++++++.----.<++++++++++.-----------.>-----------.++++.<<+.>-.--------.++++++++++++++++++++.<------------.>>---------.<<++++++.++++++.


-->

From what I can tell this is a BRAINF*CK script. After executing it, this is the output:

.2uqPEfj3D<P'a-3

Looks like one of those generated safe passwords.
----------------------------------------------------------------------------------------------------------------------------
Step 3: HTTPS:10000/20000

Going to http://10.0.0.32/10000 and we redirected to the https version of the url. We are greeted to a login page.
Using dirsearch to find more about the site and there is nothing intersting that can help us, as also using dev tools.
We have found a username and password from enumrating the services, let's see if they are the correct login credintals.
And not luck, but going to https://10.0.0.32/20000 and we gain access using those credintals.
----------------------------------------------------------------------------------------------------------------------------
Step 4: Usermin & Privilage Esceation

Now that we have access, looking in the bottom left and we get the option to open a command shell.
Going into the /home/cyber folder and reading its content we find a user.txt:

3mp!r3{You_Manage_To_Break_To_My_Secure_Access}

Using "sudo -l" to see if we have any permissions, and turns out the sudo command doesn't exist on this machine.
In the home dir, there is another file named tar.
Using the "file" command to find out what kind of file it is, we find out it is and exectuable.
Reading the manual page of the command, we get this description:

"saves many files together into a single tape or disk archive, and can
restore individual files from the archive."

Using the "getcap" command to get more info about the executable, it returns: 

cap_dac_read_search=ep

Searching what is "cap_dac_read_search=ep", it reads:
"Bypass file read permission checks and directory read and execute permission checks",
this means if we archive files and restore them we can read them no matter the permissions.

I tried finding a file with SUID permissions but no luck. But going into the /var/backups folder and listing the hidden files, there is a file 
named .old_pass.bak. We can't read the file because we don't permission.
This is where the tar file comes in.

./tar -cf back.tar /var/backups/.old_pass.bak

./tar -xf back.tar

And we got another password:

Ts&4&YurgtRX(=~h
----------------------------------------------------------------------------------------------------------------------------
Step 5: ROOT USER

Going back to the login page.
Entering the credintals root:Ts&4&YurgtRX(=~h, we have access.
Opening a terminal and we find the r00t.txt file:

3mp!r3{You_Manage_To_BreakOut_From_My_System_Congratulation}

Author: Icex64 & Empire Cybersecurity

Finding the root and user flags and with that the CTF is finished.