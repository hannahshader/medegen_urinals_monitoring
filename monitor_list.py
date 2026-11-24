#!/usr/bin/env python3
"""Usage: python monitor_list.py 1            # shift 1, today (Central)
          python monitor_list.py 3 2026-11-24
"""
import sys, boto3, psycopg2
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo
from constant import DB_CONFIG

CT = ZoneInfo("America/Chicago")
BUCKET = "tristar-ai"

def window(shift: int, day: date):
    at = lambda dd, h, m: datetime.combine(dd, time(h, m), CT)
    return {
        1: (at(day, 6, 30), at(day, 14, 30)),
        2: (at(day, 14, 30), at(day, 22, 0)),
        3: (at(day - timedelta(1), 22, 30), at(day, 6, 30)),
    }[shift]

SQL = """
SELECT pd.meta->>'start_time', pd.image_url
FROM plastic_defect pd
WHERE pd.team_id = 28 AND pd.factory_id = 76 AND pd.station_id = 1
  AND pd.deleted_at IS NULL
  AND pd.defect_types @> ARRAY['incomplete_box']
  AND pd."timestamp" >= %s AND pd."timestamp" <= %s
ORDER BY pd."timestamp" DESC
"""

def main():
    shift = int(sys.argv[1])
    day = date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else datetime.now(CT).date()
    start, end = window(shift, day)

    conn = psycopg2.connect(**DB_CONFIG)
    s3 = boto3.client("s3")
    with conn.cursor() as cur:
        cur.execute(SQL, (start, end))
        rows = cur.fetchall()

    for start_time, image_url in rows:
        prefix = image_url.removeprefix(f"s3://{BUCKET}/")
        pages = s3.get_paginator("list_objects_v2").paginate(Bucket=BUCKET, Prefix=prefix)
        for page in pages:
            for obj in page.get("Contents", []):
                if obj["Key"].endswith(".mp4"):
                    print(f"{start_time}\ts3://{BUCKET}/{obj['Key']}")

if __name__ == "__main__":
    main()