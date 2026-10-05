from watchtower.differ import digest, summary, unified


def test_digest_stable():
    assert digest("x") == digest("x")


def test_diff():
    diff = unified("old", "new")
    assert "-old" in diff and "+new" in diff
    assert "-old" in summary(diff)
