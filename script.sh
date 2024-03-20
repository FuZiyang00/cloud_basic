#!/bin/bash

for i in {1..30}
do
   docker exec -e OC_PASS=ziyang1234! --user www-data nextcloud1 /var/www/html/occ user:add --password-from-env user$i

   # docker exec -e OC_PASS=ziyang1234! --user www-data nextcloud2 /var/www/html/occ user:add --password-from-env user$i
   # for adding users to the system with 2 instances
done

locust -f testing.py --host http://localhost:80 -u 30 

# --host http://localhost:8080 for testing the single instance setting
# --host http://localhost:80 for testing the multi-instances setting