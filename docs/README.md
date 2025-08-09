# Project Documentation

- Versioning & Releases: see [VERSION_AUTOMATION.md](./VERSION_AUTOMATION.md)
- Configuration templates: see `config/README.md`
- Examples: see the `examples/` directory for HA discovery and core usage

Notes
- This library parses only `mqtt.*` from YAML. Configure HA discovery in code using `mqtt_publisher.ha_discovery`.
- For release steps, prefer the `./release.sh` script.
