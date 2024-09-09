import subprocess
from io import StringIO
from dotenv import load_dotenv
import os

result = subprocess.run(["azd","env","get-values"], stdout=subprocess.PIPE, cwd=os.getcwd())
print(result)

// docker network create mongo-network

// doceker run -d \
// -p 27017:27017 \
// -e MONGO_INITDB_ROOT_USERNAME=admin \ 
// -e MONGO_INITDB_ROOT_PASSWORD=password \
// --net mongo-network \
// --name mongodb \
// mongo

// docker run -d \
// -p 8081:8081 \
// -e ME_CONFIG_MONGODB_ADMINUSERNAME=admin \
// -e ME_CONFIG_MONGODB_ADMINPASSWORD=password \
// -e ME_CONFIG_MONGODB_SERVER=mongodb \
// --net mongo-network \
// --name mongo-express \
// mongo-express


// docker-compose -f mongo.yaml up -d
// docker-compose -f mongo.yaml donw
// docker-compose -f mongo.yaml ps
// docker-compose -f mongo.yaml logs

// mongo.yaml
// version: '3'
// services:
//   mongodb:
//     image: mongo
//     container_name: mongodb
//     ports:
//       - "27017:27017"
//     environment:
//       MONGO_INITDB_ROOT_USERNAME: admin
//       MONGO_INITDB_ROOT_PASSWORD: password
//     networks:
//       - mongo-network
//   mongo-express:
//     image: mongo-express
//     container_name: mongo-express
//     ports:
//       - "8081:8081"
//     environment:
//       ME_CONFIG_MONGODB_ADMINUSERNAME: admin
//       ME_CONFIG_MONGODB_ADMINPASSWORD: password
//       ME_CONFIG_MONGODB_SERVER: mongodb
//     networks:
//       - mongo-network