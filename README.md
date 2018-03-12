OpenStack Swift middleware to get SLO md5 hash
===========================================

Idea
==========
```
  Client  --> GET slo object with  -->
            `multipart-manifest=get` |
         <-- Proxy ( slo-hash mw ) <--
         |  Gen md5 base on manifest
         --> POST update slo metadata
```
When `slo_hash` middleware in proxy pipeline
Client can use same with to query slo manifest
to trigger get  ...
  1. **get slo md5 sum** base on slo manifest.
  2. **add it into slo manifest** as extra metadata. e.g:`X-Object-Meta-SLOmd5:xxx`.

How Could I test it or work on development ?
====================

1. Setup PACO (Swift All in One) docker container
---------------------------
`docker` is a easy way for you to run a quick test.

You can run VM or virtualbox when you doing the test.
`test/docker.sh` is the shell script as a reference for you to quick setup your docker environment.
```
#!/bin/bash
HOME="/home/ubuntu"
echo $HOME
sudo apt-get update -y
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common python-swiftclient
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
echo "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee -a /etc/apt/sources.list.d/docker-ce.list
sudo apt-get update -y
sudo apt-get install -y docker-ce
sudo systemctl start docker
sudo systemctl enable docker
sudo curl -L https://github.com/docker/compose/releases/download/1.19.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo docker-compose --version
sudo usermod -a -G docker $USER
```

You could use the docker file to do unit test under `test/paco` folder to build your own test environment.
```
$ cd ./test/paco
$ docker build -t="swift-paco:pike-slohash" -f Dockerfile.ubuntu1604 .
```
Or you can pull image directly from swiftstack docker hub.
```
$ docker pull swiftstack/swift-paco:pike-slohash
```
Then docker run or docker exec
```
$ docker run -i -t -d --net=host --hostname="paco_test" --name="paco_test" -v /srv/node/sdb1:/srv/node/sdb1:rw swift-paco:pike-slohash
$ docker exec -it paco_test /usr/local/bin/start.sh ( option, if your docker container paco_test is not running )
```

**PS**: if you want to jump into your paco docker container you can try
```
$ docker exec -it paco-test /bin/bash
```

2. Setup slo_hash middleware
---------------------
The middleware can be installed in a fashion similar to all other OpenStack
Swift middleware. Specifically, you need to install the python package on the
proxy node and add it to the pipeline.

Regarding above section, the way to jump into docker container is 
```
$ docker exec -it paco-test /bin/bash
```

Until a version of this middleware is published on PyPI (or elsewhere), the best
bet is to build it from source:
```
<virtualenv>/bin/python setup.py sdist
```

This will create a source tarball in `dist`.

Upload the tarball to the server and install with:
```
pip install slo_hash-0.0.1.linux-x86_64.tar.gz
```

**NOTE**: on some distributions the installed middleware may not be readable in
the installed directory (e.g. `/usr/local/lib/python<version>/dist-packages`)
and you'll need to make sure it is world-readable.

After this, add the middleware to your Swift pipeline in the proxy file. The
filter entry does not require any parameters. For example, the entry may look
like this:

```
[pipeline]
pipeline = slo_hash proxy-server

[filter:slo_hash]
use = egg:slo_hash#slo_hash
```

**PS**: `make.sh` is a example script to help you understand the deployment and tace it.
```
# cat ./make.sh
#python setup.py install
python ./setup.py sdist
pip install ./dist/slo_hash-0.0.1.tar.gz --upgrade
swift-init proxy-server restart
tail -f /var/log/swift/proxy_access.log
```

exit from docker container is just `$ exit`

