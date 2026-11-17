# Rebate Fraud Prevention Use Case

> `[YOUR WORDS]` This is a working draft. Rewrite the narrative in your own words before submission.

## 1. One-Line Outcome

`[YOUR WORDS]` Reduce fraudulent rebate leakage by recovering 25% of the current $10 million annual overpayment exposure—an illustrative $2.5 million per year—while creating an auditable path from suspicious claim to pharmacy response and legal escalation.

## 2. The Problem in the Customer's Words

`[YOUR WORDS]` We cannot reliably determine whether every rebate claim is supported by product purchased. A pharmacy may request rebates for more units than it bought, submit the same underlying activity through both medical and pharmacy insurance channels, or appear under several names and identifiers. Our analysts must reconcile manufacturer sales, wholesaler distribution records, and rebate claims while comparing names, addresses, phone numbers, and fax numbers to recognize that apparently different claimants are the same business. The pharmacy population also changes as locations open and close. This fragmented process contributes to an estimated $10 million in fraudulent overpayments each year and leaves communications, responses, and legal escalations without one complete paper trail.

## 3. Why Now

- `[YOUR WORDS]` **Growth increases exposure:** Expansion into additional markets will introduce more pharmacies, claims, and identity changes. If the current control gap scales with the business, fraudulent overpayments will grow with it.
- `[YOUR WORDS]` **Gross-to-net pressure is increasing:** Life Sciences manufacturers face continued pressure to control rebate leakage and explain where contracted dollars go. `[CHECK]`
- `[YOUR WORDS]` **Auditability matters:** Finance, compliance, and legal stakeholders increasingly expect traceable evidence for payment holds, recoveries, disputes, and escalation decisions. `[CHECK]`

## 4. Personas

### Director of Rebate Operations

`[YOUR WORDS]` The Director runs the operational investigation process. Each month, they must tell the SVP which suspected cases were verified as fraud, how investigations are progressing, whether pharmacies responded, and which cases require escalation. Their primary KPI is the number and rate of suspected fraud cases verified as real fraud; they also monitor investigation aging and the completeness of the evidence trail.

### SVP of Contracting and Rebates

`[YOUR WORDS]` The SVP owns the financial and control outcome across contracting and rebate operations. Today, their team reconciles sales, distribution, and rebate records while manually resolving pharmacy identities and tracking outreach across disconnected tools. Each quarter, the SVP reports recovered overpayments and remaining fraud exposure to an executive finance or risk committee. Their primary KPI is dollars in fraudulent overpayments recovered.

## 5. Today Versus Tomorrow

| Today | Tomorrow |
|---|---|
| Analysts compare names, addresses, phone numbers, fax numbers, and incomplete identifiers manually. | Continuously refreshed entity resolution links aliases and channel-specific records to a governed pharmacy identity with match evidence. |
| Medical and pharmacy claims are reviewed separately, allowing duplicate activity to escape detection. | Cross-channel claims are reconciled together and flagged when the same underlying activity appears more than once. |
| Rebate quantities are difficult to reconcile against the quantities each entity purchased. | Claims are compared with manufacturer sales and third-party distribution records before suspicious cases enter review. |
| Outreach, responses, decisions, and legal escalation evidence are fragmented. | A case workflow preserves the full communication trail, resolution status, recovery amount, and escalation history. |

## 6. Value Hypothesis: Fraud Prevention

| Value driver | Current baseline | Expected change | Assumption | Illustrative value |
|---|---:|---:|---|---:|
| Fraudulent overpayments recovered | $0 systematically attributed to the new capability | Recover 25% of estimated annual exposure | `$10M exposure` is the customer-provided annual estimate; `25% recovery` is a balanced planning target, not a guaranteed result | $2.5M annually |
| Suspected cases verified as fraud | Baseline to be measured during prototype validation | Increase the verified-fraud conversion rate by 20% | `20% improvement` assumes entity resolution and cross-channel evidence reduce false positives; the current conversion rate is unknown | Operational benefit; dollar value is included only when tied to recovered payments |
| Investigation effort | Baseline to be measured during prototype validation | Reduce analyst effort per investigated case by 30% | `30% reduction` assumes automated reconciliation and one case record replace repeated manual matching; current hours per case are unknown | Capacity benefit; no dollar value claimed until loaded labor cost is validated |
| Fraud exposure during growth | $10M annually at the current operating scale | Prevent the known control gap from scaling proportionally with expansion | Assumes fraud exposure would otherwise grow with claim volume; no growth rate is yet approved | Avoided future loss is excluded from the $2.5M recovery estimate |

## 7. The Data

All prototype data will be synthetic and vendor-neutral.

