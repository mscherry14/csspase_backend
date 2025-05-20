# CS Space backend
## Provide credentials
The credentials for the database connection and some other secrets
must be specified in the file `.env`.

Example of minimal configuration:
```
MONGODB_URL=mongodb://mongo:27017
MONGODB_NAME=test
TELEGRAM_TOKEN=<your-bot-token>
SECRET_KEY=<secret-key>
```

Any other private environment variables can be configured in the same way.

Optional: `ORIGIN=<your-site>` for CORS settings

## Docker container

Run container with

```#shell
docker-compose up --build
```
### Check MongoDB status
```#shell
docker-compose exec mongo mongosh
```
in mongosh terminal run 
```#shell
rs.status()
```
if you rs been correctly initialized, you have seen `mongo:27017` member 

- if rs wasnt initializes, run
    ```#shell
    rs.initiate({
      _id: "rs0",
      members: [{ _id: 0, host: "mongo:27017" }]
    })
    ```
- if rs has wrong config(like `localhost:27017`), run
    ```#shell
    cfg = rs.conf()
    cfg.members[0].host = "mongo:27017"
    rs.reconfig(cfg, { force: true })
    ```
  
You can test connection from backend with
```#shell
docker-compose exec backend sh
```
```#shell
python
```
```#shell
import socket
socket.gethostbyname("mongo")
```

If all is OK, you get IP like `172.x.x.x`

### Fill database

Scripts for db filling wasn't added to Github. 
But if the scripts are loaded later, you can call them with the command:
```#shell
docker-compose exec backend python <path-to-script>
```

if it is not working, try 
```#shell
docker-compose exec backend sh -c "PYTHONPATH=/app python /app/<path-to-script>"
```