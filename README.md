# CS Space backend
## Provide credentials
The credentials for the database connection
must be specified in the file `.env`.

Example of minimal configuration:
```
MONGODB_URL=mongodb://localhost:27017
MONGODB_NAME=test
```

Any other private environment variables can be configured in the same way.

## Run FastAPI

From project root:

```#shell
uvicorn src.main:app --reload
```

## Run MongoDB

```#shell
mongod --dbpath /your-db-path --replSet rs0
```
