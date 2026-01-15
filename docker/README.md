docker container creation cmd w/mapping from docker local dir to /data on container
docker run -it -p 5678:5678 -v ~/n8n-data:/home/node/.n8n -v /Users/nnayak/Documents/agentRise/aiYT/docker:/data n8n-python
^ this creates container w/a random name. To name it, add --name <container_name> before n8n-python (haven't tested this).
^ use "docker ps" to determine container name if not specified.


http request (must be runn python app2.py locally):
http://host.docker.internal:5000/test

to access shell:
docker exec -it <container_name> /bin/bash
