# NLP Dataset V1

This directory stores the custom Vietnamese smart-home corpus for the current house topology.

## Files

- `master.jsonl`: full corpus with intent, slots, split metadata, tokens, and BIO tags.
- `train.jsonl`, `val.jsonl`, `test.jsonl`: split views derived from `split_group`.
- `bio/*.jsonl`: lightweight token/tag view for PhoBERT slot tagging.
- `summary.json`: corpus counts by intent, split, and language variant.

## Record Schema

Each JSONL row contains:

- `id`
- `text`
- `normalized_text`
- `intent`
- `slots`
- `source`
- `split_group`
- `split`
- `language_variant`
- `notes`
- `tokens`
- `slot_tags`

`slots` uses the shape:

```json
{
  "room": {"value": "living_room", "text": "phòng khách"},
  "device_type": {"value": "light", "text": "đèn"},
  "device_name": {"value": "living_light", "text": "đèn phòng khách"},
  "action": {"value": "turn_on", "text": "bật"}
}
```

## Split Policy

Rows are not split randomly. `split_group` keeps paraphrase families together to reduce template leakage between train and test.

## Notes for PhoBERT

BIO tags are generated from `normalized_text`. When slots overlap, the BIO export prioritizes longer spans first so that slot tagging stays non-overlapping.
