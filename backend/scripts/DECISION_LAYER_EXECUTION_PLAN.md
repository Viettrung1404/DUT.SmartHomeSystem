# Decision Layer Execution Plan (W1-W4)

Muc tieu:
- Chuyen he thong tu event understanding sang recommendation decision dung business goal.
- Khong pha vo pipeline hien tai (run_analytics.py + run_llm_formatter.py).
- Trien khai theo sprint nho, do duoc, rollback duoc.

---

## 1) Target business moi

Target supervised uu tien:
- SHOULD_SUGGEST = 0/1

Target phu (optional):
- FORGOT_TO_TURN_OFF = 0/1

Ly do:
- Event classification (DEVICE_ON/OFF/FORGOT_OFF) chi tra loi "chuyen gi dang xay ra".
- He thong can tra loi "co nen goi y hay khong".

---

## 2) Kien truc 3 tang

1. Event Understanding
- Dau vao: activity_logs
- Dau ra: user_patterns (TIME_HABIT, CLUSTER, ANOMALY)

2. Decision Layer
- Dau vao: user_patterns + activity context + historical acceptance
- Dau ra: decision candidates (score + explain + should_suggest)

3. Delivery Layer
- Dau vao: candidates da pass threshold
- Dau ra: suggestion_logs (qua run_llm_formatter.py)

---

## 3) Decision score de production

Cong thuc de xuat:

S = w1*PatternConfidence
  + w2*AnomalySeverity
  + w3*HistoricalAcceptance
  + w4*EnergySavingPotential
  + w5*UserPreference
  + w6*Urgency

Gia tri moi thanh phan chuan hoa [0,1].
Suggest neu S >= threshold.

De xuat threshold khoi tao:
- default threshold = 0.65
- safety/anomaly co the dung threshold thap hon (0.55-0.60)

---

## 4) Schema de xuat (phase 2)

Khuyen nghi them bang moi de audit va huan luyen:

Table: recommendation_decisions
- id (pk)
- user_id (uuid)
- home_id (uuid)
- pattern_id (int, nullable)
- score (float)
- threshold (float)
- should_suggest (bool)
- score_breakdown (jsonb)
- explanation_json (jsonb)
- model_version (string)
- created_at

Tam thoi (phase 1) co the xuat ra JSON file de nhanh test.

---

## 5) W1-W4 backlog

### W1 - Baseline + scoring skeleton
Deliverables:
- run_decision_scoring.py (dry-run)
- decision_candidates.json output
- metrics baseline luu tai lieu

Done criteria:
- Script chay duoc tren DB hien tai
- Co score va should_suggest cho tung pattern active

### W2 - Feature enrichment
Deliverables:
- Them temporal/sequential feature extractor
- previous_device, time_since_last_event, frequency_24h, inactivity_gap

Done criteria:
- Co them feature vao score_breakdown
- So sanh false alerts truoc/sau

### W3 - Explainable layer
Deliverables:
- explanation builder theo rule + score contribution
- output explanation_json de UI/LLM su dung

Done criteria:
- Moi candidate pass threshold co ly do ro rang

### W4 - Evaluation theo recommendation metrics
Deliverables:
- Precision@K
- False Alert Rate
- Suggestion Acceptance Rate
- Utility score (simulation)

Done criteria:
- Co report metrics recommendation, khong chi Accuracy/F1

---

## 6) Tich hop voi pipeline hien tai

Thu tu chay de xai ngay:
1. python scripts/run_analytics.py
2. python scripts/run_decision_scoring.py --write-json backend/scripts/decision_candidates.json
3. python scripts/run_llm_formatter.py (chi format nhung candidate pass threshold trong phase tiep theo)

---

## 7) Rủi ro va cache strategy

Rui ro:
- Nhieu false positive luc dau
- Label SHOULD_SUGGEST thieu

Giam rui ro:
- Bat dau threshold cao
- Cooldown theo user/device
- Cap nhat trong 1 chu ky ngan (hang tuan)

---

## 8) Versioning

Model/version naming de de truy vet:
- decision_v0_rule_weighted
- decision_v1_temporal
- decision_v2_sequence

Moi ban release can luu:
- score formula
- weights
- threshold
- metrics
