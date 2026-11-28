from utils.misc.throttling import RateLimiter, ThrottleResult, rate_limit


class FakeClock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


def test_first_request_allowed():
    limiter = RateLimiter(default_limit=1, clock=FakeClock())
    assert limiter.check(1, "start") is ThrottleResult.ALLOWED


def test_fast_repeat_warns_once_then_silent():
    clock = FakeClock()
    limiter = RateLimiter(default_limit=1, clock=clock)
    limiter.check(1, "start")
    clock.now += 0.2
    assert limiter.check(1, "start") is ThrottleResult.FIRST_BLOCK
    clock.now += 0.2
    assert limiter.check(1, "start") is ThrottleResult.BLOCKED


def test_allowed_again_after_limit_passes():
    clock = FakeClock()
    limiter = RateLimiter(default_limit=1, clock=clock)
    limiter.check(1, "start")
    clock.now += 0.5
    limiter.check(1, "start")
    clock.now += 1.0
    assert limiter.check(1, "start") is ThrottleResult.ALLOWED
    # ogohlantirish qayta tiklanadi
    clock.now += 0.1
    assert limiter.check(1, "start") is ThrottleResult.FIRST_BLOCK


def test_users_and_keys_are_independent():
    clock = FakeClock()
    limiter = RateLimiter(default_limit=1, clock=clock)
    limiter.check(1, "start")
    assert limiter.check(2, "start") is ThrottleResult.ALLOWED
    assert limiter.check(1, "help") is ThrottleResult.ALLOWED


def test_handler_limit_overrides_default():
    clock = FakeClock()
    limiter = RateLimiter(default_limit=0.5, clock=clock)
    limiter.check(1, "help", limit=5)
    clock.now += 1
    assert limiter.check(1, "help", limit=5) is ThrottleResult.FIRST_BLOCK


def test_rate_limit_flags():
    assert rate_limit(2, "start") == {"rate_limit": 2, "throttling_key": "start"}
    assert rate_limit(3) == {"rate_limit": 3}
