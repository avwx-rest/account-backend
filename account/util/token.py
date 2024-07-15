"""Shared token utilities."""

from datetime import UTC, datetime, timedelta

from bson.objectid import ObjectId

from account.models.token import AllTokenUsageOut, TokenUsage
from account.models.user import User


async def token_usage_for(user: User, days: int) -> list[AllTokenUsageOut]:
    """Get recent token history for a user."""
    days_since = datetime.now(tz=UTC) - timedelta(days=days)
    data = (
        await TokenUsage.find(
            TokenUsage.user_id == ObjectId(user.id),
            TokenUsage.date >= days_since,
        )
        .aggregate(
            [
                {"$project": {"_id": 0, "date": 1, "count": 1, "token_id": 1}},
                {
                    "$group": {
                        "_id": "$token_id",
                        "days": {"$push": {"date": "$date", "count": "$count"}},
                    }
                },
            ]
        )
        .to_list()
    )
    for i, item in enumerate(data):
        data[i]["token_id"] = item["_id"]
        del data[i]["_id"]
    return [AllTokenUsageOut.model_validate(d) for d in data]
