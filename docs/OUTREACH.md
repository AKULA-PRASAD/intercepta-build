# Partner / collaborator outreach — drafts (for Prasad to review & send)

**How to use.** These are ready-to-adapt drafts, not messages I will send. Before sending: confirm the current
PI/contact for each group (people move labs), fill the `[...]` placeholders, and attach nothing controlled — just
the public repo link and, if asked, the brief/SAP. Keep it short; the repo does the convincing.

**Core value proposition (the honest hook — one paragraph):**
> We built and openly released a fully pre-registered, leakage- and confound-controlled engine for transcriptomic
> cancer drug-response prediction, and used it to establish — rigorously, with two decisive pre-registered negatives
> — that *baseline* molecular profiles (RNA and proteomics) predict cancer type and proliferation, **not**
> drug-specific patient response, and that a functional layer *inferred* from cell lines does not replicate across
> patient cohorts. The evidence-forced conclusion is that drug-specific signal must be **measured functionally in
> the patient**. We have the validated analysis layer, the frozen prospective analysis plan, and the power
> calculation ready; we are looking for a functional-precision partner with the one irreplaceable asset — patient
> samples and ex-vivo/organoid screening capacity.

Repo (public, reproducible): https://github.com/AKULA-PRASAD/intercepta-build · start at `REVIEWERS.md`.

---

## Template — cold email (adapt per recipient)

**Subject:** Functional-precision collaboration — a rigorously-bounded drug-response engine + a ready prospective plan

Dear [Dr. / Prof. lastname],

I'm Prasad Akula. I've built an open, pre-registered computational engine for cancer drug-response prediction and
used it to map — under a strict falsify-first protocol — exactly where transcriptomic prediction works and where it
fails. The honest result: baseline molecular profiles (we tested RNA and proteomics) capture cancer type and
proliferation, not drug-specific response; in real patients the apparent signal is entirely cancer-type confounding
(within-cancer AUROC 0.50, well-powered null); and a functional-dependency layer *inferred* from cell lines beat the
FLT3-ITD biomarker in one AML cohort but **failed to replicate** in an independent one. Everything is public and
reproducible: [repo link].

The evidence points to one conclusion I think your group is uniquely positioned to test: **drug-specific signal must
be measured functionally in the patient, not inferred.** I have a frozen, pre-registered analysis plan and power
calculation for a prospective functional-precision cohort (design target ~200 patients; ex-vivo/organoid drug
response + matched RNA/WES + outcome), with the analysis layer already validated and ready to run unchanged.

Would you be open to a short call to explore whether your [ex-vivo drug-screening / organoid / BeatAML-type]
platform and this ready, rigorous analysis layer could be combined? I'm happy to send the one-page brief and the
analysis plan. Either outcome of the study is publishable — the design cannot produce an uninformative answer.

Best regards,
Prasad Akula · akula.pra@northeastern.edu · [affiliation]

---

## Tailored one-liners (swap into the second paragraph)

- **OHSU / Beat AML program (functional genomic AML).** "Your Beat AML resource is exactly the design that gave our
  one genuine drug-specific signal — and our functional-inference result was built on, and honestly bounded by, it.
  A prospective, outcome-linked extension is the natural next step, and our analysis layer already speaks BeatAML's
  format."
- **FIMM / Helsinki (functional precision medicine, DSRT).** "We used your published AML functional-precision cohort
  (Zenodo 7370747) as the independent replication set that falsified our inferred layer — a result that argues
  directly for measuring dependency, as your DSRT platform does, rather than inferring it. I'd value your read on the
  measured-vs-inferred question our plan is built around."
- **Patient-derived-organoid drug-screening groups (solid tumors).** "Our results are AML-anchored; the open question
  is whether measured functional response predicts outcome in solid tumors, where your organoid drug-screening
  platform is the ideal instrument and our engine provides the pre-registered, confound-controlled analysis."

## Elevator version (for a warm intro / conference)
"I've open-sourced a pre-registered drug-response engine and proved, with two decisive negatives, that baseline
omics can't predict patient drug response — you have to *measure* functional response in the patient. I have the
validated analysis layer and a frozen prospective plan; I'm looking for a functional-precision lab to run it."

## Targeting notes (confirm current contacts before sending)
- Functional-precision oncology / ex-vivo AML drug screening + omics programs (e.g. OHSU Knight; FIMM Helsinki).
- Large-scale functional-genomics groups (DepMap/PRISM ecosystem) for methods collaboration.
- Patient-derived-organoid drug-screening consortia for the solid-tumor extension.
- What to attach when asked: repo link (public), `docs/COLLABORATION_BRIEF.md`, `prereg/TRACK1_SAP.md`. Never attach
  or reference any controlled/patient-level data.

## Integrity guardrails (apply to every message)
- Lead with the rigorous negatives; do **not** imply a validated clinical predictor exists.
- No invented affiliations, prior relationships, results, or metrics beyond what the LEDGER supports.
- Sending is a human action taken by Prasad; these drafts are not to be auto-sent.
