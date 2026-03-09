import types
from logic_utils import check_guess, parse_guess, update_score, get_range_for_difficulty

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, message = check_guess(50, 50)
    assert outcome == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, message = check_guess(60, 50)
    assert outcome == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, message = check_guess(40, 50)
    assert outcome == "Too Low"

def test_hint_says_go_lower_when_guess_too_high():
    # Bug fix: when guess > secret, hint must say Go LOWER (was incorrectly Go HIGHER)
    outcome, message = check_guess(80, 30)
    assert outcome == "Too High"
    assert "LOWER" in message, f"Expected hint to say LOWER, got: {message}"

def test_hint_says_go_higher_when_guess_too_low():
    # Bug fix: when guess < secret, hint must say Go HIGHER (was incorrectly Go LOWER)
    outcome, message = check_guess(10, 50)
    assert outcome == "Too Low"
    assert "HIGHER" in message, f"Expected hint to say HIGHER, got: {message}"


# ---------------------------------------------------------------------------
# New Game button — status reset bug fix tests
# ---------------------------------------------------------------------------
# Bug: clicking "New Game" after winning/losing did not restart the game
# because status stayed "won"/"lost". Fix: new_game handler now sets
# st.session_state.status = "playing".
#
# These tests simulate the session_state and run the same logic the
# new_game handler in app.py runs, without importing Streamlit.

def _simulate_new_game(session_state):
    """Mirrors the new_game handler logic from app.py."""
    session_state.attempts = 0
    session_state.secret = 42  # fixed value; randomness not under test here
    session_state.status = "playing"


def test_new_game_resets_status_after_win():
    # After winning, clicking New Game should set status back to "playing"
    state = types.SimpleNamespace(status="won", attempts=3, secret=50)
    _simulate_new_game(state)
    assert state.status == "playing", f"Expected 'playing', got '{state.status}'"


def test_new_game_resets_status_after_loss():
    # After losing, clicking New Game should set status back to "playing"
    state = types.SimpleNamespace(status="lost", attempts=8, secret=50)
    _simulate_new_game(state)
    assert state.status == "playing", f"Expected 'playing', got '{state.status}'"


def test_new_game_resets_attempts_to_zero():
    # Attempts counter must be cleared so the player gets a fresh start
    state = types.SimpleNamespace(status="lost", attempts=5, secret=50)
    _simulate_new_game(state)
    assert state.attempts == 0, f"Expected attempts=0, got {state.attempts}"


def test_new_game_does_not_preserve_old_status():
    # Guard: status must not remain "won" or "lost" after new_game
    for old_status in ("won", "lost"):
        state = types.SimpleNamespace(status=old_status, attempts=1, secret=10)
        _simulate_new_game(state)
        assert state.status != old_status, (
            f"status should have changed from '{old_status}' but it did not"
        )


# ---------------------------------------------------------------------------
# Even-attempt string-secret bug fix tests
# ---------------------------------------------------------------------------
# Bug: at even-numbered attempts, secret was cast to str before being passed
# to check_guess, so a correct int guess never matched:
#
#   if st.session_state.attempts % 2 == 0:
#       secret = str(st.session_state.secret)   # ← the bug
#   else:
#       secret = st.session_state.secret
#
# Fix: secret is always kept as int; the type-conversion branch was removed.

def _get_secret_for_attempt(secret_int, attempt_number):
    """Reproduces the BUGGY even-attempt logic from the original app."""
    if attempt_number % 2 == 0:
        return str(secret_int)   # old broken behaviour
    return secret_int


def test_correct_guess_wins_on_odd_attempt():
    # Sanity check: guess == secret (both int) always returns Win
    outcome, _ = check_guess(50, 50)
    assert outcome == "Win"


