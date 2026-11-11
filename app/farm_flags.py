from collections import defaultdict
from dataclasses import dataclass
from datetime import timedelta

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
    """Donors whose credit comes from a burst of recipients only they gave to."""
    helped: defaultdict[int, set[int]] = defaultdict(set)
    givers: defaultdict[int, set[int]] = defaultdict(set)
    people: dict[int, User] = {}
    for gift in db.session.scalars(rewardable_gifts()):
        helped[gift.donor_id].add(gift.post.user_id)
        givers[gift.post.user_id].add(gift.donor_id)
        people[gift.post.user_id] = gift.post.user
    flags: list[Flag] = []
    for donor_id, recipients in helped.items():
        only_this_donor = [people[r] for r in recipients if givers[r] == {donor_id}]
        cluster = _largest_burst(only_this_donor)
        if len(cluster) >= CLUSTER_SIZE:
            donor = db.session.get(User, donor_id)
            if donor is not None and not donor.is_banned:
                flags.append(Flag(donor, len(recipients), cluster))
    return sorted(flags, key=lambda f: (-len(f.cluster), f.donor.username))
