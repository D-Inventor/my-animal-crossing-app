```bash
kafka-console-producer --bootstrap-server kafka:9092 --topic import_commands
```

```json
{"$type":"ImportVillagersCommand", "id":"7b3ae7c1-def1-4b84-af51-d4fffaa2eb99"}
{"$type":"VillagerSnapshotDownloadedEvent", "saga_id":"7b3ae7c1-def1-4b84-af51-d4fffaa2eb99", "snapshot_id":"445befb3-fb9b-476e-bece-50eb94c34c0c"}
```