3. Try Integration Test 
-----------------------
After you update the code you can try `./test/integration_test.sh`. The result should looks as below.
However, the `integration_test.sh` use python-swiftclient, then you might need to install it on your docker host.
e.g
```
pip install python-swiftclient
```
**PS**: run `./test/integration_test.sh` in your docker host VM
```
===check md5sum for bbb_sunflower_1080_2min.mp4
ee54e072da4a66478a187ba834a0d56a
===preparation create slo and slo_segments containers===
===upload test slo 3 segments object===
bbb_sunflower_1080_2min_001.mp4
bbb_sunflower_1080_2min_002.mp4
bbb_sunflower_1080_2min_003.mp4
===get token===
AUTH_tkb372465c2d7347f7b528aa560b04b01d
===upload test slo manifest object===
*   Trying 127.0.0.1...
* Connected to 127.0.0.1 (127.0.0.1) port 8080 (#0)
> PUT /v1/AUTH_test/slo/bbb_sunflower_1080_2min.mp4?multipart-manifest=put HTTP/1.1
> Host: 127.0.0.1:8080
> User-Agent: curl/7.47.0
> Accept: */*
> X-Auth-Token: AUTH_tkb372465c2d7347f7b528aa560b04b01d
> Content-Length: 360
> Content-Type: application/x-www-form-urlencoded
>
* upload completely sent off: 360 out of 360 bytes
< HTTP/1.1 201 Created
< Last-Modified: Mon, 12 Mar 2018 21:30:44 GMT
< Content-Length: 0
< Etag: "215729ecb16ddc52e240f10d04b7751d"
< Content-Type: text/html; charset=UTF-8
< X-Trans-Id: txc0b77dae30234fcda126e-005aa6f183
< X-Openstack-Request-Id: txc0b77dae30234fcda126e-005aa6f183
< Date: Mon, 12 Mar 2018 21:30:43 GMT
<
* Connection #0 to host 127.0.0.1 left intact
===check metadata no X-Object-Meta-Slomd5===
                   URL: http://127.0.0.1:8080/v1/AUTH_test/slo/bbb_sunflower_1080_2min.mp4
            Auth Token: AUTH_tkb372465c2d7347f7b528aa560b04b01d
               Account: AUTH_test
             Container: slo
                Object: bbb_sunflower_1080_2min.mp4
          Content Type: application/x-www-form-urlencoded
        Content Length: 27883167
         Last Modified: Mon, 12 Mar 2018 21:30:44 GMT
                  ETag: "215729ecb16ddc52e240f10d04b7751d"
         Accept-Ranges: bytes
           X-Timestamp: 1520890243.62172
            X-Trans-Id: tx8e29a22ad84d4212be842-005aa6f184
 X-Static-Large-Object: True
X-Openstack-Request-Id: tx8e29a22ad84d4212be842-005aa6f184
***===trigger slomd5 via GET and ?multipart-manifest=get===***
Note: Unnecessary use of -X or --request, GET is already inferred.
*   Trying 127.0.0.1...
* Connected to 127.0.0.1 (127.0.0.1) port 8080 (#0)
> GET /v1/AUTH_test/slo/bbb_sunflower_1080_2min.mp4?multipart-manifest=get HTTP/1.1
> Host: 127.0.0.1:8080
> User-Agent: curl/7.47.0
> Accept: */*
> X-Auth-Token: AUTH_tkb372465c2d7347f7b528aa560b04b01d
>
< HTTP/1.1 200 OK
< Content-Length: 593
< Etag: 758c7941293359d8fc425e34781d7746
< Accept-Ranges: bytes
< Last-Modified: Mon, 12 Mar 2018 21:30:45 GMT
< X-Object-Meta-Slomd5: ee54e072da4a66478a187ba834a0d56a
< X-Timestamp: 1520890244.37217
< X-Static-Large-Object: True
< Content-Type: application/json; charset=utf-8
< X-Trans-Id: tx23e4997af0a94ba1a4797-005aa6f184
< X-Openstack-Request-Id: tx23e4997af0a94ba1a4797-005aa6f184
< Date: Mon, 12 Mar 2018 21:30:44 GMT
<
* Connection #0 to host 127.0.0.1 left intact
[{"hash": "07b81cd438af5097d584321ab99cdc06", "last_modified": "2018-03-12T21:30:41.000000", "bytes": 10485760, "name": "/slo_segments/bbb_sunflower_1080_2min_001.mp4", "content_type": "video/mp4"}, {"hash": "ff53521cfdfe801ab1e52d0e7fda4969", "last_modified": "2018-03-12T21:30:42.000000", "bytes": 10485760, "name": "/slo_segments/bbb_sunflower_1080_2min_002.mp4", "content_type": "video/mp4"}, {"hash": "e924eaf1e2171ff355c588fa84da5778", "last_modified": "2018-03-12T21:30:43.000000", "bytes": 6911647, "name": "/slo_segments/bbb_sunflower_1080_2min_003.mp4", "content_type": "video/mp4"}]\n
===check metadata again , has X-Object-Meta-Slomd5===
                   URL: http://127.0.0.1:8080/v1/AUTH_test/slo/bbb_sunflower_1080_2min.mp4
            Auth Token: AUTH_tkb372465c2d7347f7b528aa560b04b01d
               Account: AUTH_test
             Container: slo
                Object: bbb_sunflower_1080_2min.mp4
          Content Type: application/x-www-form-urlencoded
        Content Length: 27883167
         Last Modified: Mon, 12 Mar 2018 21:30:45 GMT
                  ETag: "215729ecb16ddc52e240f10d04b7751d"
           Meta Slomd5: ee54e072da4a66478a187ba834a0d56a
         Accept-Ranges: bytes
           X-Timestamp: 1520890244.37217
            X-Trans-Id: tx10d1de24178146a9b2937-005aa6f184
 X-Static-Large-Object: True
X-Openstack-Request-Id: tx10d1de24178146a9b2937-005aa6f184
===get Slomd5===
ee54e072da4a66478a187ba834a0d56a
===regression test for list the object by account===
dlo
slo
slo_segments
test
test_segments
===regression test for list the objects in slo container===
bbb_sunflower_1080_2min.mp4
===regression test for download the object to name bbb_sunflower_1080_2min.mp4.download===
bbb_sunflower_1080_2min.mp4 [auth 0.014s, headers 0.107s, total 0.703s, 40.453 MB/s]
===check md5sum for bbb_sunflower_1080_2min.mp4.download===
ee54e072da4a66478a187ba834a0d56a
===delete the object - wipeout manifest and segments objects===
bbb_sunflower_1080_2min.mp4
===delete download object===
===                                         sum of result                                             ===
===         before md5           vs            meta md5              vs          after md5            ===
---------------------------------------------------------------------------------------------------------
ee54e072da4a66478a187ba834a0d56a vs ee54e072da4a66478a187ba834a0d56a vs ee54e072da4a66478a187ba834a0d56a
```

**PS**: please check closely `Meta Slomd5: ee54e072da4a66478a187ba834a0d56a` for python swiftclient or `X-Object-Meta-Slomd5: ee54e072da4a66478a187ba834a0d56a` for curl command in above example. It's md5sum of testing mp4 file
