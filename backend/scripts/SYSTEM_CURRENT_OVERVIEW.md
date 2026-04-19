# Smart Home System - Current Architecture Overview

Tai lieu nay giai thich he thong hien tai dang van hanh nhu the nao,
model nao dung cho viec gi, va du lieu chay qua cac buoc ra sao.

## 1) Muc tieu he thong hien tai

He thong phan tich hanh vi su dung thiet bi trong nha thong minh,
sau do tao goi y cho nguoi dung theo 3 nhom:

- TIME_HABIT: thoi quen bat thiet bi theo gio
- CLUSTER: nhom phong cach sinh hoat cua user (K-Means)
- ANOMALY: canh bao bat thuong (co the quen tat)

Cuoi cung LLM formatter chuyen pattern thanh cau goi y tieng Viet de hien thi tren app.

## 2) Thanh phan chinh va vai tro

### 2.1 Analytics pipeline

File chinh: backend/scripts/run_analytics.py

Pipeline nay tao pattern tu activity logs va luu vao bang user_patterns.

Gom 3 pha:

1. Rule-based habit miner (TIME_HABIT)
- Khong phai ML model.
- Gom nhom theo user, device, hour, day_of_week.
- Tim thoi quen xuat hien du tan suat.

2. K-Means clustering (CLUSTER)
- Day la model ML chinh trong he thong hien tai.
- Muc tieu: phan cum user theo phong cach su dung thiet bi.
- Ket qua luu vao user_patterns voi pattern_type = CLUSTER.

3. Statistical anomaly detector (ANOMALY)
- Khong phai ML supervised.
- Dung nguong mean + 2 * std tren duration_seconds.
- Tim cac lan bat thiet bi qua lau de canh bao.

### 2.2 LLM formatter pipeline

File chinh: backend/scripts/run_llm_formatter.py

Pipeline nay KHONG lam mining pattern.
No chi doc pattern da co trong user_patterns,
sau do goi LLM (Ollama/Claude) de viet goi y tu nhien.

Output luu vao bang suggestion_logs.

## 3) Model nao dang dung cho viec gi?

- K-Means:
  - Dung cho CLUSTER (phan cum thoi quen user)
  - La model ML chinh cua he thong analytics

- Rule-based GROUP BY:
  - Dung cho TIME_HABIT
  - Khong phai ML

- Statistical threshold (mean + 2*std):
  - Dung cho ANOMALY
  - Khong phai ML

- LLM (Ollama/Claude):
  - Dung de dien dat pattern thanh suggestion text/json
  - Khong thay the K-Means, khong thay rule miner

## 4) Luong du lieu end-to-end

1. activity_logs -> run_analytics.py
2. run_analytics.py -> user_patterns (TIME_HABIT, CLUSTER, ANOMALY)
3. user_patterns -> run_llm_formatter.py
4. run_llm_formatter.py -> suggestion_logs
5. API/mobile doc suggestion_logs de hien thi cho nguoi dung

## 5) Feature va du lieu cho K-Means

Trong run_analytics.py, vector hanh vi user gom 27 chieu:

- 24 chieu: tan suat theo gio h0..h23
- 1 chieu: unique_devices ratio
- 1 chieu: weekend_ratio
- 1 chieu: avg_duration_hours

Tien xu ly:

- Loc event DEVICE_ON
- Loc trigger_source phu hop hanh vi nguoi dung
- Chuan hoa StandardScaler truoc khi clustering

## 6) Dieu kien de tung pha duoc chay

- TIME_HABIT: can du ngay du lieu toi thieu (rule-based threshold)
- CLUSTER (K-Means): can du so ngay va du so user hop le
- ANOMALY: can du mau tren tung device de tinh mean/std co y nghia

Neu khong du dieu kien, pha do se bi skip.

## 7) Bang Input/Output nhanh

- Input chinh:
  - homes
  - users, home_users
  - activity_logs

- Output trung gian:
  - user_patterns

- Output cuoi cho app:
  - suggestion_logs

## 8) Y nghia thuc te cho bao cao

Neu can tra loi cau hoi "he thong hien tai dang dung model gi",
ban co the noi ngan gon:

- He thong su dung K-Means de phan cum thoi quen su dung thiet bi cua user.
- He thong ket hop rule-based va statistical detection de tao pattern bo tro.
- LLM duoc dung o buoc dien dat ket qua thanh goi y than thien cho nguoi dung.

## 9) File tham chieu quan trong

- backend/scripts/run_analytics.py
- backend/scripts/run_llm_formatter.py
- backend/scripts/model_selection_smarthome.ipynb
- backend/scripts/analytics_best_config.json
