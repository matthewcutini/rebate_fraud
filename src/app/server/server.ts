import { createApp, analytics, genie, lakebase, server } from '@databricks/appkit';
import { z } from 'zod';

const updateSchema = z.object({
  status: z.enum(['NEW', 'IN_REVIEW', 'OUTREACH_SENT', 'VERIFIED', 'DISMISSED', 'ESCALATED', 'CLOSED']),
  owner: z.string().max(200).nullable(),
  priority: z.enum(['LOW', 'MEDIUM', 'HIGH', 'URGENT']),
  notes: z.string().max(5000).nullable(),
  dueDate: z.string().date().nullable(),
});

createApp({
  plugins: [
    analytics(),
    genie({ spaces: { default: process.env.DATABRICKS_GENIE_SPACE_ID ?? '' } }),
    lakebase(),
    server(),
  ],
  async onPluginsReady(appkit) {
    appkit.server.extend((app) => {
      app.get('/api/health', (_request, response) => response.json({ status: 'ok' }));
      app.get('/api/whoami', (request, response) => response.json({
        email: request.header('x-forwarded-email') ?? 'local-user',
        user: request.header('x-forwarded-user') ?? 'local-user',
        governance: 'Analytics and Genie execute on behalf of the signed-in user.',
      }));
      app.get('/api/persona-preview', (request, response) => {
        const persona = request.query.persona === 'svp' ? 'svp' : 'director';
        response.json(persona === 'svp'
          ? { persona, headline: 'Financial exposure and control outcome', emphasis: ['estimated exposure', 'priority cases', 'executive questions'] }
          : { persona, headline: 'Investigation flow and complete paper trail', emphasis: ['case status', 'ownership', 'due dates', 'history'] });
      });
      app.get('/api/cases', async (_request, response) => {
        const result = await appkit.lakebase.query(`
          SELECT case_id, pharmacy_name, region, state_code, product_code, review_period,
                 fraud_score, estimated_overpayment, status, owner, priority, due_date,
                 legal_escalation, updated_at
          FROM rebate_ops.cases
          ORDER BY fraud_score DESC, estimated_overpayment DESC, case_id LIMIT 100
        `);
        response.json(result.rows);
      });
      app.get('/api/cases/:caseId', async (request, response) => {
        const caseResult = await appkit.lakebase.query('SELECT * FROM rebate_ops.cases WHERE case_id = $1', [request.params.caseId]);
        if (!caseResult.rows[0]) { response.status(404).json({ error: 'Case not found' }); return; }
        const historyResult = await appkit.lakebase.query(
          `SELECT event_id, event_type, change_source, changed_by, changed_at, changed_columns
           FROM rebate_ops.case_events WHERE case_id = $1
           ORDER BY changed_at DESC, event_id DESC LIMIT 25`,
          [request.params.caseId],
        );
        response.json({ case: caseResult.rows[0], history: historyResult.rows });
      });
      app.patch('/api/cases/:caseId', async (request, response) => {
        const parsed = updateSchema.safeParse(request.body);
        if (!parsed.success) { response.status(400).json({ error: 'Invalid workflow update' }); return; }
        const actor = request.header('x-forwarded-email') ?? 'local-user';
        const client = await appkit.lakebase.pool.connect();
        try {
          await client.query('BEGIN');
          await client.query("SELECT set_config('rebate_ops.change_source', 'APP', true)");
          await client.query("SELECT set_config('rebate_ops.changed_by', $1, true)", [actor]);
          const result = await client.query(
            `UPDATE rebate_ops.cases SET status=$2, owner=$3, priority=$4, notes=$5,
             due_date=$6, updated_at=now() WHERE case_id=$1 RETURNING *`,
            [request.params.caseId, parsed.data.status, parsed.data.owner, parsed.data.priority, parsed.data.notes, parsed.data.dueDate],
          );
          await client.query('COMMIT');
          if (!result.rows[0]) { response.status(404).json({ error: 'Case not found' }); return; }
          response.json(result.rows[0]);
        } catch (error) {
          await client.query('ROLLBACK');
          throw error;
        } finally { client.release(); }
      });
    });
  },
}).catch(console.error);
