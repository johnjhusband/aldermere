import { serve } from '@hono/node-server';
import { Hono } from 'hono';
import { pingDb } from './db.js';

const app = new Hono();

app.get('/', (c) => c.text('Aldermere API. See https://aldermere.world for the app.'));

const PLACEHOLDER_PAGE = (title: string, body: string) => `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>${title} — Aldermere</title>
<style>
  body { font-family: system-ui, -apple-system, sans-serif; max-width: 720px; margin: 4em auto; padding: 0 1.2em; color: #222; line-height: 1.6; }
  h1 { font-size: 1.6em; margin-bottom: .2em; }
  .meta { color: #888; font-size: .9em; margin-bottom: 2em; }
  footer { margin-top: 4em; color: #888; font-size: .85em; }
</style>
</head>
<body>
<h1>${title}</h1>
<div class="meta">Aldermere · Published by Husband, LLC · john@husband.llc</div>
${body}
<footer>This is a placeholder document. The full policy is being prepared and will replace this page before public launch.</footer>
</body>
</html>`;

app.get('/privacy', (c) =>
  c.html(
    PLACEHOLDER_PAGE(
      'Privacy Policy',
      `<p>Aldermere is a personal task-as-fantasy game built by Husband, LLC. While in development we collect only the information needed to operate the service: Google account email, an in-fiction Game Name you choose, the tasks and photos you upload, and AI-generated content tied to your world.</p>
       <p>We do not sell your data. We do not use your data to train third-party models. AI calls (OpenAI) and email delivery (Resend) are made on your behalf using API keys we control; those providers process the data needed to fulfill each request and discard it per their stated retention policies.</p>
       <p>You can request deletion of your account and associated data at any time by emailing <a href="mailto:john@husband.llc">john@husband.llc</a>.</p>`,
    ),
  ),
);

app.get('/terms', (c) =>
  c.html(
    PLACEHOLDER_PAGE(
      'Terms of Service',
      `<p>Aldermere is provided as-is during development by Husband, LLC. By using it you agree not to upload content that violates applicable laws or that exceeds the content rating chosen by the Governor of your world.</p>
       <p>The service may change, pause, or terminate at any time. We will give reasonable notice before shutting a world down and provide an export of your story state if requested.</p>
       <p>Questions: <a href="mailto:john@husband.llc">john@husband.llc</a>.</p>`,
    ),
  ),
);

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
