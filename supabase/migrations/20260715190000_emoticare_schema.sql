-- EmotiCare AIoT Internet Service schema for Supabase PostgreSQL.
-- The app's primary migration path is Alembic; this file mirrors the current
-- schema for Supabase CLI/dashboard workflows.

do $$ begin
  create type device_status_enum as enum ('online', 'offline', 'disabled');
exception when duplicate_object then null;
end $$;

do $$ begin
  create type quality_flag_enum as enum ('clean', 'noisy', 'too_short', 'low_confidence');
exception when duplicate_object then null;
end $$;

do $$ begin
  create type reco_status_enum as enum ('success', 'failed', 'limited');
exception when duplicate_object then null;
end $$;

do $$ begin
  create type activity_type_enum as enum ('breathing', 'rest', 'movement', 'journaling');
exception when duplicate_object then null;
end $$;

do $$ begin
  create type safety_flag_enum as enum ('none', 'low', 'medium', 'high');
exception when duplicate_object then null;
end $$;

do $$ begin
  create type period_type_enum as enum ('daily', 'weekly', 'monthly', 'yearly');
exception when duplicate_object then null;
end $$;

do $$ begin
  create type data_quality_enum as enum ('enough_data', 'limited_data');
exception when duplicate_object then null;
end $$;

do $$ begin
  create type media_type_enum as enum ('song', 'podcast');
exception when duplicate_object then null;
end $$;

do $$ begin
  create type media_category_enum as enum (
    'relax',
    'focus',
    'sleep',
    'happy',
    'sad_support',
    'anger_release',
    'energy_recover'
  );
exception when duplicate_object then null;
end $$;

create table if not exists users (
  id varchar(36) primary key,
  name varchar(120) not null,
  pairing_code varchar(20),
  consent_audio_storage boolean not null default false,
  created_at timestamptz not null,
  updated_at timestamptz not null,
  constraint uq_users_pairing_code unique (pairing_code)
);

create table if not exists devices (
  id varchar(36) primary key,
  user_id varchar(36) not null references users(id) on delete cascade,
  name varchar(120) not null,
  device_token_hash varchar(255) not null,
  firmware_version varchar(50),
  last_seen_at timestamptz,
  status device_status_enum not null default 'offline',
  created_at timestamptz not null
);

create index if not exists ix_devices_user_id on devices(user_id);

create table if not exists media_items (
  id varchar(36) primary key,
  media_type media_type_enum not null,
  title varchar(160) not null,
  creator varchar(160),
  category media_category_enum not null,
  duration_sec integer,
  source_url text,
  enabled boolean not null default true
);

create index if not exists ix_media_type_category on media_items(media_type, category);

create table if not exists emotion_sessions (
  id varchar(36) primary key,
  client_session_id varchar(80) not null,
  user_id varchar(36) not null references users(id) on delete cascade,
  device_id varchar(36) not null references devices(id) on delete cascade,
  emotion_label varchar(50) not null,
  confidence_score numeric(4, 3) not null,
  quality_flag quality_flag_enum not null,
  inference_latency_ms integer,
  client_created_at timestamptz not null,
  created_at timestamptz not null,
  constraint uq_emotion_device_client_session unique (device_id, client_session_id)
);

create index if not exists ix_emotion_user_created on emotion_sessions(user_id, created_at);
create index if not exists ix_emotion_device_created on emotion_sessions(device_id, created_at);

create table if not exists recommendation_requests (
  id varchar(36) primary key,
  session_id varchar(36) not null references emotion_sessions(id) on delete cascade,
  request_payload jsonb not null,
  response_payload jsonb not null,
  status reco_status_enum not null default 'success',
  created_at timestamptz not null
);

create index if not exists ix_reco_session_id on recommendation_requests(session_id);

create table if not exists activity_feedback (
  id varchar(36) primary key,
  recommendation_id varchar(36) not null references recommendation_requests(id) on delete cascade,
  activity_type activity_type_enum not null,
  selected boolean not null default false,
  feedback_score integer,
  created_at timestamptz not null
);

create index if not exists ix_activity_feedback_reco_id on activity_feedback(recommendation_id);

create table if not exists conversation_requests (
  id varchar(36) primary key,
  session_id varchar(36) not null references emotion_sessions(id) on delete cascade,
  user_message_summary text,
  response_text varchar(500) not null,
  safety_flag safety_flag_enum not null default 'none',
  created_at timestamptz not null
);

create index if not exists ix_conversation_session_id on conversation_requests(session_id);

create table if not exists tft_reports (
  id varchar(36) primary key,
  user_id varchar(36) not null references users(id) on delete cascade,
  period_type period_type_enum not null,
  period_start date not null,
  period_end date not null,
  tft_cards jsonb not null default '[]'::jsonb,
  emotion_distribution jsonb not null default '{}'::jsonb,
  trend_summary varchar(500),
  data_quality data_quality_enum not null default 'limited_data',
  generated_at timestamptz not null
);

create index if not exists ix_tft_report_user_period on tft_reports(user_id, period_type, period_start);

create table if not exists media_selection_logs (
  id varchar(36) primary key,
  session_id varchar(36) not null references emotion_sessions(id) on delete cascade,
  media_item_id varchar(36) not null references media_items(id) on delete cascade,
  user_intent varchar(120),
  selected_category varchar(50) not null,
  feedback_score integer,
  created_at timestamptz not null
);

create index if not exists ix_media_log_session on media_selection_logs(session_id, created_at);

alter table emotion_sessions drop constraint if exists emotion_sessions_client_session_id_key;
alter table emotion_sessions drop constraint if exists uq_emotion_sessions_client_id;
