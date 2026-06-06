# Environment Data V1

Environment prediction in this repo is scoped to a single ambient zone because the current hardware plan assumes one DHT11 node.

## Expected House Log CSV

Place your real log at:

- `data/environment/house_ambient_log.csv`

Expected columns:

- `timestamp`
- `temperature`
- `humidity`

Optional columns:

- `room_id`
- `occupancy_ratio`
- `fan_on`
- `rain_detected`
- `outdoor_temp`
- `bathroom_occupied`

If only `bathroom_occupied` exists, the trainer maps it into `occupancy_ratio`.

## Reference Data

If you want a public-reference benchmark, place a CSV at:

- `data/environment/reference_environment_log.csv`

The trainer will use:

1. `house_ambient_log.csv` when available
2. `reference_environment_log.csv` otherwise
3. synthetic bootstrap data as a final fallback

## Reporting Rule

When presenting results, keep the distinction explicit:

- `benchmark on public/reference data`
- `final demo model trained on house logs`
