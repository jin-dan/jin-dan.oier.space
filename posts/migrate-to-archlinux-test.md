## 前言

本文只适用于 UEFI 引导。  
本文适用于从 Windows 迁移到 Archlinux。  
作者不保证本文中的方法可以在您的计算机上使用。  
本文使用 [Creative Commons 署名 - 非商业性使用 - 相同方式共享 4.0 国际 (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh) 协议共享。  
如果文章内容有误，恳请各位指出，感谢。

## 目录

0x00 前情提要

0x01 备份数据

0x02 制作安装盘

- 下载镜像
- 写入 U 盘

0x03 安装系统

- 从 U 盘启动
- 连接 Wi-Fi（有线用户直接跳过）
- 同步 pacman
- 硬盘分区
- 格式化
- 挂载分区
- 安装系统
- 配置引导
- 退出新系统并取消挂载

0x04 配置系统

0x05 KDE 配置

- Fctix5+Rime

0x06 软件相关

- 软件快速参考
- 使用 AUR (Arch User Repository)
  - 安装 yay
  - 使用 yay 进行包的安装
- 使用 wine 运行 windows 应用
- 使用 winapps 运行 windows 应用
- 创建 windows 虚拟机

0x07 系统美化

- GRUB 美化
- SDDM 美化
- KDE 美化
  - 插件

0x08 附录

- yay 的使用方法

0x09 参考资料

---

## 0x00 前情提要

作者的电脑有 1 块 512GB 大小的 NVMe 固态硬盘，同时有一块 2TB 大小的西部数据黑盘移动（机械）硬盘，所以作者需要先把 windows 分区克隆到移动硬盘上，然后全部格式化进行 archlinux 安装

## 0x01 备份数据

使用 [微 PE](https://www.wepe.com.cn/) 和 [DiskGenius](https://www.diskgenius.cn/) 工具进行数据备份和分区克隆  
由于在 PE 环境下您可能无法进行网课/刷题等操作，所以我们可以先使用 DiskGenius 的分区镜像功能把分区镜像保存到移动硬盘上，再回到 windows 系统使用 DeskGenius 把分区镜像还原到移动硬盘上（这是因为分区镜像是 4K/顺序读顺序写操作，而分区还原是顺序读 4K/顺序写操作，固态硬盘的小文件读写速度显著大于机械硬盘）

1. 制作 wepe 环境  
[微 PE 下载连接](https://www.aliyundrive.com/s/2XrrMYJU2gi)  
~~作者是在 arch 下写的没法演示了建议自己去找教程~~  
2. 进入 wepe 环境，使用 DiskGenius 进行磁盘镜像操作  
~~作者是在 arch 下写的没法演示了建议自己去找教程~~  
3. 回到 windows 环境恢复硬盘  
~~作者是在 arch 下写的没法演示了建议自己去找教程~~  
此处注意，恢复完成后硬盘将会脱机，需要打开 `计算机 -> 管理 -> 磁盘管理` ，右击移动硬盘点击 `联机`，硬盘管理将会重新为分区分配序列号。

## 0x02 制作安装盘

### 下载镜像

首先下载 ISO 镜像：[官方下载链接](https://archlinux.org/download/)，建议翻到下面找中国的镜像进行下载。

### 写入 U 盘

然后写入 U 盘，建议使用 [Rufus](https://rufus.ie/zh/) 工具，分区类型选择 GPT 而非默认的 MBR ，写入方式为 DD 而非 ISO。

## 0x03 安装系统

### 连接 Wi-Fi（有线用户直接跳过）

1. 输入 `iwctl` 进入 iwd 命令行
2. 输入 `device list` 查看无线网卡设备
3. 假设无线网卡为 `wlan0` ，则输入 `station wlan0 scan` 扫描网络
4. 输入 `station wlan0 get-networks` 查看扫描到的网络
5. 假设要连接网络的 SSID 为 `114514` 则输入 `station wlan0 connect 114514` 如果有密码，则输入密码。
6. 输入 `exit` 退出 iwd 命令行

### 同步 pacman

输入下列语句，这将自动选出最快的镜像源并替换

```
reflector -c China --sort rate --save /etc/pacman.d/mirrorlist
```

完成后输入 `pacman -Syyy` 同步 pacman 源（如下图）
![图 1](https://cdn.luogu.com.cn/upload/image_hosting/641fquep.png)

### 分区格式化

假设分区为 `nvme0n1p2`，输入下列命令

```
mkfs.ext4 /dev/nvme0n1p2
```

### 挂载分区

1. 把要安装系统的分区挂载到 `/mnt`

```
mount /dev/nvme0n1p2 /mnt
```

2. 创建 `/mnt/boot` 文件夹

```
mkdir /mnt/boot
```

3. 把 EFI 分区挂载到 `/mnt/boot`，假设 EFI 分区为 `nvme0n1p1`

```
mount /dev/nvme0n1p1 /mnt/boot
```

### 安装系统

1. 执行下列命令安装基本系统

```
pacstrap /mnt base linux linux-firmware nano
```

2. 生成 fstab 文件

```
genfstab -U /mnt >> /mnt/etc/fstab
```

3. 切换到安装好的系统

```
arch-chroot /mnt
```

4. 建立 swapfile

```
dd if=/dev/zero of=/swapfile bs=2048 count=1048576 status=progress # 创建 swapfile
chmod 600 /swapfile # 改权限
mkswap /swapfile # 建立 swap
swapon /swapfile # 激活 swap
```

5. 修改 fstab 以支持 swapfile  
输入 `nano /etc/fstab`，在文件末尾添加 `/swapfile none swap defaults 0 0`，然后按顺序按 `Ctrl+O Enter Ctrl+X` 保存退出
6. 设置时区

```
ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
```

7. 同步硬件时钟

```
hwclock --systohc
```

8. 设置 locale，输入 `nano /etc/locale.gen`，按 `Ctrl+W` 再输入 `#en_US` `回车` 找到 UTF-8，`删除井号` 取消注释，然后再 `Ctrl+W` 搜索 `#zh_CN` `回车` 找到 UTF-8，`删除井号` 取消注释，然后按顺序按 `Ctrl+O Enter Ctrl+X` 保存退出
9. 生成 locale

```
locale-gen
```

10. 创建并写入 `/etc/locale.conf` 文件  
输入 `nano /etc/locale.conf`，填入 `LANG=en_US.UTF-8`，然后按顺序按 `Ctrl+O Enter Ctrl+X` 保存退出
11. 创建并写入 hostname  
输入 `nano /etc/hostname`，填入 你要使用的 hostname（如 `jindan`），然后按顺序按 `Ctrl+O Enter Ctrl+X` 保存退出
11. 写入 hosts  
输入 `nano /etc/hosts`，写入的内容如图，然后按顺序按 `Ctrl+O Enter Ctrl+X` 保存退出（暂时使用知乎大佬的图片，文章见结尾参考资料部分）
![](https://cdn.luogu.com.cn/upload/image_hosting/f5lpxefm.png)
13. 为 root 用户创建密码

```
passwd
```

然后输入并确认密码（linux 终端的密码没有回显，输完直接回车就好）

### 配置引导

1. 安装 GRUB 包和其他需要的包

```
pacman -S grub efibootmgr networkmanager network-manager-applet dialog wireless_tools wpa_supplicant os-prober mtools dosfstools ntfs-3g base-devel linux-headers reflector git sudo
```

2. 安装微码
如果是 Intel 的 CPU，需要安装 Intel 的微码文件

```
pacman -S intel-ucode
```

如果是 AMD 的 CPU，需要安装 AMD 的微码文件

```
pacman -S amd-ucode
```

3. 如果你还有其他的系统需要引导（尤其是 Windows），需要启用 OS Prober 来自动检测其他系统  
输入 `nano /etc/default/grub` 进入 nano，在最后输入 `GRUB_DISABLE_OS_PROBER=false`，然后按顺序按 `Ctrl+O Enter Ctrl+X` 保存退出
4.. 安装 GRUB

```
grub-install --target=x86_64-efi --efi-directory=/boot --bootloader-id=Arch
grub-mkconfig -o /boot/grub/grub.cfg
```

### 退出新系统并取消挂载

```
exit
umount -a
reboot
```

## 0x04 配置系统

1. 启动网络服务

```
systemctl enable --now NetworkManager
```

2. 连接 Wi-Fi（有线用户直接跳过）

```
nmtui
```

3. 新建用户并授权
假设用户名为 `jindan`，则输入

```
useradd -m -G wheel jindan
```

4. 为新用户设置密码

```
passwd jindan
```

输入并确认密码
5. 授权
输入 `EDITOR=nano visudo` 进入 nano，`Ctrl+W` 输入 `# %wheel` `回车`，`删除井号` 取消注释，然后按顺序按 `Ctrl+O Enter Ctrl+X` 保存退出
6. 安装显卡驱动
安装 AMD 显卡驱动：

```
pacman -S xf86-video-amdgpu
```

安装 NVIDIA 显卡驱动：

```
pacman -S nvidia nvidia-utils
```

7. 安装 Display Server（xorg）

```
pacman -S xorg
```

8. 安装 Display Manager
Gnome：

```
pacman -S gdm
```

KDE：

```
pacman -S sddm
```

Xfce / DDE：

```
pacman -S lightdm lightdm-gtk-greeter
```

9. 设置开机自启，假设安装的是 KDE (`sddm`)

```
systemctl enable sddm
```

10. 安装 Desktop Environment
Gnome：

```
pacman -S gnome
```

KDE：

```
pacman -S plasma kde-applications packagekit-qt5
```

Xfce：

```
pacman -S xfce4 xfce4-goodies
```

DDE：

```
pacman -S deepin deepin-extra
```

11. 添加 archlinuxcn 源
输入 `nano /etc/pacman.conf`，写入的内容如下代码框，并 `取消对 multilib 源的注释`，然后按顺序按 `Ctrl+O Enter Ctrl+X` 保存退出

```
## 阿里云 (Global CDN) (ipv4, ipv6, http, https)
## Added: 2020-07-03
[archlinuxcn]
Server = https://mirrors.aliyun.com/archlinuxcn/$arch
```

12. 同步 pacman 源并安装 keyring

```
pacman -Syu && pacman -S archlinuxcn-keyring
```

13. 安装字体

```
pacman -S ttf-sarasa-gothic noto-fonts-cjk
```

14. 重启

```
reboot
```

## 0x05 KDE 配置

### Fcitx5+Rime

> Fcitx5 是继 Fcitx 后的新一代输入法框架。

> Rime（中州韻輸入法引擎）是一款支持多种输入方案的输入法引擎。

Rime 本身并不提供用于处理用户输入的前端，需要和输入法框架配合才能使用，比如 Fcitx5 (简体中文) 或 IBus (简体中文)。

1. 输入下列命令安装

```
sudo su
pacman -S fcitx5-im
echo "GTK_IM_MODULE=fcitx" >> /etc/environment
echo "QT_IM_MODULE=fcitx" >> /etc/environment
echo "XMODIFIERS=@im=fcitx" >> /etc/environment
echo "INPUT_METHOD=fcitx" >> /etc/environment
echo "SDL_IM_MODULE=fcitx" >> /etc/environment
cp /usr/share/applications/org.fcitx.Fcitx5.desktop ~/.config/autostart/
pacman -S fcitx5-rime
exit
```

安装后可能需要重启  
2. 添加输入法  
![](https://cdn.luogu.com.cn/upload/image_hosting/oxdzu4d7.png)  
![](https://cdn.luogu.com.cn/upload/image_hosting/q2xky5av.png)  
4.  设置成简体中文  
![](https://cdn.luogu.com.cn/upload/image_hosting/6iaoq5py.png)  

## 0x06 软件相关

A 全部功能均可使用  
X 不可使用  
/ 未测试  
注：AUR 中的 deepin-wine 包也算作 `原生/AUR` 类别  
| 名称 | 原生/AUR | Wine | WinApps |
| :------------: | :------------: | :------------: | :------------: |
| 微信 | X | / | / |
| QQ | A | / | / |
| 钉钉 | 不能进行会议 | / | / |
| Microsoft Office | X | / | A |

### 使用 AUR (Arch User Repository)

> Arch 用户软件仓库（Arch User Repository，AUR）是为用户而建、由用户主导的 Arch 软件仓库。AUR 中的软件包以软件包生成脚本（PKGBUILD）的形式提供，用户自己通过 makepkg 生成包，再由 pacman 安装。创建 AUR 的初衷是方便用户维护和分享新软件包，并由官方定期从中挑选软件包进入 community 仓库。

当您要安装任何软件时，您可以首先前往 [AUR 官网](https://aur.archlinux.org/) 查询是否有您需要的软件，如果有，就可以直接使用 yay 进行安装，yay 的安装和使用方法见下文

#### 安装 yay

yay 是用于快速安装 aur 包的工具

1. 安装 git

```
sudo pacman -S git
```

2. 克隆 yay 仓库

```
git clone https://aur.archlinux.org/yay.git
```

3. 构建并安装

```
cd yay
makepkg -si
```

#### 使用 yay 进行包的安装

输入 `yay -S <包名>` 即可，如果询问是否显示差异则输入 `n` 回车忽略，否则输入 `y` 回车确认即可
更多信息情参见 `附录` 章节内的 `yay 的使用方法`

### 创建 windows 虚拟机

1. 安装 KVM 和 Virtual Machine Manager

```
pacman -S virt-manager
```

2. 下载 Windows 10 ISO 和 virtio 驱动
Windows 10 ISO：[https://www.microsoft.com/en-us/software-download/windows10ISO](https://www.microsoft.com/en-us/software-download/windows10ISO)（Windows 11 亦可）
VirtIO 驱动：[https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/stable-virtio/virtio-win.iso](https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/stable-virtio/virtio-win.iso)
3. 打开 `虚拟系统管理器`  
![](https://cdn.luogu.com.cn/upload/image_hosting/5wgnjyck.png)
然后点击 `编辑 -> Preferences`，启用 `启用 XML 编辑`（如图）
![](https://cdn.luogu.com.cn/upload/image_hosting/1d9s6n4n.png)
4. 点击 `文件 -> 添加连接`，确保和图片的设置一样，点击 `连接` 即可  
![](https://cdn.luogu.com.cn/upload/image_hosting/8zdmgcbe.png)
5. 点击新建虚拟机  
![](https://cdn.luogu.com.cn/upload/image_hosting/rp2kzpk7.png)
6. 选择 `QEMU/KVM` 连接，点击 `Forward`（如图）
![](https://cdn.luogu.com.cn/upload/image_hosting/6lp4eh1j.png)
7. 选择镜像（如图）
![](https://cdn.luogu.com.cn/upload/image_hosting/3e4hrszg.png)
8. 设置内存和 CPU，建议为 4096MB，这其实是最大占用内存（作者太懒了直接用官方文档的图片了）
![](https://github.com/Fmstrat/winapps/raw/main/docs/kvm/05.png)
9. 选择您的虚拟磁盘大小，记住这是磁盘将增长到的最大大小，但它不会占用这个空间，直到它需要它  
![](https://github.com/Fmstrat/winapps/blob/main/docs/kvm/06.png)
10. 接下来，为您的机器命名，命名为 RDPWindows 以便 WinApps 可以检测到它，然后选择 Customize configuration before install  
![](https://github.com/Fmstrat/winapps/raw/main/docs/kvm/07.png)
11. 单击 Finish，确保在 CPU 下 Copy host CPU configuration 被选中，然后 Apply
12. 接下来，转到 `XML` 选项卡，然后编辑该 `<clock>` 部分以包含

```xml
<clock offset='localtime'>
  <timer name='hpet' present='yes'/>
  <timer name='hypervclock' present='yes'/>
</clock>
```

然后 Apply ，这将大大减少空闲 CPU 使用率（从 ~25% 到 ~3%）
然后你就可以启动系统进行一个正常的 Windows 安装了

## 0x07 系统美化

### GRUB 美化

1. 挑选喜欢的主题并下载
在 [Gnome-look](https://www.gnome-look.org/browse?cat=109&ord=latest) 网站可以找到 GRUB 主题，点击喜欢的主题进入主页，点击 `Files` ，选择对应的版本下载（如图）
![](https://cdn.luogu.com.cn/upload/image_hosting/ujyz130k.png)
2. 脚本安装
我选择的主题是 `Grub-theme-vimix`，`unzip` 解压后可以发现该主题带有一个 `install.sh` 脚本，可以使用脚本安装，输入

```
bash install.sh
```

3. 手动安装
等待补充

### sddm 美化

```
yay -S sddm-config-editor-git
yay -S archlinux-themes-sddm
```

然后搜索打开 `SDDM Configuration`，点击主题，进行主题更换，如果您使用的是 plasma 默认主题，可以使用 breeze（如图）
![](https://cdn.luogu.com.cn/upload/image_hosting/0f0btkbh.png)

### KDE 美化

#### 插件

- [Awesome Widget](https://store.kde.org/p/998913) 可以显示自定义的系统参数  
- [Weather Widget](https://store.kde.org/p/998917/) 会把天气以图标和表格两种形式展示出来  
- Global Menu 与 Application title 配合使用达到 MacOS 的效果，可以让界面更美观，操作更方便  
- [Panon](https://github.com/rbn42/panon) 音效可视化插件  
- [Event Calendar](https://store.kde.org/p/998901/) 快捷添加任务、显示天气、日期和节假日

## 0x08 附录

### yay 的使用方法

> 在使用 Arch 用户软件仓库时， AUR 工具可以自动完成某些任务：

- 搜索在 AUR 中发布的软件包
- 解析 AUR 软件包之间的依赖关系
- 下载 AUR 软件包
- 下载网站内容，例如用户评论
- 提交 AUR 软件包

> pacman 只会处理其仓库中预先构建好的软件包的更新。 AUR 软件包以 PKGBUILD 的形式再分发并需要 AUR helper 来自动化构建流程。然而请注意，即使软件包自身并没有更新，但由于某些库文件的更新，您可能仍需重新构建某些软件包。
不会为 AUR 软件包检查更新，所以一些工具也可以自动从 AUR 检查更新并再次构建新版本的软件包。请注意，即使软件包自身并没有更新，但由于某些库文件的更新，您可能仍需重新构建某些软件包。
                                                                                              💻  

#### 基本使用

```
yay -S <包名> # 在 AUR 中搜索包并安装
yay -Ss <包名> # 在 AUR 和 官方源 中搜索包并安装
yay -Si <包名> # 在 AUR 中获取包的信息
yay -U <包路径> # 安装本地包
yay -Pu # 检查更新
yay -Sy # 同步
yay -Syu # 更新系统
yay -Syua # 更新系统和已经安装的 AUR 软件包
yay -Yc # 删除不必要的依赖
yay -R <包名> # 删除包
yay -Rs <包名> # 删除包及其依赖
yay -Rnsc <包名> # 删除包、依赖和配置文件
```

## 0x09 参考资料

1. [ArchWiki：您的在线 Arch Linux 文档库](https://wiki.archlinux.org/title/Main_page)（官方 Wiki）
2. [2021 Archlinux 双系统安装教程（超详细）](https://zhuanlan.zhihu.com/p/138951848)（知乎）作者：ayamir  
3. [Linux Grub 引导界面（启动界面）美化](https://zhuanlan.zhihu.com/p/94331255)（知乎）作者：Kuari  
4. [KDE 美化之路](https://zhuanlan.zhihu.com/p/89847601)（知乎）作者：知乎用户 9g4W9C

作为 archlinux 小白在此对上述参考资料的作者表示由衷的感谢  
感谢 @Hello 报告错误  
