#python setup.py install
python ./setup.py sdist
pip install ./dist/slo_hash-0.0.1.tar.gz --upgrade
swift-init proxy-server restart
tail -f /var/log/swift/proxy_access.log
