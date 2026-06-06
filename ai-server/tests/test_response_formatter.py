from app.agent.response_formatter import collect_evidence, fallback_answer, max_severity


def test_collect_evidence_keeps_safe_fields():
    evidence = collect_evidence([
        {
            "tool_name": "query_guardian_events",
            "result_count": 1,
            "items": [
                {
                    "id": "e1",
                    "severity": "high",
                    "description": "Door opened",
                    "secret": "hidden",
                }
            ],
        }
    ])

    assert evidence == [
        {
            "type": "query_guardian_events",
            "id": "e1",
            "severity": "high",
            "description": "Door opened",
        }
    ]


def test_max_severity():
    assert max_severity([{"severity": "low"}, {"severity": "critical"}]) == "critical"


def test_fallback_no_evidence_does_not_hallucinate():
    answer, actions = fallback_answer("GUARDIAN_EVENT_QUERY", [])
    assert "chưa tìm thấy dữ liệu" in answer.lower()
    assert actions == []

