create extension if not exists pgcrypto;

create table if not exists public.chat_messages (
    id uuid primary key default gen_random_uuid(),
    owner_id text not null,
    role text not null check (role in ('user', 'assistant')),
    content text not null,
    created_at timestamptz not null default now()
);

create index if not exists chat_messages_owner_created_idx
    on public.chat_messages (owner_id, created_at);

alter table public.chat_messages enable row level security;

comment on table public.chat_messages is
    'Streamlit 서버의 Supabase secret key를 통해 저장하는 사용자별 연구 대화 기록';

