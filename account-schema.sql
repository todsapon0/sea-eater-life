-- Run only in an approved dedicated Supabase test project.
create table public.player_characters (
  user_id uuid not null references auth.users(id) on delete cascade,
  character_class text not null check (character_class in ('sea','bloop','maja','crab'))  -- crab = Tenticle Crab, reserved: not selectable in the game yet,
  save_data jsonb not null check (jsonb_typeof(save_data) = 'object'),
  revision bigint not null default 0 check (revision >= 0),
  primary key (user_id, character_class)  -- one account, up to three characters, each with its own level and quest
);
-- Already created the old one-row table? Run once: alter table public.player_characters drop constraint player_characters_pkey, add primary key (user_id, character_class);
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


-- If the table already exists, widen the class list once:
-- alter table public.player_characters drop constraint if exists player_characters_character_class_check;
-- alter table public.player_characters add constraint player_characters_character_class_check check (character_class in ('sea','bloop','maja','crab'));
