"""Serving layer: merges the batch and speed views at query time.

This merge is the crux of a Lambda architecture: callers always query
*through* `merge_views()` rather than either underlying table directly,
so they see batch-layer completeness (the full history, as of the last
batch run) plus speed-layer recency (everything since) without the batch
layer needing to run continuously.
"""
import pandas as pd

_SUMMARY_COLUMNS = [
    "customer_id",
    "name",
    "email",
    "country",
    "order_count",
    "total_spent",
    "last_order_date",
]


def merge_views(batch_df: pd.DataFrame, speed_df: pd.DataFrame) -> pd.DataFrame:
    """Combine the batch view (authoritative up to the watermark) with the
    speed view (increments since the watermark) into one served result.

    An outer join on `customer_id` so customers who only appear in the
    speed layer (e.g. a brand-new customer whose first order hasn't gone
    through a batch run yet) are still included; counts/spend are summed
    and the latest order date across both layers wins.
    """
    if speed_df.empty:
        return batch_df.reindex(columns=_SUMMARY_COLUMNS).copy()
    if batch_df.empty:
        return speed_df.reindex(columns=_SUMMARY_COLUMNS).copy()

    merged = batch_df.merge(
        speed_df, on="customer_id", how="outer", suffixes=("_batch", "_speed")
    )
    merged["name"] = merged["name_batch"].combine_first(merged["name_speed"])
    merged["email"] = merged["email_batch"].combine_first(merged["email_speed"])
    merged["country"] = merged["country_batch"].combine_first(merged["country_speed"])
    merged["order_count"] = (
        merged["order_count_batch"].fillna(0) + merged["order_count_speed"].fillna(0)
    ).astype(int)
    merged["total_spent"] = (
        merged["total_spent_batch"].fillna(0) + merged["total_spent_speed"].fillna(0)
    ).round(2)
    merged["last_order_date"] = merged[
        ["last_order_date_batch", "last_order_date_speed"]
    ].max(axis=1)
    return merged[_SUMMARY_COLUMNS]
