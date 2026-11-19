import { createBrowserRouter, RouterProvider, NavLink, Outlet, Link, useOutletContext, useParams } from 'react-router';
import { useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import { Badge, Button, Card, CardContent, CardHeader, CardTitle, GenieChat, Skeleton, ResourceStatusIndicator, ResourceStatusProvider } from '@databricks/appkit-ui/react';
import { useAnalyticsQuery } from '@databricks/appkit-ui/react';
import { sql } from '@databricks/appkit-ui/js';

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  `px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
    isActive
      ? 'bg-primary text-primary-foreground'
      : 'text-muted-foreground hover:bg-muted hover:text-foreground'
  }`;

type Persona = 'director' | 'svp';

function NavLinks() {
  return (
    <nav className="flex flex-wrap gap-1">
      <NavLink to="/" end className={navLinkClass}>Overview</NavLink>
      <NavLink to="/cases" className={navLinkClass}>Priority cases</NavLink>
      <NavLink to="/genie" className={navLinkClass}>Ask Genie</NavLink>
    </nav>
  );
}

function Layout() {
  const [persona, setPersona] = useState<Persona>(() => (localStorage.getItem('persona') as Persona) || 'director');
  const [identity, setIdentity] = useState('Signed-in user');
  useEffect(() => { fetch('/api/whoami').then((r) => r.json()).then((data) => setIdentity(data.email)).catch(() => undefined); }, []);
  const switchPersona = (next: Persona) => { localStorage.setItem('persona', next); setPersona(next); };

  return (
    <ResourceStatusProvider>
      <ResourceStatusIndicator />
      <div className="min-h-screen bg-muted/30 flex flex-col">
        <header className="border-b bg-background px-4 md:px-8 py-4 space-y-3">
          <div className="flex flex-wrap items-center gap-3">
            <div><h1 className="text-xl font-semibold">Rebate Integrity Operations</h1><p className="text-xs text-muted-foreground">Synthetic glucose-monitor rebate controls</p></div>
            <Badge className="ml-auto">{identity}</Badge>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <NavLinks />
            <div className="ml-auto flex gap-1" aria-label="Persona lens">
              <Button size="sm" variant={persona === 'director' ? 'default' : 'outline'} onClick={() => switchPersona('director')}>Director lens</Button>
              <Button size="sm" variant={persona === 'svp' ? 'default' : 'outline'} onClick={() => switchPersona('svp')}>SVP lens</Button>
            </div>
          </div>
        </header>
        <main className="flex-1 p-4 md:p-8"><Outlet context={{ persona }} /></main>
      </div>
    </ResourceStatusProvider>
  );
}

const router = createBrowserRouter([
  {
    element: <Layout />,
    children: [
      { path: '/', element: <OverviewPage /> },
      { path: '/cases', element: <CasesPage /> },
      { path: '/cases/:caseId', element: <CasePage /> },
      { path: '/genie', element: <GeniePage /> },
    ],
  },
]);

export default function App() {
  return <RouterProvider router={router} />;
}

function SourceNote({ children }: { children: ReactNode }) { return <p className="text-xs text-muted-foreground mt-3">Source: {children}</p>; }
function Money({ value }: { value: number | string | null | undefined }) { return <>{new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(Number(value || 0))}</>; }

function OverviewPage() {
  const { persona } = useOutletContext<{ persona: Persona }>();
  const { data, loading, error } = useAnalyticsQuery('overview', {});
  const row = data?.[0];
  if (loading) return <Skeleton className="h-80 w-full" />;
  if (error) return <p className="text-destructive">Unable to load governed metrics: {error}</p>;
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div><h2 className="text-3xl font-semibold">From raw claims to investigation action</h2><p className="text-muted-foreground">{persona === 'svp' ? 'Focus on financial exposure, control outcomes, and the highest-priority cases.' : 'Focus on investigation progress, ownership, due dates, and a complete paper trail.'}</p></div>
      <div className="grid gap-4 md:grid-cols-4">
        {[['Suspected cases', row?.suspected_cases ?? 0], ['Estimated exposure', <Money value={row?.estimated_exposure} />], ['Excess units', row?.excess_units ?? 0], ['Cross-channel cases', row?.cross_channel_cases ?? 0]].map(([label, value]) => <Card key={String(label)}><CardHeader><CardTitle className="text-sm text-muted-foreground">{label}</CardTitle></CardHeader><CardContent className="text-2xl font-semibold">{value}</CardContent></Card>)}
      </div>
      <Card><CardHeader><CardTitle>Connected control journey</CardTitle></CardHeader><CardContent className="grid gap-3 md:grid-cols-6 text-sm">{['Synthetic files', 'Lakeflow quality', 'Unity Catalog policies', 'Explainable scoring', 'Lakebase workflow', 'Genie analysis'].map((step, index) => <div className="rounded-md border p-3" key={step}><Badge variant="outline">{index + 1}</Badge><p className="mt-2 font-medium">{step}</p></div>)}</CardContent></Card>
      <SourceNote>user-authorized SQL over `vandelay.rebate_fraud.gold_fraud_cases`; refreshed {row?.data_freshness ?? 'unknown'}.</SourceNote>
    </div>
  );
}

