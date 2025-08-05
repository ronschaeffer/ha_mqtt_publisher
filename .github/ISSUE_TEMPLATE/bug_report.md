---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: 'bug'
assignees: ''

---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Configure MQTT settings '...'
2. Initialize publisher '....'
3. Publish message '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Configuration sample**
```python
# Minimal code that reproduces the issue
from mqtt_publisher import MQTTPublisher

config = {...}
publisher = MQTTPublisher(config)
```

**Error message**
```
Full error message and traceback if applicable
```

**Environment:**
 - OS: [e.g. Windows, macOS, Linux]
 - Python version: [e.g. 3.11.0]
 - Package version: [e.g. 1.0.0]
 - MQTT Broker: [e.g. Mosquitto 2.0.15]

**Additional context**
Add any other context about the problem here.
