create table if not exists audits(
  id serial primary key,
  task_id text not null,
  state text not null,
  created_at timestamptz default now()
);