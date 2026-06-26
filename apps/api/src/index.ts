import { serve } from '@hono/node-server';
import { Hono } from 'hono';
import { pingDb } from './db.js';

const app = new Hono();

app.get('/', (c) => c.text('Aldermere API. See https://aldermere.world for the app.'));

app.get('/health', (c) =>
  c.json({
    status: 'ok',
    service: 'aldermere-api',
    version: process.env.npm_package_version ?? '0.0.1',
    time: new Date().toISOString(),
  }),
);

app.get('/health/db', async (c) => {
  const r = await pingDb();
  return c.json(r, r.ok ? 200 : 503);
});

const port = Number(process.env.PORT ?? 3000);

serve({ fetch: app.fetch, port }, ({ port }) => {
  console.log(`Aldermere API listening on http://0.0.0.0:${port}`);
});
