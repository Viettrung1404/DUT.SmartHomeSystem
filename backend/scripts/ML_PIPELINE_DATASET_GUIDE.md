# Smart Home ML Pipeline and Dataset Integration Guide

Tai lieu nay giai thich 2 viec theo cach de ap dung:

1. Luong logic ML pipeline hien tai trong he thong Smart Home.
2. Cach lay dataset tren mang, transform, va nap vao DB de fit voi pipeline.

---

## 1) He thong hien tai dang lam gi?

Muc tieu cua he thong:

- Doc hanh vi su dung thiet bi tu activity_logs.
- Rut ra pattern hanh vi tu run_analytics.py.
- Chuyen pattern thanh goi y de doc cho nguoi dung tu run_llm_formatter.py.

Output cuoi de app hien thi la bang suggestion_logs.

---

## 2) Luong du lieu end-to-end (de hieu)

1. Du lieu su kien vao DB:
   - Chu yeu vao activity_logs.
   - Co lien ket home_id, user_id, device_id.

2. Chay analytics (run_analytics.py):
   - Pha A: TIME_HABIT (rule-based).
   - Pha B: CLUSTER (KMeans/DBSCAN theo config).
   - Pha C: ANOMALY (thong ke mean + 2*std).
   - Ket qua luu vao user_patterns.

3. Chay formatter (run_llm_formatter.py):
   - Doc user_patterns active.
   - Goi LLM de viet lai thanh cau goi y.
   - Luu vao suggestion_logs.

Tom gon:

activity_logs -> user_patterns -> suggestion_logs

---

## 3) Logic tung pha trong run_analytics.py

### 3.1 TIME_HABIT (rule-based)

Y tuong:

- Nhom theo (user_id, device_id, hour, day_of_week).
- Neu tan suat du lon thi xem la thoi quen.

Dau vao can co:

- event_type = DEVICE_ON.
- trigger_source uu tien hanh vi nguoi dung (USER, PHYSICAL_ATTRIBUTED).
- Du so ngay toi thieu (threshold trong script).

Dau ra:

- Pattern TIME_HABIT trong user_patterns.

### 3.2 CLUSTER (ML)

Y tuong:

- Moi user duoc bien thanh 1 vector hanh vi (theo gio, cuoi tuan, so thiet bi, duration).
- Scale feature -> cluster.
- Dat nhan mo ta kieu sinh hoat cho cum.

Dau vao can co:

- Du data cho moi user de tao feature vector.
- Du so user hop le trong cung home de cluster co y nghia.

Dau ra:

- Pattern CLUSTER trong user_patterns.

### 3.3 ANOMALY (thong ke)

Y tuong:

- Tinh baseline duration theo thiet bi.
- Tim lan su dung vuot nguong bat thuong.

Dau ra:

- Pattern ANOMALY trong user_patterns.

---

## 4) Vi sao du lieu moi thuong khong ra pattern?

4 loi pho bien:

1. Khong du density theo thoi gian:
   - Du lieu trai dai qua nhieu ngay nhung moi ngay qua it event.
2. Event schema khong dung:
   - State khong map duoc sang ON/OFF.
3. User mapping kem chat luong:
   - Tat ca event don 1 user hoac phan bo vo nghia.
4. Device naming khong on dinh:
   - Cung mot thiet bi nhung nhieu ten khac nhau.

Khi gap truong hop nay, uu tien sua ETL/transform truoc khi chinh model.

---

## 5) Playbook: transform dataset tren mang vao DB

Ap dung cho dataset IoT/smart home bat ky (CASAS, UCI, Kaggle, log tu thiet bi that).

### Buoc 1 - Kiem tra dataset goc

Can xac dinh:

- Co timestamp hay khong?
- Co sensor/device id hay khong?
- Co state/event type hay khong?
- Co user/person label hay khong?

Neu khong co user label, van nap duoc (co the map 1 user, hoac chia deterministic).

### Buoc 2 - Chuan hoa schema trung gian

Nen dua moi dong ve dang:

- timestamp
- sensor_name
- state_raw
- label (optional)

Vi du state map:

- ON, OPEN, PRESENT -> DEVICE_ON
- OFF, CLOSE, ABSENT -> DEVICE_OFF

### Buoc 3 - Chuan hoa timezone

- Chot 1 timezone nhat quan, hien tai he thong dung Asia/Ho_Chi_Minh.
- Neu dataset la UTC, convert truoc khi insert.

