# jelastic-autofs

### Build RPM packages
Build docker images

for Centos7:
```sh
 $ docker build --build-arg TAG=7 -t autofs:c7 -f Dockerfile-centos .
```
for Centos6:
```sh
 $ docker build --build-arg TAG=6 -t autofs:c6 -f Dockerfile-centos .
```
```sh
 $ docker run --rm -v YOUR_PATH:/mnt  autofs:c7
 $ docker run --rm -v YOUR_PATH:/mnt  autofs:c6
```
in YOUR_PATH you'll get rpm and src.rpm packages
