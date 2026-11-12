from collections import defaultdict
from dataclasses import dataclass
from datetime import timedelta

from sqlalchemy import select

from app.extensions import db
from app.models import User, as_utc
from app.rewards import rewardable_gifts

# Three or more people helped who got gifts from nobody else and whose accounts
# were made within a day of each other look like one person's sock puppets (#2).
# Flags only ask an admin to look; they never change a ranking.
CLUSTER_SIZE = 3
CLUSTER_WINDOW = timedelta(hours=24)


@dataclass(frozen=True)
class Flag:
    donor: User
    helped: int
    cluster: list[User]
    # What the donor's confirmed gifts to each clustered account add up to.
    cents: dict[int, int]


def _largest_burst(people: list[User]) -> list[User]:
    ordered = sorted(people, key=lambda u: as_utc(u.created_at))
    best: list[User] = []
    start = 0
    for end, person in enumerate(ordered):
        while as_utc(person.created_at) - as_utc(ordered[start].created_at) > CLUSTER_WINDOW:
            start += 1
        if end + 1 - start > len(best):
            best = ordered[start : end + 1]
    return best


def suspected_farms() -> list[Flag]:
    """Donors whose credit comes from a burst of recipients nobody else really gave to.

    A giver doesn't count as someone else if they're banned or one of the
    donor's own recipients, so puppets gifting each other and puppets reused
    after a ban are still caught.
    """
    helped: defaultdict[int, set[int]] = defaultdict(set)
    givers: defaultdict[int, set[int]] = defaultdict(set)
    cents: defaultdict[tuple[int, int], int] = defaultdict(int)
    people: dict[int, User] = {}
    for gift in db.session.scalars(rewardable_gifts()):
        recipient = gift.post.user_id
        helped[gift.donor_id].add(recipient)
        givers[recipient].add(gift.donor_id)
        cents[gift.donor_id, recipient] += gift.amount_cents
        people[recipient] = gift.post.user
    donors = {u.id: u for u in db.session.scalars(select(User).where(User.id.in_(helped)))}
    banned = {id_ for id_, u in donors.items() if u.is_banned}
    flags: list[Flag] = []
    for donor_id, recipients in helped.items():
        if donor_id in banned:
            continue
        insiders = recipients | banned | {donor_id}
        alone = [people[r] for r in recipients if givers[r] <= insiders]
        cluster = _largest_burst(alone)
        if len(cluster) >= CLUSTER_SIZE:
            gifts = {u.id: cents[donor_id, u.id] for u in cluster}
            flags.append(Flag(donors[donor_id], len(recipients), cluster, gifts))
    return sorted(flags, key=lambda f: (-len(f.cluster), f.donor.username))
