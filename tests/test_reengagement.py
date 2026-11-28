from datetime import UTC, date, datetime

import pytest

from services.reengagement import due_stage, notification_key

STAGES = (60, 90, 120)
LAST = date(2026, 9, 1)


@pytest.mark.parametrize(
    "today, expected",
    [
        (date(2026, 10, 30), None),  # 59 kun
        (date(2026, 10, 31), 60),
        (date(2026, 11, 29), 60),  # 89 kun
        (date(2026, 11, 30), 90),
        (date(2026, 12, 30), 120),
        (date(2027, 6, 1), 120),  # undan keyin ham 120 (lekin u bir marta yuboriladi)
    ],
)
def test_due_stage(today, expected):
    assert due_stage(LAST, today, STAGES) == expected


def test_missed_days_send_only_latest_stage():
    # bot 60-kundan 95-kungacha ishlamagan bo'lsa, faqat 90 yuboriladi
    assert due_stage(LAST, date(2026, 12, 5), STAGES) == 90


def test_key_changes_after_new_purchase():
    first = datetime(2026, 9, 1, 10, tzinfo=UTC)
    second = datetime(2026, 11, 10, 10, tzinfo=UTC)
    assert notification_key(5, 60, first) != notification_key(5, 60, second)
    assert notification_key(5, 60, first) == notification_key(5, 60, first)