| Source | Representative tables | Approximate scale | Known data problems |
|---|---|---:|---|
| Manufacturer sales | `sales_orders`, `sales_order_lines`, `shipments` | `[ASSUMPTION]` 150,000 line items per year | Returns, shipment timing, unit-of-measure differences, and sales accounts that do not match claim identifiers |
| Wholesaler distribution feeds | `wholesaler_shipments`, `wholesaler_returns`, `wholesaler_inventory` | `[ASSUMPTION]` 250,000 transactions per year | Different customer identifiers by wholesaler, delayed reports, corrections, returns, and inconsistent units of measure |
| Third-party 867 distribution feed | `distribution_867_transactions` | `[ASSUMPTION]` 300,000 transactions per year | Late files, corrected files, duplicate transmissions, and changing distributor customer identifiers |
| Rebate processor | `rebate_claims`, `rebate_claim_lines` | 120,000 claims per year, based on 10,000 claims per month | Medical and pharmacy channels use different field names; claims may lack a shared pharmacy identifier |
| Pharmacy identity reference | `pharmacy_source_records`, `pharmacy_identity_links` | 500 active pharmacies; `[ASSUMPTION]` 750 active and historical identities | Openings, closures, aliases, spelling differences, reused addresses, and inconsistent phone and fax formatting |
| Investigation workflow | `fraud_cases`, `case_events`, `communications`, `recoveries` | `[ASSUMPTION]` 2,000 case events per year | Communications stored separately, inconsistent statuses, missing response dates, and incomplete escalation history |

The planted data issues will include late 867 files, duplicate records, channel-specific field names, pharmacy aliases, missing identifiers, address variations, reformatted phone and fax numbers, closures, and new openings. The exact planted patterns and rates require separate approval before data generation.

## 8. How the Six Stages Serve the Story

- **Lakeflow:** Ingests changing manufacturer sales, wholesaler, 867, rebate, identity, and case-event feeds; handles late and corrected records without duplicating claims.
- **Unity Catalog:** Gives the SVP governed, traceable definitions for pharmacy identity, purchased quantity, claimed quantity, suspected fraud, verified fraud, and recovered dollars.
- **Lakebase:** Serves the current operational case state, communications, responses, assignments, and legal escalation trail needed by investigators and the application.
- **ML or GenAI:** Uses fuzzy entity resolution and anomaly scoring to connect pharmacy aliases and prioritize quantity or cross-channel discrepancies; GenAI drafts grounded outreach and legal case summaries for human review.
- **Genie:** Lets the SVP ask governed questions about fraud exposure, verified cases, recoveries, channels, regions, and investigation aging without waiting for a custom report.
- **Databricks App:** Gives the operations team one place to review evidence, contact a pharmacy, record its response, resolve a case, or escalate it to legal.

Each stage consumes governed output from the preceding stage: ingested records become governed evidence; governed identities and signals feed operational cases; case and feature data support AI; AI-enriched governed data supports Genie; and the App operationalizes the same cases, evidence, and recommendations.

## 9. What We Will Not Build

- A connection to real customer, pharmacy, patient, prescriber, payer, distributor, or rebate-processor data.
- Automated denial, payment withholding, recovery, or legal action without human approval.
- A production master-data-management replacement for every pharmacy in the United States.
- A complete contract adjudication, chargeback, Medicaid rebate, or government-pricing platform.
- Direct email, fax, or legal-system integration; the prototype records synthetic communications and responses.
- A clinical fraud, patient eligibility, prescriber behavior, or medical-necessity solution.
- A guaranteed financial result; the value case remains a hypothesis until baselines and recovery outcomes are validated.

## 10. Challenge Assessment

| Challenge | Why it weakens the case | How to make it specific | Stage necessity check |
|---|---|---|---|
| The story could sound like generic duplicate detection. | Many demos flag duplicate rows without reflecting rebate operations. | Demonstrate one pharmacy operating through aliases, both claim channels, excess claimed quantity, outreach, response, recovery, and escalation. | Lakeflow is needed to reconcile late, corrected, multi-source records. |
| Entity resolution may look like an internal data-cleaning exercise. | Identity matching alone does not prove business value. | Show how a resolved identity changes the payable quantity, connects cross-channel claims, and creates a recoverable case. | Unity Catalog is needed for governed identity, lineage, and consistent fraud metrics. |
| Case management may appear bolted onto analytics. | A dashboard that stops at a score does not complete the customer workflow. | Make the paper trail the operational outcome: evidence, outreach, response, decision, recovery, and legal escalation. | Lakebase is needed for low-latency mutable case and communication state. |
| AI could be difficult to defend without labeled fraud history. | A black-box fraud score would reduce trust and demo credibility. | Use explainable fuzzy-match features and anomaly signals; label outcomes only after human verification. Ground generated text solely in case evidence. | ML/GenAI is needed for changing identities, prioritization, and evidence-grounded drafting—not final adjudication. |
| Genie could duplicate the App. | Two interfaces with the same purpose look disconnected. | Use Genie for executive and investigative questions across governed history; use the App for case actions and paper-trail updates. | Genie is needed for flexible governed analysis; the App is needed for operational workflow. |
| The $2.5M value may look invented. | Recovery rates are not yet validated. | Keep the $10M exposure tied to the customer scenario, label 25% as a planning assumption, and show sensitivity at prototype review. | The connected journey must generate measurable verified cases and recoveries to test the hypothesis. |
| Named vendors or real entities would make the submission look customer-specific or internal. | It could violate synthetic-data requirements and distract from the reusable industry pattern. | Keep all organizations, systems, pharmacies, communications, and identities synthetic and vendor-neutral. | Every stage operates only on synthetic records. |

`[YOUR WORDS]` The strongest demo is one traceable case: two apparently different pharmacy records are resolved to one entity; medical and pharmacy claims overlap; total claimed quantity exceeds documented purchases; an investigator reviews the evidence; outreach and a synthetic response are recorded; the case is verified; recovery is entered; and repeated behavior is escalated to legal with the complete paper trail.
