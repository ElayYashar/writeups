Target: 10.0.0.15

## ***NMAP***

    # nmap -sS -T4 -A -p- 10.0.0.15

    PORT     STATE SERVICE VERSION
    21/tcp   open  ftp     vsftpd 3.0.3
    | ftp-syst: 
    |   STAT: 
    | FTP server status:
    |      Connected to ::ffff:10.0.0.27
    |      Logged in as ftp
    |      TYPE: ASCII
    |      No session bandwidth limit
    |      Session timeout in seconds is 300
    |      Control connection is plain text
    |      Data connections will be plain text
    |      At session startup, client count was 1
    |      vsFTPd 3.0.3 - secure, fast, stable
    |_End of status
    | ftp-anon: Anonymous FTP login allowed (FTP code 230)
    |_-rwxr-xr-x    1 0        0            1306 Oct 12  2020 init.py.bak
    1337/tcp open  http    Werkzeug httpd 1.0.1 (Python 2.7.16)
    |_http-title: Site doesn't have a title (text/html; charset=utf-8).
    | http-auth: 
    | HTTP/1.0 401 UNAUTHORIZED\x0D
    |_  Basic realm=Pickle login
    |_http-server-header: Werkzeug/1.0.1 Python/2.7.16

## ***FTP***

From out NMAP scan we can see that anonymous login is enabled on the FTP server on the machine. Let's login.

    # ftp anonymous@10.0.0.15 

    Connected to 10.0.0.15.
    220 (vsFTPd 3.0.3)
    331 Please specify the password.
    Password: 
    230 Login successful.
    Remote system type is UNIX.
    Using binary mode to transfer files.
    ftp> ls
    229 Entering Extended Passive Mode (|||38265|)
    150 Here comes the directory listing.
    -rwxr-xr-x    1 0        0            1306 Oct 12  2020 init.py.bak

### ***init.py.bak:***

    from functools import wraps
    from flask import *
    import hashlib
    import socket
    import base64
    import pickle
    import hmac

    app = Flask(__name__, template_folder="templates", static_folder="/opt/project/static/")

    @app.route('/', methods=["GET", "POST"])
    def index_page():
            '''
                    __index_page__()
            '''
            if request.method == "POST" and request.form["story"] and request.form["submit"]:
                    md5_encode = hashlib.md5(request.form["story"]).hexdigest()
                    paths_page  = "/opt/project/uploads/%s.log" %(md5_encode)
                    write_page = open(paths_page, "w")
                    write_page.write(request.form["story"])

                    return "The message was sent successfully!"

            return render_template("index.html")

    @app.route('/reset', methods=["GET", "POST"])
    def reset_page():
            '''
                    __reset_page__()
            '''
            pass


    @app.route('/checklist', methods=["GET", "POST"])
    def check_page():
            '''
                    __check_page__()
            '''
            if request.method == "POST" and request.form["check"]:
                    path_page    = "/opt/project/uploads/%s.log" %(request.form["check"])
                    open_page    = open(path_page, "rb").read()
                    if "p1" in open_page:
                            open_page = pickle.loads(open_page)
                            return str(open_page)
                    else:
                            return open_page
            else:
                    return "Server Error!"

            return render_template("checklist.html")

    if __name__ == '__main__':
            app.run(host='0.0.0.0', port=1337, debug=True)

The Python script we found seems to be running ***flask*** on the remote machine on port 1337.

## ***HTTP | PORT 1337 ***

Going to ***http://10.0.0.15:1337*** we are prompted to enter a username and password.

![image](https://user-images.githubusercontent.com/76552238/171037699-90f79ab3-29a3-4261-8684-1e2c45a420e0.png)

This server is running ***SNMP***, let's use the command ***snmp-check*** to get some information out of the service.

    # snmp-check 10.0.0.15

    snmp-check v1.9 - SNMP enumerator
    Copyright (c) 2005-2015 by Matteo Cantoni (www.nothink.org)

    [+] Try to connect to 10.0.0.15:161 using SNMPv1 and community 'public'

    [*] System information:

    Host IP address               : 10.0.0.15
    Hostname                      : pickle
    Description                   : Linux pickle 4.19.0-11-amd64 #1 SMP Debian 4.19.146-1 (2020-09-17) x86_64
    Contact                       : lucas:SuperSecretPassword123!
    Location                      : Sitting on the Dock of the Bay
    Uptime snmp                   : 00:37:16.99
    Uptime system                 : 00:36:58.08
    System date                   : 2022-5-30 13:48:33.0

In the Contact tab we can find the username and password for the login page on port 1337.

![image](https://user-images.githubusercontent.com/76552238/171041057-99249b37-b81e-4151-99c0-1b53ad6a978b.png)

After logging in with the credentials we found, we are directed to the page seen above. Now we can the view the Python script we found the FTP server and see how the web server is built.
Going to ***http://10.0.0.15/reset*** and ***http://10.0.0.15/checklist*** we get a server error.

...

<!--Run as python2 (bullshit!)-->

Using a Python script we can execute arbitrary code on the remote machine and get a reverse shell.

## ***PRIVILEGE ESCALATION***

    $ whoami
    lucas


We are logged in as the user ***'lucas'***. 

    $ pwd
    /home
    $ ls -l
    drwxr-xr-x 3 lucas lucas 4096 Oct 11  2020 lucas
    drwxr-x--- 4 mark  mark  4096 Oct 12  2020 mark


The machine has another named ***'mark'*** on the machine which we currently don't have access to.
There are no SUID files and we don't have access to use the ***'sudo'*** command. 

After uploading and executing ***'linPeas'*** to the remote machine we can find the directory ***/opt/project*** where is web server is running.

    $ pwd
    /opt/project
    $ ls -l
    -rwxr-xr-x 1 root root 2654 Oct 12  2020 project.py
    drwxr-xr-x 4 root root 4096 Oct 11  2020 static
    drwxr-xr-x 2 root root 4096 Oct 11  2020 templates
    drwxrwxrwx 2 root root 4096 May 31 12:20 uploads

After reading ***'project.py'***, we have two addons from the backup script we found on the FTP server.

    @app.route('/reset', methods=["GET", "POST"])
    @requires_auth
    def reset_page():
            '''
                    __reset_page__()
            '''
            if request.method == "POST" and request.form["username"] and request.form["key"]:
                    key    = "dpff43f3p214k31301"
                    raw    = request.form["username"] + key + socket.gethostbyname(socket.gethostname())
                    hashed = hmac.new(key, raw, hashlib.sha1)
                    if request.form["key"] == hashed.hexdigest():
                            return base64.b64encode(hashed.digest().encode("base64").rstrip("\n"))
            else:
                    return "Server Error!"
            return render_template("reset.html")

    ...
    ...
    ...

    @app.route('/console')
    @requires_auth
    def secret_page():
            return "Server Error!"

Let's start with with ***'reset_page()'*** method.

    user.txt: 
    e25fd1b9248d1786551e3412adc74f6f

After logging in as the user ***'mark'*** we have a an executable with SUID root permissions. Running it gives us a Python shell, by using the ***'os'*** library we are able to run commands as root on the machine and read the final flag.

    root.txt:
    7a32c9739cc63ed983ae01af2577c01c