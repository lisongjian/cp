## 网页网赚
修改package deer的版本号
然后运行grunt deploy


### PIL安装
```
wget http://effbot.org/media/downloads/PIL-1.1.7.tar.gz
tar -zxvf PIL-1.1.7.tar.gz
```
先查看README再安装
```
sudo apt-get install zlib1g-dev
sudo apt-get install libfreetype6-dev
```
修改 setup.py 
```
FREETYPE_ROOT = "/usr/lib/x86_64-linux-gnu/", "/usr/include/freetype/"
ln -s /usr/include/freetype2/ /usr/include/freetype/
python setup.py build_ext -i
```
查看系统中图像库是否存在
```
PIL 1.1.7 SETUP SUMMARY
--------------------------------------------------------------------
version       1.1.7
platform      linux2 2.7.6 (default, Mar 22 2014, 22:59:56)
              [GCC 4.8.2]
--------------------------------------------------------------------
*** TKINTER support not available
*** JPEG support not available
*** ZLIB (PNG/ZIP) support available
*** FREETYPE2 support available
*** LITTLECMS support not available
--------------------------------------------------------------------
```

