# Smart Home Model Ingest Contract

AI Server does not depend on a dataset name or simulator name. Any simulator,
model, or real device pipeline should write records into the existing smart home
database schema, scoped by the current `home_id`, `user_id`, and `device_id`.

## Required Mapping

### Devices

Use these tables when a model introduces or updates a device:

- `devices`: canonical device identity, name, slug, type, room.
- `device_states`: current state, online flag, last update.

The stable identifier for control is `devices.id`. External identifiers from a
simulator can be stored in `devices.slug` or a model-specific metadata field if
one is added later.

### Activity

Use `activity_logs` for device/sensor events that happened over time:

- `home_id`
- `user_id` when known, otherwise `NULL`
- `device_id`
- `event_type`
- `timestamp`
- `session_end`
- `duration_seconds`
- `description`

### Alerts

Use `security_events` for guardian/security/anomaly alerts:

- `home_id`
- `event_type`
- `severity`
- `description`
- `timestamp`

### Suggestions

Use `suggestion_logs` for recommendations, reminders, and model-generated
advice:

- `user_id`
- `pattern_id` when related to a `user_patterns` row
- `action_type`
- `suggestion_text`
- `suggestion_json`
- `created_at`

When a suggestion belongs to a home-level pattern, connect it through
`user_patterns.home_id`. Do not rely on global dataset rows for product behavior.

### Patterns

Use `user_patterns` for learned behavior:

- `home_id`
- `user_id`
- `device_id` when device-specific
- `pattern_type`
- `pattern_data`
- `confidence`
- `computed_at`
- `is_active`

## AI Query Rule

AI tools only read the current `home_id` and `user_id`. They should not search
other homes or dataset-global rows. If a simulator/model wants AI chat to answer
about a record, it must ingest that record into the active home/user scope.
