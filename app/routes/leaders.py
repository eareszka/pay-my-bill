from flask import Blueprint, render_template, request
from flask_login import current_user

from app.leaderboard import TOP, Period, Scope, rank
from app.models import User

bp = Blueprint("leaders", __name__)


def scopes_for(viewer: User | None) -> dict[Scope, str]:
    # State and city boards use the viewer's own self-reported region.
    tabs = {Scope.GLOBAL: "Global"}
    if viewer and viewer.state:
        tabs[Scope.STATE] = viewer.state
        if viewer.city:
            tabs[Scope.CITY] = viewer.city
    return tabs


@bp.get("/leaders")
def index() -> str:
    viewer: User | None = current_user if current_user.is_authenticated else None
    tabs = scopes_for(viewer)
    scope = request.args.get("scope", Scope.GLOBAL, type=Scope)
    if scope not in tabs:
        scope = Scope.GLOBAL
    period = request.args.get("period", Period.WEEK, type=Period)
    rows = rank(scope, period, viewer)
    shown = rows[:TOP]
    mine = next((row for row in rows if viewer and row.user.id == viewer.id), None)
    return render_template(
        "leaders/index.html",
        rows=shown,
        mine=mine if mine and mine not in shown else None,
        viewer_id=viewer.id if viewer else None,
        tabs=tabs,
        scope=scope,
        period=period,
        Period=Period,
    )
