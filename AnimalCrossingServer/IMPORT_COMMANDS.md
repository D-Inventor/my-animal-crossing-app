```bash
kafka-console-producer --bootstrap-server kafka:9092 --topic import_orchestrator_commands
```

```json
{"$type":"ImportVillagersCommand", "id":"a792f746-da95-44ab-b874-5b5853912f83"}
{"$type":"VillagerSnapshotDownloadedEvent", "saga_id":"a99ca4ff-0c1b-42df-bb0b-4a0ba3f1a6ef", "snapshot_id":"445befb3-fb9b-476e-bece-50eb94c34c0c"}
```