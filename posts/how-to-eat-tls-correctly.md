## 开端

我看到 SuperMain 写了一篇《如何给你的网站部署一张 SSL 证书》。
但是，我**因此骂了他一顿**。为什么要骂他？  
> 这个标准正在推行  
就意味着还没好  
还没能像 HTML 成为标准  
再没成为标准之前  
我基本上都不知道（  
在写这篇文章之前  
我甚至不知道这玩意

因此，我打算写一篇如何正确部署 TLS 证书的文章，来堵住他的嘴。  

## 理论基础

### 1. `TLS` 是什么

> 传输层安全性协议（英语：Transport Layer Security，缩写：TLS）及其前身安全套接层（英语：Secure Sockets Layer，缩写：SSL）是一种安全协议，目的是为互联网通信提供安全及数据完整性保障。

TLS 的整个过程如下：

1. 客户端向服务器端索要并验证公钥。
2. 双方协商生成"对话密钥"。
3. 双方采用"对话密钥"进行加密通信。

TLS 的握手过程如下：

1. 当客户端连接到支持 TLS 协议的服务器要求创建安全连接并列出了受支持的密码包（包括加密算法、散列算法等），握手开始。
2. 服务器从该列表中决定密码包，并通知客户端。
3. 服务器发回其数字证书，此证书通常包含服务器的名称、受信任的证书颁发机构（CA）和服务器的公钥。
4. 客户端确认其颁发的证书的有效性。
5. 为了生成会话密钥用于安全连接，客户端使用服务器的公钥加密随机生成的密钥，并将其发送到服务器，只有服务器才能使用自己的私钥解密。
6. 利用随机数，双方生成用于加密和解密的对称密钥。这就是 TLS 协议的握手，握手完毕后的连接是安全的，直到连接（被）关闭。如果上述任何一个步骤失败，TLS 握手过程就会失败，并且断开所有的连接。

[SSL/TLS 协议运行机制的概述 - 阮一峰](https://www.ruanyifeng.com/blog/2014/02/ssl_tls.html) 这篇文章详细而简洁易懂地介绍了这部分内容，如果您想要了解更多，可以点击链接前往查看。

### 2. 我们为什么需要 `TLS`

TLS 有以下优点：

1. 所有信息都是加密传播，第三方无法窃听。
2. 具有校验机制，一旦被篡改，通信双方会立刻发现。
3. 配备身份证书，防止身份被冒充。

### 3. 证书从哪里来

证书要从哪里来？  
我们穷人直接用 [Let's Encrypt](https://letsencrypt.org/zh-cn/) 就行了。  
> Let’s Encrypt 是一家免费、开放、自动化的证书颁发机构（CA），为公众的利益而运行。 它是一项由 Internet Security Research Group (ISRG) 提供的服务。  
我们以尽可能对用户友好的方式免费提供为网站启用 HTTPS（SSL/TLS）所需的数字证书。 这是因为我们想要创建一个更安全，更尊重隐私的 Web 环境。  
我们在努力让所有人体验到一个更加安全、尊重隐私的 Web 环境。我们让获取 HTTPS 证书变得十分方便，因为易用性对于其推广至关重要。我们免费提供证书，因为证书费用可能会阻止一部分站长使用 HTTPS。我们的证书在世界上每个国家都可使用，因为安全的 Web 不是部分人的专属品。我们尽力做到公开、透明，因为这些价值对于信任至关重要。 ————Let‘s Encrypt 官网

这玩意有几个显著的优点：

1. **永久免费**
2. 借助工具可以实现自动续期，如果可以通过 API 修改 DNS，还可以使用通配符证书而不需要每个子域名都申请一遍证书

申请指南可以参考 `实战操作` 部分。

### 4. 并不神奇的 `HSTS`

> HTTP Strict Transport Security（通常简称为 HSTS）是一个安全功能，它告诉浏览器只能通过 HTTPS 访问当前资源，而不是 HTTP。 ————MDN

简略地来说，HSTS 就是在浏览器连接到网站时返回一个 `Strict-Transport-Security` 头，这告诉浏览器在指定时间内必须使用 HTTPS 访问此网站而禁止使用明文 HTTP。

### 5. 神奇的 `HSTS Preload List`

前面说到，HSTS 需要在第一次连接到网站的时候返回指定的头。这样做的前提是 `第一次成功连接到网站`，所以如果第一次就连接到攻击者的网站，还是无法避免被篡改。
而为了解决这个问题，就有了 `HSTS Preload List`。这的本质就是一个巨大的表，跟随着操作系统和浏览器的版本更新而更新。

## 实战操作

首先需要有 3 个文件：

1. 证书（.crt 格式）
2. 私钥（.key 格式）
3. 证书链（.crt 格式）（可选）

证书和私钥是必须的，而证书链是可选的。但是如果您没有证书链文件，建议您使用 [MySSL.com 提供的证书链下载／证书链修复工具](https://myssl.com/chain_download.html) 上传您的证书来下载证书链。这是因为在您的证书和跟证书直接可能会有其他证书，如果您不提供证书链，就需要浏览器下载证书链上的中间证书。

### 对于 Apache 用户

1. 启用 `*:443` 端口
2. 修改配置文件  

```
SSLCertificateFile      /path/to/your/certificate.crt
SSLCertificateKeyFile   /path/to/your/private/key.key
SSLCertificateChainFile /path/to/your/certificate/chain.crt
SSLProtocol  all -SSLv2 -SSLv3
SSLCipherSuite ECDH:AESGCM:HIGH:!RC4:!DH:!MD5:!aNULL:!eNULL
SSLHonorCipherOrder on
```

3. 启用 HSTS

```
a2enmod headers
```

然后在 `<VirtualHost>` 中加入

```
Header always set Strict-Transport-Security "max-age=63072000; includeSubdomains; preload"
```

### 对于 Nginx 用户

1. `listen 443;`
2. 在 `server {}` 内添加：

```
ssl on;
ssl_certificate     /usr/local/nginx/cert/ssl.pem;  # pem 或 crt 文件的路径
ssl_certificate_key  /usr/local/nginx/cert/ssl.key; # key 文件的路径
ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
ssl_prefer_server_ciphers on;
ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE:ECDH:AES:HIGH:!NULL:!aNULL:!MD5:!ADH:!RC4;
```

3. 启用 HSTS

```
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### 申请 HSTS Preload

直接前往 [HSTSPreload 网站申请](https://hstspreload.org/)。

### 查询 HSTS Preload

直接前往 [Chromium 网站](https://source.chromium.org/chromium/chromium/src/+/main:net/http/transport_security_state_static.json) 搜索。  
当然，加入到了 HSTS Preload List 后，你可能还需要等待 1-2 月，待新版本的 Chrome 和 Chromium、Firefox、IE 等发布后，你的域名算是正式被各大浏览器承认并强制使用 Https 访问了，你可以在 Chrome 浏览器的地址框中输入`chrome://net-internals/#hsts`查看。

### 番外：取消 HSTS Preload 请求

直接前往 [HSTSPreload Removal 网站申请](https://hstspreload.org/removal/)。