function CasesPage() {
  const { data, loading, error } = useAnalyticsQuery('priority_cases', {});
  if (loading) return <Skeleton className="h-96 w-full" />;
  if (error) return <p className="text-destructive">Unable to load priority cases: {error}</p>;
  return <div className="space-y-5 max-w-7xl mx-auto"><div><h2 className="text-3xl font-semibold">Priority case queue</h2><p className="text-muted-foreground">Highest explainable scores and suspected exposure first.</p></div><Card><CardContent className="p-0 overflow-x-auto"><table className="w-full text-sm"><thead className="bg-muted"><tr>{['Pharmacy', 'Region', 'Score', 'Exposure', 'Why', 'Action'].map((h) => <th className="text-left p-3" key={h}>{h}</th>)}</tr></thead><tbody>{data?.map((row) => <tr className="border-t" key={row.case_id}><td className="p-3 font-medium">{row.pharmacy_name}<div className="text-xs text-muted-foreground">{row.product_code} · {row.review_period}</div></td><td className="p-3">{row.region}</td><td className="p-3"><Badge>{row.fraud_score}</Badge></td><td className="p-3"><Money value={row.estimated_exposure} /></td><td className="p-3 max-w-md">{Array.isArray(row.score_drivers) ? row.score_drivers.join(' · ') : ''}</td><td className="p-3"><Button asChild size="sm"><Link to={`/cases/${row.case_id}`}>Review</Link></Button></td></tr>)}</tbody></table></CardContent></Card><SourceNote>user-authorized SQL over governed gold scoring output; workflow edits are stored separately in Lakebase.</SourceNote></div>;
}

