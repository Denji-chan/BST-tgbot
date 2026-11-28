import asyncio

from services.broadcast import DeliveryStatus, RetryAfter, run_broadcast


class FakeSleep:
    def __init__(self):
        self.calls: list[float] = []

    async def __call__(self, seconds: float) -> None:
        self.calls.append(seconds)


def run(coro):
    return asyncio.run(coro)


def test_counts_delivered_blocked_failed():
    outcomes = {
        10: DeliveryStatus.DELIVERED,
        20: DeliveryStatus.BLOCKED,
        30: DeliveryStatus.FAILED,
        40: DeliveryStatus.DELIVERED,
    }

    async def send(chat_id):
        return outcomes[chat_id]

    sleep = FakeSleep()
    report = run(run_broadcast([(1, 10), (2, 20), (3, 30), (4, 40)], send, sleep=sleep))
    assert (report.total, report.delivered, report.blocked, report.failed) == (4, 2, 1, 1)
    assert report.blocked_user_ids == [2]


def test_rate_limit_sleeps_between_messages():
    async def send(chat_id):
        return DeliveryStatus.DELIVERED

    sleep = FakeSleep()
    run(run_broadcast([(i, i) for i in range(50)], send, rate_per_second=25, sleep=sleep))
    assert len(sleep.calls) == 50
    assert all(abs(s - 0.04) < 1e-9 for s in sleep.calls)
    assert abs(sum(sleep.calls) - 2.0) < 1e-6  # 50 ta xabar >= 2 soniya


def test_retry_after_waits_and_retries():
    attempts = {"n": 0}

    async def send(chat_id):
        attempts["n"] += 1
        if attempts["n"] == 1:
            raise RetryAfter(7)
        return DeliveryStatus.DELIVERED

    sleep = FakeSleep()
    report = run(run_broadcast([(1, 10)], send, sleep=sleep))
    assert report.delivered == 1
    assert attempts["n"] == 2
    assert sleep.calls[0] == 7


def test_retry_after_gives_up_after_max_retries():
    async def send(chat_id):
        raise RetryAfter(1)

    sleep = FakeSleep()
    report = run(run_broadcast([(1, 10), (2, 20)], send, sleep=sleep, max_retries=2))
    assert report.failed == 2
    assert report.delivered == 0


def test_empty_recipients():
    async def send(chat_id):
        raise AssertionError("chaqirilmasligi kerak")

    report = run(run_broadcast([], send, sleep=FakeSleep()))
    assert report.total == 0