### Buoc 4 - Chuan hoa ten thiet bi

- Slug hoa ten sensor de tao device_id on dinh.
- Cung mot sensor phai ra cung mot device_id.

Vi du:

- Kitchen Light -> casas_kitchen_light
- Kitchen-Light -> cung casas_kitchen_light

### Buoc 5 - Gan home/user

Can tao/gan:

- 1 home cho bo dataset.
- 1 hoac nhieu user.
- Bang lien ket home_users.

Neu dataset khong co person label:

- Cach 1: map tat ca ve 1 user.
- Cach 2: map deterministic (theo ngay + gio + sensor) de chia deu va reproducible.

### Buoc 6 - Build activity session

- Moi ON can co OFF de tinh duration_seconds.
- Neu ON ma khong co OFF thi danh dau FORGOT_OFF.

Ket qua insert vao activity_logs nen co:

- timestamp
- event_type
- trigger_source (nen de SENSOR neu la dataset sensor)
- device_id
- user_id
- home_id
- duration_seconds (neu co)
- metadata_json (giu raw info de trace)

### Buoc 7 - Validate du lieu sau ETL

Kiem tra nhanh truoc khi chay analytics:

- So dong log theo user/home.
- So ngay co data (COUNT DISTINCT DATE(timestamp)).
- So device khac nhau.
- Ti le ON/OFF va FORGOT_OFF.

Neu co user < 20 events (hoac qua it), cluster se bi skip.

### Buoc 8 - Chay pipeline

Thu tu chay:

1. ETL import data
2. python scripts/run_analytics.py
3. python scripts/run_llm_formatter.py

---

## 6) Mapping table de fit DB (thuc dung)

| Nguon dataset | DB field de nap | Rule map goi y |
| --- | --- | --- |
| date + time | activity_logs.timestamp | Parse datetime + gan timezone |
| sensor | activity_logs.device_id | Slug hoa + tao device neu chua co |
| state | activity_logs.event_type | ON/OPEN/PRESENT -> DEVICE_ON; OFF/CLOSE/ABSENT -> DEVICE_OFF |
| person (neu co) | activity_logs.user_id | Map user theo label; neu khong co dung rule deterministic |
| dataset id/home name | activity_logs.home_id | Tao 1 home cho moi bo dataset |
| ON/OFF pair | activity_logs.duration_seconds | OFF - ON (second) |
| nhan hoat dong goc | activity_logs.metadata_json | Luu lai de truy vet |

---

## 7) Ap dung nhanh voi CASAS (da co san)

Duong ETL hien tai:

- backend/data/ETL_Pipeline/casas_etl.py

Input ho tro:

- Raw CSV: date,time,sensor,state
- Labeled CSV: date,time,sensor,state,label

Script nay da lam san:

- Auto tao home/user/room/device/device_state.
- Map ON/OFF event type.
- Pair ON/OFF de tinh duration.
- Suy dien FORGOT_OFF.
- Ho tro map nhieu user qua --user-emails.

---

## 8) Checklist truoc khi danh gia model

Truoc khi ket luan model khong tot, kiem tra 6 dieu sau:

1. Du lieu da convert dung timezone chua?
2. Device ID co bi trung nghia khac ten khong?
3. User mapping co hop ly khong?
4. Co du so ngay va du tan suat event chua?
5. Co qua nhieu missing OFF log khong?
6. Trigger source co dung cho bai toan hanh vi khong?

Neu 6 muc nay on ma pattern van yeu, luc do moi chinh threshold/feature/model.

---

## 9) File lien quan trong backend/scripts

- run_analytics.py: mining pattern.
- run_llm_formatter.py: tao suggestion text/json.
- analytics_best_config.json: config model export tu notebook.
- model_selection_smarthome.ipynb: notebook chon model.
- model_output.ipynb: notebook output da execute (phuc vu review/bao cao).

---

## 10) De xuat van hanh practical

De tranh loi tung lan import dataset moi:

1. Luon chay import mau (--limit) truoc.
2. Chay bo validate SQL ngan gon.
3. Chay analytics va xem so pattern moi home.
4. Neu pattern = 0, sua ETL mapping/quality truoc, khong voi doi model.

Mau quy trinh nay giup ban dua dataset tu internet vao he thong nhanh hon va it gap loi logic pipeline.
