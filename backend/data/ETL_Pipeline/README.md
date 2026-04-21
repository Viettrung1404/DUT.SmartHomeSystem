# CASAS ETL Pipeline

Script: `casas_etl.py`

## Muc tieu

Import du lieu CASAS CSV (raw/labeled) vao bang `activity_logs` theo schema SmartHome.

## Input formats ho tro

- Raw: `date,time,sensor,state`
- Labeled: `date,time,sensor,state,label`

## Chay nhanh (Aruba)

```powershell
python data/ETL_Pipeline/casas_etl.py \
  --input data/dataset/data/data/aruba.csv \
  --home-name "CASAS Aruba Home" \
  --user-emails "hung@import.local,mai@import.local" \
  --reset-home-data
```

## Gan userId cho 2 nguoi

Script da ho tro gan user theo danh sach email voi `--user-emails`.

- Neu truyen 1 email: tat ca log map ve 1 user.
- Neu truyen 2 email tro len: log duoc chia deterministically theo ngay (day parity).

Vi du:

```powershell
python data/ETL_Pipeline/casas_etl.py \
  --input data/dataset/data/data/aruba.csv \
  --home-name "CASAS Aruba Home" \
  --user-emails "hung@import.local,mai@import.local" \
  --reset-home-data
```

## Chay thu voi gioi han dong

```powershell
python data/ETL_Pipeline/casas_etl.py \
  --input data/dataset/data/data/aruba.csv \
  --limit 20000 \
  --home-name "CASAS Aruba Home" \
  --user-email "aruba@import.local" \
  --reset-home-data
```

## Chay voi file labeled

```powershell
python data/ETL_Pipeline/casas_etl.py \
  --input data/dataset/labeled_data/labeled/hh101.csv \
  --home-name "CASAS HH101 Home" \
  --user-email "hh101@import.local" \
  --reset-home-data
```

## Ket qua ETL

- Tu dong tao `home`, `user`, `home_users` neu chua ton tai.
- Tu dong tao `rooms`, `devices`, `device_states` theo sensor.
- Map state:
  - `ON|OPEN|PRESENT -> DEVICE_ON`
  - `OFF|CLOSE|ABSENT -> DEVICE_OFF`
- Tinh `duration_seconds` bang cap ON/OFF theo tung sensor.
- Neu ON khong co OFF, event duoc suy dien thanh `FORGOT_OFF`.
