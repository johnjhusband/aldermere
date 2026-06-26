import { Pool } from 'pg';

const url = process.env.DATABASE_URL;
if (!url) {
  console.error('DATABASE_URL not set — DB endpoints will fail');
}

export const pool = new Pool({
  connectionString: url,
  max: 10,
  idleTimeoutMillis: 30_000,
  connectionTimeoutMillis: 5_000,
});

export async function pingDb(): Promise<{ ok: true; version: string } | { ok: false; error: string }> {
  try {
    const r = await pool.query<{ version: string }>('SELECT version() as version');
    return { ok: true, version: r.rows[0]?.version ?? 'unknown' };
  } catch (e) {
    return { ok: false, error: e instanceof Error ? e.message : String(e) };
  }
}
