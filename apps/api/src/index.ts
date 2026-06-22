import { serve } from '@hono/node-server';
import { Hono } from 'hono';

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

const port = Number(process.env.PORT ?? 3000);

serve({ fetch: app.fetch, port }, ({ port }) => {
  console.log(`Aldermere API listening on http://0.0.0.0:${port}`);
});
