network:
	sudo docker network create -d macvlan \
		--subnet=192.168.1.0/24 \
		--gateway=192.168.1.1 \
		-o parent=enp7s0 \
		homelab

up:
	sudo docker build -t simple-scraper web_scraper
	sudo docker run -d \
		--network homelab \
	 	--ip 192.168.1.10 \
		-p 8001:8001 \
		--name web_scraper \
		simple-scraper
	
	sudo docker build -t echo-api echo
	sudo docker run -d \
		--network homelab \
  	--ip 192.168.1.11 \
		-p 8000:8000 \
		--name echo-api \
		echo-api

	# sudo docker build -t echo-api-vulnerable echo_vulnerable
	# sudo docker run -d \
	# 	--network homelab \
	# 	--ip 192.168.1.12 \
	# 	-p 8002:8002 \
	# 	--name echo-api-vulnerable \
	# 	echo-api-vulnerable

	sudo docker build -t net-tester net_tester
	sudo docker run -d \
			--network homelab \
			--ip 192.168.1.13 \
			--name net-tester \
			net-tester

down:
	sudo docker stop /web_scraper /echo-api /echo-api-vulnerable # /net-tester
	sudo docker rm /web_scraper /echo-api  /echo-api-vulnerable # /net-tester
