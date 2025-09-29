
### To start mongo shell `docker exec -it mongo mongosh` then `use air_quality` then `rs.initiate()`

### Setup kafka topic manually <!-- docker-compose exec kafka kafka-topics --create --topic air_quality_events --partitions 1 --replication-factor 1 --bootstrap-server localhost:9092 -->

### Restart storage and streaming containers after the setting up mongo in step 1 and setting up kafka topic step 4 `docker restart storage streaming`
### To start cassandra `cqlsh localhost 9042` then `USE air_quality_keyspace;`
