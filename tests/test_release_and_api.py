"""Release metadata failures and compatibility of common EOQ entrypoints."""

import subprocess

import pytest

from inventory_models import (
    EPQ,
    BackorderEOQ,
    BasicEOQ,
    DiscountEOQ,
    IncrementalDiscountEOQ,
)
from model_common import OrderConstraints
from scripts.check_release import check_release


@pytest.mark.parametrize(
    "cls,extra",
    [
        (BasicEOQ, {}),
        (EPQ, {"production_rate": 200}),
        (BackorderEOQ, {"shortage_cost": 3}),
        (DiscountEOQ, {"discount_rates": {20: 0.1}}),
        (IncrementalDiscountEOQ, {"discount_rates": {20: 0.1}}),
    ],
)
def test_total_cost_common_api(cls, extra):
    model = cls(price=10, demand_rate=100, ordering_cost=5, holding_rate=0.2, **extra)
    assert model.calculate_total_cost(30) == model.calculate_costs(30).total_cost
    if isinstance(model, DiscountEOQ):
        assert model.calculate_total_cost(30, 7) == pytest.approx(700 + 500 / 30 + 21)


def test_backorder_legacy_metrics_respect_constraints():
    model = BackorderEOQ(
        price=10, demand_rate=100, ordering_cost=5, holding_rate=0.2, shortage_cost=3
    )
    constraints = OrderConstraints(40, 40)
    result = model.solve(constraints)
    metrics = model.calculate_cycle_metrics(constraints)
    assert metrics == {
        "Q_opt": 40,
        "S_max": result.max_inventory,
        "B_max": result.max_backorder,
        "TotalCost": result.costs.relevant_cost,
    }
    assert model.calculate_total_cost(40) - metrics["TotalCost"] == pytest.approx(1000)


def test_graph_uses_requested_policy(monkeypatch):
    import plotly.express as px

    captured = {}

    class Figure:
        def show(self):
            captured["shown"] = True

    def line(**kwargs):
        captured.update(kwargs)
        return Figure()

    monkeypatch.setattr(px, "line", line)
    model = BasicEOQ(price=10, demand_rate=100, ordering_cost=5)
    constraints = OrderConstraints(40, 40)
    model.graph(days_of_operation=250, constraints=constraints)
    assert captured["shown"]
    assert captured["x"][-1] == 250
    assert captured["y"] == pytest.approx(
        model.inventory_level(
            captured["x"], days_of_operation=250, constraints=constraints
        )
    )
    with pytest.raises(ValueError, match="renderer"):
        model.graph("unknown")


@pytest.fixture
def release_repo(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "0.5.0"\n')
    (tmp_path / "CHANGELOG.md").write_text(
        "# Changelog\n\n## Unreleased\n\n## [0.5.0] - 2026-09-09\n\n* Added models.\n\n## [0.4.1] - 2026-08-29\n\n* Fixed bug.\n"
    )
    return tmp_path


def test_release_metadata(release_repo):
    assert check_release(release_repo) == "0.5.0"


@pytest.mark.parametrize(
    "old,new",
    [
        ("0.5.0", "0.6.0"),
        ("2026-09-09", "2026-02-30"),
        ("0.4.1", "0.5.0"),
        ("* Added models.", ""),
        ("## Unreleased", "## Pending"),
    ],
)
def test_release_rejects_drift(release_repo, old, new):
    path = release_repo / "CHANGELOG.md"
    path.write_text(path.read_text().replace(old, new))
    with pytest.raises(ValueError):
        check_release(release_repo)


def test_release_tag_identity_and_annotation(release_repo):
    def git(*args):
        return subprocess.run(
            ["git", *args], cwd=release_repo, check=True, capture_output=True, text=True
        )

    git("init")
    git("add", ".")
    git(
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "-m",
        "release",
    )
    git("tag", "v0.5.0")
    with pytest.raises(ValueError, match="annotated"):
        check_release(release_repo, "v0.5.0")
    git("tag", "-d", "v0.5.0")
    git(
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.invalid",
        "tag",
        "-a",
        "v0.5.0",
        "-m",
        "release",
    )
    assert check_release(release_repo, "v0.5.0") == "0.5.0"
    with pytest.raises(ValueError, match="package version"):
        check_release(release_repo, "v0.4.1")
    git(
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "--allow-empty",
        "-m",
        "next",
    )
    with pytest.raises(ValueError, match="HEAD"):
        check_release(release_repo, "v0.5.0")


def test_ci_restores_annotated_tag_from_remote(release_repo, tmp_path):
    """Reproduce a checkout tag ref pointing at the peeled commit, then recover."""

    def git(*args):
        return subprocess.run(
            ["git", *args], cwd=release_repo, check=True, capture_output=True, text=True
        )

    git("init")
    git("add", ".")
    git(
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "-m",
        "release",
    )
    git(
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.invalid",
        "tag",
        "-a",
        "v0.5.0",
        "-m",
        "release",
    )
    remote = tmp_path / "remote.git"
    git("clone", "--bare", str(release_repo), str(remote))
    git("remote", "add", "origin", str(remote))
    git("update-ref", "refs/tags/v0.5.0", "HEAD")
    with pytest.raises(ValueError, match="annotated"):
        check_release(release_repo, "v0.5.0")
    git("fetch", "--force", "--no-tags", "origin", "refs/tags/v0.5.0:refs/tags/v0.5.0")
    assert check_release(release_repo, "v0.5.0") == "0.5.0"
