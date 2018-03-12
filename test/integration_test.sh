echo "===check md5sum for bbb_sunflower_1080_2min.mp4"
beforemd5=$(md5sum ./samples/bbb_sunflower_1080_2min.mp4 | awk '{print $1}')
echo $beforemd5

echo "===preparation create slo and slo_segments containers==="
swift -A http://127.0.0.1:8080/auth/v1.0 -U test:tester -K testing post slo
swift -A http://127.0.0.1:8080/auth/v1.0 -U test:tester -K testing post slo_segments

echo "===upload test slo 3 segments object==="
swift -A http://127.0.0.1:8080/auth/v1.0 -U test:tester -K testing upload slo_segments ./samples/bbb_sunflower_1080_2min_001.mp4 --object-name bbb_sunflower_1080_2min_001.mp4
swift -A http://127.0.0.1:8080/auth/v1.0 -U test:tester -K testing upload slo_segments ./samples/bbb_sunflower_1080_2min_002.mp4 --object-name bbb_sunflower_1080_2min_002.mp4
swift -A http://127.0.0.1:8080/auth/v1.0 -U test:tester -K testing upload slo_segments ./samples/bbb_sunflower_1080_2min_003.mp4 --object-name bbb_sunflower_1080_2min_003.mp4

echo "===get token==="
auth_token=$(swift -A http://127.0.0.1:8080/auth/v1.0 -U test:tester -K testing auth | grep "export OS_AUTH_TOKEN=" | awk -F"=" '{print $2}')
echo $auth_token
echo "===upload test slo manifest object==="
curl -H "X-Auth-Token: $auth_token" -v -X PUT http://127.0.0.1:8080/v1/AUTH_test/slo/bbb_sunflower_1080_2min.mp4?multipart-manifest=put -d '[{"path":"slo_segments/bbb_sunflower_1080_2min_001.mp4","etag":"07b81cd438af5097d584321ab99cdc06","size_bytes":10485760},{"path":"slo_segments/bbb_sunflower_1080_2min_002.mp4","etag":"ff53521cfdfe801ab1e52d0e7fda4969","size_bytes":10485760},{"path":"slo_segments/bbb_sunflower_1080_2min_003.mp4","etag":"e924eaf1e2171ff355c588fa84da5778","size_bytes":6911647}]'

echo "===check metadata no X-Object-Meta-Slomd5==="
swift -A http://127.0.0.1:8080/auth/v1.0 -U test:tester -K testing stat -v slo bbb_sunflower_1080_2min.mp4

echo "***===trigger slomd5 via GET and ?multipart-manifest=get===***"
curl -H "X-Auth-Token: $auth_token" -v -X GET http://127.0.0.1:8080/v1/AUTH_test/slo/bbb_sunflower_1080_2min.mp4?multipart-manifest=get

echo "\n"

echo "===check metadata again , has X-Object-Meta-Slomd5==="
swift -A http://127.0.0.1:8080/auth/v1.0 -U test:tester -K testing stat -v slo bbb_sunflower_1080_2min.mp4

echo "===get Slomd5==="
metamd5=$(swift -A http://127.0.0.1:8080/auth/v1.0 -U test:tester -K testing stat -v slo bbb_sunflower_1080_2min.mp4 | grep Slomd5 | awk '{print $3}')
echo $metamd5

echo "===regression test for list the object by account==="
swift -A http://127.0.0.1:8080/auth/v1.0 -U test:tester -K testing list

echo "===regression test for list the objects in slo container==="
swift -A http://127.0.0.1:8080/auth/v1.0 -U test:tester -K testing list slo

echo "===regression test for download the object to name bbb_sunflower_1080_2min.mp4.download==="
swift -A http://127.0.0.1:8080/auth/v1.0 -U test:tester -K testing download slo bbb_sunflower_1080_2min.mp4 --output bbb_sunflower_1080_2min.mp4.download

echo "===check md5sum for bbb_sunflower_1080_2min.mp4.download==="
aftermd5=$(md5sum ./bbb_sunflower_1080_2min.mp4.download | awk '{print $1}')
echo $aftermd5

echo "===delete the object - wipeout manifest and segments objects==="
swift -A http://127.0.0.1:8080/auth/v1.0 -U test:tester -K testing delete slo bbb_sunflower_1080_2min.mp4

echo "===delete download object==="
rm -rf ./bbb_sunflower_1080_2min.mp4.download

echo "===                                         sum of result                                             ==="
echo "===         before md5           vs            meta md5              vs          after md5            ==="
echo "---------------------------------------------------------------------------------------------------------"
echo "$beforemd5 vs $metamd5 vs $aftermd5"