function CasePage() {
  const { caseId = '' } = useParams();
  const params = useMemo(() => ({ caseId: sql.string(caseId) }), [caseId]);
  const evidence = useAnalyticsQuery('case_evidence', params);
  const [operational, setOperational] = useState<any>(null);
  const [saving, setSaving] = useState(false);
  const load = () => fetch(`/api/cases/${caseId}`).then((r) => r.json()).then(setOperational);
  useEffect(() => { void load(); }, [caseId]);
  const save = async () => { setSaving(true); await fetch(`/api/cases/${caseId}`, { method: 'PATCH', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ status: operational.case.status, owner: operational.case.owner || null, priority: operational.case.priority, notes: operational.case.notes || null, dueDate: operational.case.due_date || null }) }); await load(); setSaving(false); };
  if (evidence.loading || !operational) return <Skeleton className="h-96 w-full" />;
  const row = evidence.data?.[0];
  return <div className="space-y-5 max-w-7xl mx-auto"><div><Link className="text-sm text-primary" to="/cases">← Priority cases</Link><h2 className="text-3xl font-semibold mt-2">{row?.pharmacy_name}</h2><p className="text-muted-foreground">Case {caseId}</p></div><div className="grid gap-5 lg:grid-cols-2"><Card><CardHeader><CardTitle>Governed source evidence</CardTitle></CardHeader><CardContent className="grid grid-cols-2 gap-3 text-sm">{[['Claimed units', row?.claimed_units], ['Manufacturer units', row?.manufacturer_units], ['Wholesaler units', row?.wholesaler_units], ['Supported units', row?.supported_units], ['Excess units', row?.excess_units], ['Estimated exposure', <Money value={row?.estimated_exposure} />], ['Medical claims', row?.medical_claim_count], ['Pharmacy claims', row?.pharmacy_claim_count]].map(([label, value]) => <div className="rounded-md border p-3" key={String(label)}><p className="text-muted-foreground">{label}</p><p className="font-semibold">{value}</p></div>)}<div className="col-span-2"><SourceNote>user-authorized SQL over governed gold case evidence.</SourceNote></div></CardContent></Card><Card><CardHeader><CardTitle>Investigation action</CardTitle></CardHeader><CardContent className="space-y-3"><label className="text-sm">Status<select className="mt-1 w-full rounded-md border bg-background p-2" value={operational.case.status} onChange={(event) => setOperational({ ...operational, case: { ...operational.case, status: event.target.value } })}>{['NEW','IN_REVIEW','OUTREACH_SENT','VERIFIED','DISMISSED','ESCALATED','CLOSED'].map((value) => <option key={value}>{value}</option>)}</select></label><label className="text-sm">Owner<input className="mt-1 w-full rounded-md border bg-background p-2" value={operational.case.owner || ''} onChange={(event) => setOperational({ ...operational, case: { ...operational.case, owner: event.target.value } })} /></label><label className="text-sm">Notes<textarea className="mt-1 w-full rounded-md border bg-background p-2 min-h-24" value={operational.case.notes || ''} onChange={(event) => setOperational({ ...operational, case: { ...operational.case, notes: event.target.value } })} /></label><Button onClick={save} disabled={saving}>{saving ? 'Saving…' : 'Save workflow update'}</Button><SourceNote>Lakebase `rebate_ops.cases`; every actual update creates a `case_events` history row.</SourceNote></CardContent></Card></div><Card><CardHeader><CardTitle>AI-assisted explanation</CardTitle></CardHeader><CardContent className="space-y-3"><p>{row?.ai_explanation}</p><p className="font-medium">Suggested next step</p><p>{row?.ai_next_action}</p><p className="text-xs text-muted-foreground">AI-generated—verify against source evidence. Model: {row?.ai_model}.</p></CardContent></Card><Card><CardHeader><CardTitle>Change history</CardTitle></CardHeader><CardContent className="space-y-2">{operational.history.map((item: any) => <div className="border-l-2 pl-3 text-sm" key={item.event_id}><p className="font-medium">{item.event_type} · {item.change_source}</p><p className="text-muted-foreground">{item.changed_at} by {item.changed_by}</p><p>{item.changed_columns?.join(', ')}</p></div>)}</CardContent></Card></div>;
}

function GeniePage() { return <div className="space-y-5 max-w-5xl mx-auto"><div><h2 className="text-3xl font-semibold">Ask governed rebate data</h2><p className="text-muted-foreground">Answers run as the signed-in user so Unity Catalog row filters and masks apply.</p></div><Card><CardContent className="p-0 h-[68vh]"><GenieChat alias="default" /></CardContent></Card><p className="text-xs text-muted-foreground">AI-generated—verify. Inspect the generated SQL and result table in each answer. Source: governed Genie space over `governed_case_features`.</p></div>; }
