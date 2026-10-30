# Test-only player accounts and server saves

This is a draft integration, not an operational backend until the owner provisions a dedicated Supabase project and verifies it. The owner must approve project creation and any preview configuration separately. Do not connect this draft to real player accounts until security and failure tests pass.

1. In an approved Free test project, run `account-schema.sql` once in the SQL editor. Verify table permissions and RLS; do not use a service-role key in a browser or repository.
2. Set the project's HTTPS URL and **publishable/anon** key in `account-config.js` on a test-only branch. These values are public browser configuration, not database authorization. Never put a secret key, service-role key, passwords, or player saves in source control.
3. Disable public signups and create/invite each of the three independent test users using the provider's admin interface. Each signs in with their own email and password; no shared master account and no public registration button. Configure redirect/email settings as appropriate and do not share credentials in public.
4. Open an isolated HTTPS preview of the configured commit. Sign in, select one character for a new user, play and observe save status. Sign out by closing the tab; sessions are memory-only. On a second device sign in and verify level, XP, items, species and quest state. Test errors, disconnection, overlapping sessions, and user A attempting to read/update user B via the API.
5. Existing local saves are not automatically migrated. The local-play option continues to use existing keys and export remains a local-backup feature. Do not clear production data. The initial server character is new; migration/import requires separate work and consent.

The server adapter coalesces local writes and uses a revision predicate to detect concurrent updates; on a failure or conflict it stops subsequent writes and displays a warning. It does not yet provide a retry/export of unsaved account progress. Closing the page while a save is pending can lose that progress. These are release blockers until tested and resolved. No background multiplayer is included.

Supabase Free projects may pause after a period of low activity; check [project pausing](https://supabase.com/docs/guides/platform/free-project-pausing). Maintain a private backup strategy and test restoration. Confirm free-tier limitations directly in the owner account before provisioning.

