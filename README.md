# autofs

### Build RPM packages
Build docker images

for Centos7:
```sh
 $ docker build --build-arg TAG=7 -t autofs:c7 -f Dockerfile-centos .
```
for Centos8:
```sh
 $ docker build --build-arg TAG=8 -t autofs:c8 -f Dockerfile-centos .
```
```sh
 $ docker run --rm -v YOUR_PATH:/mnt  autofs:c7
 $ docker run --rm -v YOUR_PATH:/mnt  autofs:c8
```
for  Ubuntu/Debian
```sh
 $ docker build --build-arg AUTOFS_VERSION=5.1.8 -t autofs:ubuntu -f Dockerfile-ubuntu .
 $ docker run -v /home/dimkapc/work/jelastic-autofs/rpm:/mnt  autofs:ubuntu
```
in YOUR_PATH you'll get rpm and src.rpm packages