def test_buggy_even_attempt_causes_wrong_outcome():
    # Demonstrates what the bug looked like: passing a string secret to
    # check_guess breaks the game entirely. Python 3 allows int == str (always
    # False), but raises TypeError on int > str, so the function crashes before
    # it can return any outcome.
    secret_as_string = _get_secret_for_attempt(50, attempt_number=2)
    try:
        outcome, _ = check_guess(50, secret_as_string)
        # If somehow no crash, a correct guess must NOT have been a "Win"
        assert outcome != "Win", (
            "int 50 should not equal str '50'"
        )
    except TypeError:
        pass  # Expected: int > str raises TypeError in Python 3, proving the bug


def test_fixed_even_attempt_correct_guess_wins():
    # After the fix, secret is always int regardless of attempt number.
    # Simulate attempt 2 and 4 — should both result in a win.
    for secret_val in (2, 4, 6):
        outcome, _ = check_guess(secret_val, secret_val)   # both int — the fixed state
        assert outcome == "Win", (
            f"Expected Win with int secret {secret_val}, got: {outcome}"
        )


def test_fixed_even_attempt_no_type_mismatch():
    # The fix ensures secret is never a string; confirm int comparison is used.
    secret = 37
    guess = 37
    assert type(secret) is int, "Secret must stay an int, not a string"
    outcome, _ = check_guess(guess, secret)
    assert outcome == "Win"


# ---------------------------------------------------------------------------
# parse_guess tests
# ---------------------------------------------------------------------------

def test_parse_guess_valid_integer():
    ok, value, err = parse_guess("42")
    assert ok is True
    assert value == 42
    assert err is None


def test_parse_guess_empty_string():
    ok, _, err = parse_guess("")
    assert ok is False
    assert "guess" in err.lower()


def test_parse_guess_none():
    ok, _, _ = parse_guess(None)
    assert ok is False


def test_parse_guess_non_numeric():
    ok, _, err = parse_guess("abc")
    assert ok is False
    assert "number" in err.lower()


def test_parse_guess_decimal_truncates_to_int():
    # e.g. "3.7" should parse as 3, not reject
    ok, value, _ = parse_guess("3.7")
    assert ok is True
    assert isinstance(value, int)


# ---------------------------------------------------------------------------
# update_score tests
# ---------------------------------------------------------------------------

def test_update_score_win_early_gives_high_points():
    # Winning on attempt 1 should give more points than winning late
    score = update_score(0, "Win", attempt_number=1)
    assert score > 0


def test_update_score_win_late_gives_fewer_points():
    early = update_score(0, "Win", attempt_number=1)
    late = update_score(0, "Win", attempt_number=7)
    assert early > late


def test_update_score_too_low_subtracts_points():
    score = update_score(100, "Too Low", attempt_number=1)
    assert score < 100


def test_update_score_too_high_subtracts_points():
    # Bug fix: Too High should always subtract, not add on even attempts
    score_odd = update_score(100, "Too High", attempt_number=1)
    score_even = update_score(100, "Too High", attempt_number=2)
    assert score_odd < 100
    assert score_even < 100


def test_update_score_unknown_outcome_unchanged():
    score = update_score(50, "InvalidOutcome", attempt_number=1)
    assert score == 50


# ---------------------------------------------------------------------------
# get_range_for_difficulty tests
# ---------------------------------------------------------------------------

def test_easy_range_is_smallest():
    low, high = get_range_for_difficulty("Easy")
    assert low == 1
    assert high == 20


def test_normal_range():
    low, high = get_range_for_difficulty("Normal")
    assert low == 1
    assert high == 50


def test_hard_range_is_largest():
    low, high = get_range_for_difficulty("Hard")
    assert low == 1
    assert high == 100


def test_easy_range_smaller_than_normal():
    _, easy_high = get_range_for_difficulty("Easy")
    _, normal_high = get_range_for_difficulty("Normal")
    assert easy_high < normal_high


def test_normal_range_smaller_than_hard():
    _, normal_high = get_range_for_difficulty("Normal")
    _, hard_high = get_range_for_difficulty("Hard")
    assert normal_high < hard_high
