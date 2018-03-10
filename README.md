OpenStack Swift middleware to get SLO md5 hash
===========================================

How do I set this up?
---------------------

The middleware can be installed in a fashion similar to all other OpenStack
Swift middleware. Specifically, you need to install the python package on the
proxy node and add it to the pipeline.

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

How Could I test it?
----------------
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

After docker PACO container up and running, try the command line on your host maine as below.
```
ubuntu@docker:~/git$ curl -H 'X-Auth-Token: AUTH_tke383f71f6f324372bef38a6372c2d6ab' -v -X DELETE http://127.0.0.1:8080/v1/AUTH_test/slo/bbb_sunflower_1080_2min.mp4
*   Trying 127.0.0.1...
* Connected to 127.0.0.1 (127.0.0.1) port 8080 (#0)
> DELETE /v1/AUTH_test/slo/bbb_sunflower_1080_2min.mp4 HTTP/1.1
> Host: 127.0.0.1:8080
> User-Agent: curl/7.47.0
> Accept: */*
> X-Auth-Token: AUTH_tke383f71f6f324372bef38a6372c2d6ab
>
< HTTP/1.1 204 No Content
< Content-Length: 0
< Content-Type: text/html; charset=UTF-8
< X-Trans-Id: tx180bd73896c147329d5f2-005aa3406e
< X-Openstack-Request-Id: tx180bd73896c147329d5f2-005aa3406e
< Date: Sat, 10 Mar 2018 02:18:22 GMT
<
* Connection #0 to host 127.0.0.1 left intact
ubuntu@docker:~/git$ curl -H 'X-Auth-Token: AUTH_tke383f71f6f324372bef38a6372c2d6ab' -vv -X PUT http://127.0.0.1:8080/v1/AUTH_test/slo/bbb_sunflower_1080_2min.mp4?multipart-manifest=put -d '[{"path":"test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000000","etag":"d4cd1ebdd6ffd624c13442a3150ba648","size_bytes":1048576},{"path":"test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000001","etag":"39a8e52484fe541173cbd9c10f174798","size_bytes":1048576},{"path":"test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000002","etag":"5b9f6406ae96d5320fa156fd12f2436f","size_bytes":1048576},{"path":"test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000003","etag":"9975d30d2b6bfa51b2d8370555ac5080","size_bytes":1048576},{"path":"test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000004","etag":"f045ccb6f4051e421de7639bbb13e4b2","size_bytes":1048576},{"path":"test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000005","etag":"43f57e2e8a5ed9089812496cad72fdb1","size_bytes":1048576},{"path":"test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000006","etag":"8426f2c064c18df2c6fe37f7c3b0f047","size_bytes":1048576},{"path":"test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000007","etag":"e2abcbfe74aae58d0e408beb5097ce20","size_bytes":1048576},{"path":"test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000008","etag":"e3f497be28f16d8cd53698d40d438821","size_bytes":1048576},{"path":"test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000009","etag":"015f42efd59b9ffdd382f3e58fc66baf","size_bytes":1048576},{"path":"test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000010","etag":"b23d343e5af6b002b20892c77ba45685","size_bytes":1048576},{"path":"test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000011","etag":"6627b9f714f2f24120b45324d42f7eab","size_bytes":1048576},{"path":"test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000012","etag":"65df14fb47075c83ff0e51c9c95f335b","size_bytes":1048576},{"path":"test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000013","etag":"aac01f3ee2c8166e069972b386ab6334","size_bytes":1048576},{"path":"test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000014","etag":"482b33723dfa57235d8204ac5c5b60b2","size_bytes":1048576},{"path":"test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000015","etag":"a53ab1e24eabb5c08d6b5533b04fb112","size_bytes":1048576},{"path":"test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000016","etag":"6201980a66f777d041b287fe9b539d19","size_bytes":1048576},{"path":"test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000017","etag":"bb43e35e29364c25965fe34be119bd07","size_bytes":1048576},{"path":"test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000018","etag":"018ad2e30338737613d85c3e7c4a6130","size_bytes":1048576},{"path":"test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000019","etag":"637be930fee722f2cc1be414e24b5b29","size_bytes":1048576},{"path":"test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000020","etag":"176f1c056099d2c49ecea19c1e94c493","size_bytes":1048576},{"path":"test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000021","etag":"9d71937d63c2922c4bbade05a7058a5d","size_bytes":1048576},{"path":"test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000022","etag":"c43b28d7cb03280c49e0a6ef94c7a539","size_bytes":1048576},{"path":"test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000023","etag":"fd0d7b2d1a16aaa588bf37dc2ac1033f","size_bytes":1048576},{"path":"test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000024","etag":"91f8af59b779d85bfb48bf19dee8faae","size_bytes":1048576},{"path":"test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000025","etag":"217af21ad4ab9836c012f7e9b5763d96","size_bytes":1048576},{"path":"test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000026","etag":"85f1e02ddd35a5085cd724148b154c73","size_bytes":620191}]'
*   Trying 127.0.0.1...
* Connected to 127.0.0.1 (127.0.0.1) port 8080 (#0)
> PUT /v1/AUTH_test/slo/bbb_sunflower_1080_2min.mp4?multipart-manifest=put HTTP/1.1
> Host: 127.0.0.1:8080
> User-Agent: curl/7.47.0
> Accept: */*
> X-Auth-Token: AUTH_tke383f71f6f324372bef38a6372c2d6ab
> Content-Length: 4320
> Content-Type: application/x-www-form-urlencoded
> Expect: 100-continue
>
< HTTP/1.1 100 Continue
* We are completely uploaded and fine
< HTTP/1.1 201 Created
< Last-Modified: Sat, 10 Mar 2018 02:18:32 GMT
< Content-Length: 0
< Etag: "8b9a8a2c3a6573ecdfd2096303e44b42"
< Content-Type: text/html; charset=UTF-8
< X-Trans-Id: tx606df49946b2451c847aa-005aa34077
< X-Openstack-Request-Id: tx606df49946b2451c847aa-005aa34077
< Date: Sat, 10 Mar 2018 02:18:31 GMT
<
* Connection #0 to host 127.0.0.1 left intact
ubuntu@docker:~/git$ swift -A http://127.0.0.1:8080/auth/v1.0 -U test:tester -K testing stat -v slo bbb_sunflower_1080_2min.mp4
                   URL: http://127.0.0.1:8080/v1/AUTH_test/slo/bbb_sunflower_1080_2min.mp4
            Auth Token: AUTH_tke383f71f6f324372bef38a6372c2d6ab
               Account: AUTH_test
             Container: slo
                Object: bbb_sunflower_1080_2min.mp4
          Content Type: application/x-www-form-urlencoded
        Content Length: 27883167
         Last Modified: Sat, 10 Mar 2018 02:18:32 GMT
                  ETag: "8b9a8a2c3a6573ecdfd2096303e44b42"
         Accept-Ranges: bytes
           X-Timestamp: 1520648311.59085
            X-Trans-Id: tx0f18689fc89843e9955fc-005aa3407c
 X-Static-Large-Object: True
X-Openstack-Request-Id: tx0f18689fc89843e9955fc-005aa3407c
ubuntu@docker:~/git$ curl -H 'X-Auth-Token: AUTH_tke383f71f6f324372bef38a6372c2d6ab' -v -X GET http://127.0.0.1:8080/v1/AUTH_test/slo/bbb_sunflower_1080_2min.mp4?multipart-manifest=get
Note: Unnecessary use of -X or --request, GET is already inferred.
*   Trying 127.0.0.1...
* Connected to 127.0.0.1 (127.0.0.1) port 8080 (#0)
> GET /v1/AUTH_test/slo/bbb_sunflower_1080_2min.mp4?multipart-manifest=get HTTP/1.1
> Host: 127.0.0.1:8080
> User-Agent: curl/7.47.0
> Accept: */*
> X-Auth-Token: AUTH_tke383f71f6f324372bef38a6372c2d6ab
>
< HTTP/1.1 200 OK
< Content-Length: 6830
< Etag: 6e78a77f81de2eb88440d8a98906c93b
< Accept-Ranges: bytes
< Last-Modified: Sat, 10 Mar 2018 02:18:42 GMT
< X-Object-Meta-Slomd5: ee54e072da4a66478a187ba834a0d56a
< X-Timestamp: 1520648321.10714
< X-Static-Large-Object: True
< Content-Type: application/json; charset=utf-8
< X-Trans-Id: txd2b66e1d608e44f29e8d7-005aa34080
< X-Openstack-Request-Id: txd2b66e1d608e44f29e8d7-005aa34080
< Date: Sat, 10 Mar 2018 02:18:41 GMT
<
[{"hash": "d4cd1ebdd6ffd624c13442a3150ba648", "last_modified": "2018-03-06T20:12:02.000000", "bytes": 1048576, "name": "/test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000000", "content_type": "application/octet-stream"}, {"hash": "39a8e52484fe541173cbd9c10f174798", "last_modified": "2018-03-06T20:12:02.000000", "bytes": 1048576, "name": "/test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000001", "content_type": "application/octet-stream"}, {"hash": "5b9f6406ae96d5320fa156fd12f2436f", "last_modified": "2018-03-06T20:12:02.000000", "bytes": 1048576, "name": "/test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000002", "content_type": "application/octet-stream"}, {"hash": "9975d30d2b6bfa51b2d8370555ac5080", "last_modified": "2018-03-06T20:12:02.000000", "bytes": 1048576, "name": "/test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000003", "content_type": "application/octet-stream"}, {"hash": "f045ccb6f4051e421de7639bbb13e4b2", "last_modified": "2018-03-06T20:12:02.000000", "bytes": 1048576, "name": "/test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000004", "content_type": "application/octet-stream"}, {"hash": "43f57e2e8a5ed9089812496cad72fdb1", "last_modified": "2018-03-06T20:12:02.000000", "bytes": 1048576, "name": "/test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000005", "content_type": "application/octet-stream"}, {"hash": "8426f2c064c18df2c6fe37f7c3b0f047", "last_modified": "2018-03-06T20:12:02.000000", "bytes": 1048576, "name": "/test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000006", "content_type": "application/octet-stream"}, {"hash": "e2abcbfe74aae58d0e408beb5097ce20", "last_modified": "2018-03-06T20:12:02.000000", "bytes": 1048576, "name": "/test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000007", "content_type": "application/octet-stream"}, {"hash": "e3f497be28f16d8cd53698d40d438821", "last_modified": "2018-03-06T20:12:02.000000", "bytes": 1048576, "name": "/test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000008", "content_type": "application/octet-stream"}, {"hash": "015f42efd59b9ffdd382f3e58fc66baf", "last_modified": "2018-03-06T20:12:02.000000", "bytes": 1048576, "name": "/test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000009", "content_type": "application/octet-stream"}, {"hash": "b23d343e5af6b002b20892c77ba45685", "last_modified": "2018-03-06T20:12:03.000000", "bytes": 1048576, "name": "/test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000010", "content_type": "application/octet-stream"}, {"hash": "6627b9f714f2f24120b45324d42f7eab", "last_modified": "2018-03-06T20:12:03.000000", "bytes": 1048576, "name": "/test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000011", "content_type": "application/octet-stream"}, {"hash": "65df14fb47075c83ff0e51c9c95f335b", "last_modified": "2018-03-06T20:12:03.000000", "bytes": 1048576, "name": "/test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000012", "content_type": "application/octet-stream"}, {"hash": "aac01f3ee2c8166e069972b386ab6334", "last_modified": "2018-03-06T20:12:03.000000", "bytes": 1048576, "name": "/test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000013", "content_type": "application/octet-stream"}, {"hash": "482b33723dfa57235d8204ac5c5b60b2", "last_modified": "2018-03-06T20:12:03.000000", "bytes": 1048576, "name": "/test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000014", "content_type": "application/octet-stream"}, {"hash": "a53ab1e24eabb5c08d6b5533b04fb112", "last_modified": "2018-03-06T20:12:03.000000", "bytes": 1048576, "name": "/test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000015", "content_type": "application/octet-stream"}, {"hash": "6201980a66f777d041b287fe9b539d19", "last_modified": "2018-03-06T20:12:03.000000", "bytes": 1048576, "name": "/test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000016", "content_type": "application/octet-stream"}, {"hash": "bb43e35e29364c25965fe34be119bd07", "last_modified": "2018-03-06T20:12:03.000000", "bytes": 1048576, "name": "/test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000017", "content_type": "application/octet-stream"}, {"hash": "018ad2e30338737613d85c3e7c4a6130", "last_modified": "2018-03-06T20:12:03.000000", "bytes": 1048576, "name": "/test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000018", "content_type": "application/octet-stream"}, {"hash": "637be930fee722f2cc1be414e24b5b29", "last_modified": "2018-03-06T20:12:03.000000", "bytes": 1048576, "name": "/test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000019", "content_type": "application/octet-stream"}, {"hash": "176f1c056099d2c49ecea19c1e94c493", "last_modified": "2018-03-06T20:12:03.000000", "bytes": 1048576, "name": "/test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000020", "content_type": "application/octet-stream"}, {"hash": "9d71937d63c2922c4bbade05a7058a5d", "last_modified": "2018-03-06T20:12:03.000000", "bytes": 1048576, "name": "/test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000021", "content_type": "application/octet-stream"}, {"hash": "c43b28d7cb03280c49e0a6ef94c7a539", "last_modified": "2018-03-06T20:12:03.000000", "bytes": 1048576, "name": "/test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000022", "content_type": "application/octet-stream"}, {"hash": "fd0d7b2d1a16aaa588bf37dc2ac1033f", "last_modified": "2018-03-06T20:12:03.000000", "bytes": 1048576, "name": "/test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000023", "content_type": "application/octet-stream"}, {"hash": "91f8af59b779d85bfb48bf19dee8faae", "last_modified": "2018-03-* Connection #0 to host 127.0.0.1 left intact
06T20:12:03.000000", "bytes": 1048576, "name": "/test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000024", "content_type": "application/octet-stream"}, {"hash": "217af21ad4ab9836c012f7e9b5763d96", "last_modified": "2018-03-06T20:12:03.000000", "bytes": 1048576, "name": "/test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000025", "content_type": "application/octet-stream"}, {"hash": "85f1e02ddd35a5085cd724148b154c73", "last_modified": "2018-03-06T20:12:03.000000", "bytes": 620191, "name": "/test_segments/bbb_sunflower_1080_2min.mp4/1520366236.000000/27883167/1048576/00000026", "content_type": "application/octet-stream"}]ubuntu@docker:~/git$
ubuntu@docker:~/git$
ubuntu@docker:~/git$ swift -A http://127.0.0.1:8080/auth/v1.0 -U test:tester -K testing stat -v slo bbb_sunflower_1080_2min.mp4
                   URL: http://127.0.0.1:8080/v1/AUTH_test/slo/bbb_sunflower_1080_2min.mp4
            Auth Token: AUTH_tke383f71f6f324372bef38a6372c2d6ab
               Account: AUTH_test
             Container: slo
                Object: bbb_sunflower_1080_2min.mp4
          Content Type: application/x-www-form-urlencoded
        Content Length: 27883167
         Last Modified: Sat, 10 Mar 2018 02:18:42 GMT
                  ETag: "8b9a8a2c3a6573ecdfd2096303e44b42"
           Meta Slomd5: ee54e072da4a66478a187ba834a0d56a
         Accept-Ranges: bytes
           X-Timestamp: 1520648321.10714
            X-Trans-Id: tx701c78b4748e4952bf7ad-005aa34091
 X-Static-Large-Object: True
X-Openstack-Request-Id: tx701c78b4748e4952bf7ad-005aa34091
```
**PS**: please check closely `Meta Slomd5: ee54e072da4a66478a187ba834a0d56a` for python swiftclient or `X-Object-Meta-Slomd5: ee54e072da4a66478a187ba834a0d56a` for curl command in above example. It's md5sum of testing mp4 file
```
$ md5sum bbb_sunflower_1080_2min.mp4
ee54e072da4a66478a187ba834a0d56a  bbb_sunflower_1080_2min.mp4
```
