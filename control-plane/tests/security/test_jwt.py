from agent_runtime.auth.jwt import TokenError, issue_local_token, verify


def test_signed_local_token_exposes_trusted_identity_claims():
    token = issue_local_token("team-a", "agent:builder", ["task.submit"], "agent")
    claims = verify(token)
    assert claims["tenant"] == "team-a"
    assert claims["sub"] == "agent:builder"
    assert claims["principal_type"] == "agent"


def test_tampered_token_is_rejected():
    token = issue_local_token("team-a", "user:alice", ["task.submit"])
    try:
        verify(f"{token[:-1]}x")
    except TokenError as error:
        assert "signature" in str(error)
    else:
        raise AssertionError("tampered token accepted")


def test_expired_token_is_rejected():
    token = issue_local_token("team-a", "user:alice", ["task.submit"], expires_in_seconds=-1)
    try:
        verify(token)
    except TokenError as error:
        assert "expired" in str(error)
    else:
        raise AssertionError("expired token accepted")


def test_wrong_audience_is_rejected():
    token = issue_local_token(
        "team-a", "user:alice", ["task.submit"], audience="another-service"
    )
    try:
        verify(token)
    except TokenError as error:
        assert "issuer or audience" in str(error)
    else:
        raise AssertionError("invalid token accepted")
