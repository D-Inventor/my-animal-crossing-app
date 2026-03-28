```bash
kafka-console-producer --bootstrap-server kafka:9092 --topic import_commands
```

```json
{"$type":"ImportVillagersCommand", "id":"a99ca4ff-0c1b-42df-bb0b-4a0ba3f1a6ef"}
{"$type":"VillagerSnapshotDownloadedEvent", "saga_id":"a99ca4ff-0c1b-42df-bb0b-4a0ba3f1a6ef", "snapshot_id":"445befb3-fb9b-476e-bece-50eb94c34c0c"}
```