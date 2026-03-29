```bash
kafka-console-producer --bootstrap-server kafka:9092 --topic import_commands
```

```json
{"$type":"ImportVillagersCommand", "id":"b50a5295-3cb6-4922-9ca3-c1638cb9ca75"}
{"$type":"VillagerSnapshotDownloadedEvent", "saga_id":"a99ca4ff-0c1b-42df-bb0b-4a0ba3f1a6ef", "snapshot_id":"445befb3-fb9b-476e-bece-50eb94c34c0c"}
```