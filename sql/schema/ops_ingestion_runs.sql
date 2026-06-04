

CREATE  SCHEMA IF NOT EXISTS ops;
CREATE extension if not exists pgcrypto;
CREATE TABLE IF NOT EXISTS ops.ingestion_runs (
    run_id uuid primary key default gen_random_uuid(),
    source text not null,
    feed text not null,
    started_at timestamptz not null DEFAULT now() ,
    finished_at timestamptz ,
    range_start timestamptz not null,
    range_end timestamptz not null,
    rows_fetched bigint not null default 0,
    files_written int not null default 0,
    output_path text,
    result_status text not null default 'running'  check(result_status in('success','failed','running')),
    error_message text
);
CREATE index if not EXISTS idx_ingestion_runs_feed_start_end
on ops.ingestion_runs(feed,range_start, range_end);
