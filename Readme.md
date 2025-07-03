
# Time tracking web application.

## Requirements

- Podman

For containerized run, but the app can be run by just python app.py in local shell.


## Prepare a DB directory:

mkdir -p ./time-tracker-data

create and initalize ./time-tracker-data/activities.json

```bash
[
  {
    "id": 0,
    "task_id": 0,
    "action": 1,
    "at": "2025-07-03T10:00:00"
  }
]
```
create and initalize ./time-tracker-data/tasks.json
```bash
[
  {
    "id": 0,
    "name": "Setting up time-tracker"
  }
]
```

## Build the container:

```bash
podman build -t time-tracker .
```

## Run the container in background:

```bash
podman run -d --name time-tracker -p 8001:8001 -v ./time-tracker-data:/data:Z time-tracker
```

 > **_NOTE:_** We are adding a DB dir as a volume to container, so even container is terminated for some reason, data will safe.
