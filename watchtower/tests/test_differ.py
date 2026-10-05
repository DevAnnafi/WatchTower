from watchtower.differ import digest, summary, unified


def test_digest_stable(): assert digest("x") == digest("x")
def test_diff():
    d = unified("old", "new")
    assert "-old" in d and "+new" in d
    assert "-old" in summary(d)
