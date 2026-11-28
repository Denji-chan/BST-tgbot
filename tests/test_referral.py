from services.referral import is_bonus_due, is_valid_referrer
from services.rules import BusinessRules

RULES = BusinessRules()


def test_bonus_due_only_for_first_purchase():
    assert is_bonus_due(True, 350_000, RULES) is True
    assert is_bonus_due(False, 350_000, RULES) is False


def test_bonus_threshold_inclusive():
    assert is_bonus_due(True, 300_000, RULES) is True
    assert is_bonus_due(True, 299_999, RULES) is False


def test_bonus_threshold_configurable():
    assert is_bonus_due(True, 100_000, BusinessRules(referral_min_purchase=100_000)) is True


def test_self_referral():
    assert is_valid_referrer(1, 1) is False
    assert is_valid_referrer(1, 2) is True
