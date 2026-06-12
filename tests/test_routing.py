from agent_routing_kit import estimate_context, route_task


def test_routes_public_capability_by_default():
    result = route_task("write docs and tests for a Python CLI package")

    names = [capability.name for capability, _score in result.matches]

    assert "python-packaging" in names
    assert "documentation" in names
    assert "restricted-operation" not in names


def test_private_lanes_are_opt_in():
    default = route_task("review private broker credential live payload corridor")
    included = route_task(
        "review private broker credential live payload corridor",
        include_private=True,
    )

    assert all(capability.risk == "public" for capability, _score in default.matches)
    assert any(capability.risk != "public" for capability, _score in included.matches)


def test_context_budget_statuses():
    assert estimate_context("short", max_tokens=100).status == "fits"
    assert estimate_context("x" * 320, max_tokens=100).status == "warn"
    assert estimate_context("x" * 500, max_tokens=100).status == "over"
