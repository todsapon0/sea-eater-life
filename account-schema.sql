-- Run only in an approved dedicated Supabase test project.
create table public.player_characters (
  user_id uuid primary key references auth.users(id) on delete cascade,
  character_class text not null check (character_class in ('sea','bloop','maja')),
  save_data jsonb not null check (jsonb_typeof(save_data) = 'object'),
  revision bigint not null default 0 check (revision >= 0)
);
alter table public.player_characters enable row level security;
revoke all on public.player_characters from anon, authenticated;
grant select, insert, update on public.player_characters to authenticated;
create policy player_read_own on public.player_characters for select to authenticated
  using ((select auth.uid()) = user_id);
create policy player_insert_own on public.player_characters for insert to authenticated
  with check ((select auth.uid()) = user_id);
create policy player_update_own on public.player_characters for update to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

