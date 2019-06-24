# Configuration

### Create environment

```
py -3 -m venv venv
```

### Active environment

```
venv\Scripts\activate
```

### Install Flask

```
pip install Flask
```

### Download mod_wsgi

[http://www.lfd.uci.edu/~gohlke/pythonlibs/#pil](https://link.jianshu.com/?t=http://www.lfd.uci.edu/~gohlke/pythonlibs/#pil)



### Remove

decompress the file by changing the file type as zip

remove ==server/mod_wsgi.cp36-win_amd64.pydf== to ==Apache/modules==

rename mod_wsgi.cp36-win_amd64.pyd  as ==mod_wsgi.pyd==

open Apache24\conf\httpd.conf

add ==LoadModule wsgi_module modules/mod_wsgi.pyd==

remove ==#== before LoadModule vhost_alias_module modules/mod_vhost_alias.so



### wsgi.py 

In the Flask project, add ==wsgi.py== file 

```
from app import app as application
```

### Configuration

In ==httpd.conf== file

```
Listen 6111
<VirtualHost *:6111>
    WSGIScriptAlias / C:\test\wsgi.py
    <Directory 'C:\test'>
        Require all granted
        Require host ip
    </Directory>
</VirtualHost>
```

