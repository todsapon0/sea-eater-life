/* Writes account-config.js at deploy time from environment variables, so the
 * Supabase project URL and key never live in this public repo.
 *
 * Cloudflare Pages -> sea-eater-test -> Settings -> Environment variables (Preview):
 *   SUPABASE_URL              https://<project-ref>.supabase.co
 *   SUPABASE_PUBLISHABLE_KEY  the publishable / anon key  (NEVER the service-role key)
 * Settings -> Builds & deployments:
 *   Build command             node build-config.mjs
 *   Build output directory    /
 *
 * With no variables set (local use, or a fork), it writes empty values and the
 * game falls back to local play instead of breaking.
 */
import { writeFileSync } from 'node:fs';

const url = (process.env.SUPABASE_URL || '').trim();
const key = (process.env.SUPABASE_PUBLISHABLE_KEY || '').trim();
const fail = m => { console.error('build-config: ' + m); process.exit(1); };

// Same shape checks the game applies at runtime, enforced here so a bad value
// fails the build instead of silently shipping a broken or unsafe page.
if (url && !/^https:\/\/[a-z0-9-]+\.supabase\.co$/i.test(url)) fail('SUPABASE_URL must look like https://<project-ref>.supabase.co');

function publicKeyOnly(k) {
  if (!k || /^sb_secret_/i.test(k)) return false;
  if (k.startsWith('sb_publishable_')) return true;
  try { return JSON.parse(Buffer.from(k.split('.')[1], 'base64').toString('utf8')).role === 'anon'; }
  catch { return false; }
}
if (key && !publicKeyOnly(key)) fail('SUPABASE_PUBLISHABLE_KEY is not a publishable/anon key. A service-role key must never be deployed to a browser.');
if (!!url !== !!key) fail('set both SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY, or neither.');

writeFileSync('account-config.js',
  '// Generated at build time by build-config.mjs. Do not commit real values.\n' +
  '// Public project URL and publishable/anon key only. Never use a service-role key.\n' +
  'window.SEA_ACCOUNT_CONFIG = ' + JSON.stringify({ url, publishableKey: key }) + ';\n');

console.log(url
  ? 'build-config: wrote account-config.js for ' + url + ' (key length ' + key.length + ')'
  : 'build-config: no Supabase variables set, wrote empty config (local play only)');
