upd：由于作者前几天不小心把树莓派上的 Python 扬了，ScreepsMinus 暂时不能使用

---
ScreepsMinus 代码已开源：[Github Repo](https://github.com/ScreepsMinus/screepsminus-core)  
本教程适用于 Ubuntu/Raspbian 系统

## 目录

0x01 部署 Carbon 和 Graphite-API  

- 安装 Carbon
- 安装 Graphite-API
- 使用 Apache2 部署 Graphite-API

0x02 部署 Grafana  
0x03 后端编写  
0x04 前端编写

## 0x01 安装 Carbon 和 Graphite-API

### 安装 Carbon

- 使用 APT 安装

```
apt-get install graphite-carbon
```

- 修改配置文件 `/etc/default/graphite-carbon`

```
CARBON_CACHE_ENABLED=true
```

- 启动 Carbon 服务

```
service carbon-cache start
```

### 安装 Graphite-API

- 安装依赖

```
apt-get install python python-pip build-essential python-dev libcairo2-dev libffi-dev
```

- 安装 Graphite-API

```
pip install graphite-api
```

- 配置 Carbon  
新建 `/etc/graphite-api.yaml`

```
search_index: /var/lib/graphite/index
finders:
  - graphite_api.finders.whisper.WhisperFinder
functions:
  - graphite_api.functions.SeriesFunctions
  - graphite_api.functions.PieFunctions
whisper:
  directories:
    - /var/lib/graphite/whisper
carbon:
  hosts:
    - 127.0.0.1:7002
  timeout: 1
  retry_delay: 15
  carbon_prefix: carbon
  replication_factor: 1
```

### 使用 Apache2 部署 Graphite-API

- 安装 mod-wsgi

```
apt-get install libapache2-mod-wsgi
```

- 新建 `/var/www/wsgi-scripts/graphite-api.wsgi`

```
# /var/www/wsgi-scripts/graphite-api.wsgi

from graphite_api.app import app as application
```

- 新建 `/etc/apache2/sites-available/graphite.conf`

```
# /etc/apache2/sites-available/graphite.conf
LoadModule wsgi_module modules/mod_wsgi.so
WSGISocketPrefix /var/run/wsgi
Listen 8013
<VirtualHost *:8013>

 WSGIDaemonProcess graphite-api processes=5 threads=5 display-name='%{GROUP}' inactivity-timeout=120
 WSGIProcessGroup graphite-api
 WSGIApplicationGroup %{GLOBAL}
 WSGIImportScript /var/www/wsgi-scripts/graphite-api.wsgi process-group=graphite-api application-group=%{GLOBAL}

 WSGIScriptAlias / /var/www/wsgi-scripts/graphite-api.wsgi

 <Directory /var/www/wsgi-scripts/>
 Order deny,allow
 Allow from all
 </Directory>
 </VirtualHost>
```

- 软链接

```
ln -s ../sites-available/graphite.conf .
```

- 重启 Apache

```
service apache2 restart
```

## 0x02 部署 Grafana

新坑待填

## 0x03 后端编写

新坑待填

## 0x04 前端编写

新坑待填

## 参考资料

1. [安装 Carbon 和 Graphite-API](https://markinbristol.wordpress.com/2015/09/20/setting-up-graphite-api-grafana-on-a-raspberry-pi/)  
2. [Grafana 文档](https://grafana.com/docs/)  
3. [Graphite 文档](https://graphite.readthedocs.io/en/latest/overview.html)  
4. [Graphite-API 文档](https://graphite-api.readthedocs.io/en/latest/)  
5. [TinyDB 文档](https://tinydb.readthedocs.io/en/latest/)  
6. [Flask 文档](https://flask.palletsprojects.com/en/2.1.x/)  
7. [Python screepsapi 模块仓库及其文档](https://github.com/screepers/python-screeps)
