# How We Know It Is Real — Validation Philosophy

*PART FOUR: COMMITMENTS*

---

The most important question for any clinical decision support system is also the simplest: how do we know it works? Without honest answers to this question, every other commitment in this book is theatrical. Architecture means nothing if validation cannot demonstrate it produces correct outputs. Universality means nothing if it cannot be verified disease by disease. Scientific honesty means nothing if it does not extend to honesty about evidence supporting claims.

This chapter is INTERCEPTA's validation philosophy: the methodologies and practices that ground claims in evidence rather than aspiration. The chapter walks through the validation problem in computational medicine, why benchmarks lie, falsification as discipline, internal and external validation, prospective vs retrospective evaluation, cross-population validation, mechanism validation, the regulatory pathway, and continuous validation in deployment. Each section specifies what we do, why we do it that way, and what the alternatives are.

## The Validation Problem in Computational Medicine

The translation gap between computational prediction and clinical reality is one of the central problems in healthcare AI. Most computational medicine claims fail to translate clinically. The reasons are structural, not incidental.

Benchmarks reward gaming. Public benchmarks like those used in single-cell drug response prediction provide standardized evaluation that lets methods be compared. They also create incentives to optimize for benchmark performance specifically. Methods that score well on benchmarks may not generalize to real clinical contexts. Researchers know this; they often optimize anyway because publications and citations follow benchmark wins.

Distribution shift undermines deployment. A method trained and validated on one distribution of data may fail on a different distribution. Clinical populations differ from research populations. Clinical samples differ from research samples in processing and quality. The shift between training and deployment distributions can be enormous, and it produces failures that are not predictable from training-distribution validation.

Retrospective overfitting masks reality. Methods evaluated on retrospective data — outcomes already observed — can be inadvertently fit to those outcomes through choices made during method development. Even with appropriate cross-validation, the development process biases the method toward retrospective performance in ways that do not transfer to prospective use.

Lack of prospective validation is endemic. Most computational medicine methods are validated only on retrospective data. Prospective validation — running the method, applying it to decisions, observing outcomes, comparing to predictions — is rare. It is also expensive, slow, and ethically complex. The gap between retrospective validation and prospective performance is real and often large.

Patient-level performance differs from population-level performance. A method that performs well on a population in aggregate may perform variably across individuals. The variation is what matters clinically: the patient in front of the clinician deserves a prediction that is accurate for them, not a prediction that is accurate on average.

These problems are not specific to INTERCEPTA. They are characteristic of computational medicine. INTERCEPTA's commitment is to address them rather than to ignore them.

## Why Benchmarks Lie

The case against pure benchmark optimization is concrete. Two examples from the field illustrate the problem.

The Elmarakeby et al. evaluation (Dana Farber, October 2025) tested whether single-cell foundation models were better at predicting patient-level cancer outcomes than simpler baselines. The expectation, given enthusiastic field adoption of foundation models, was that they would outperform substantially. The finding was that they did not. Foundation models showed limited advantages over simpler approaches for patient-level outcome prediction. This was a published, peer-reviewed finding that contradicted prevailing assumptions.

Compare to the scDrugMap evaluation from earlier in 2025: foundation models including scFoundation showed impressive performance at cell-level drug response prediction, with F1 scores around 0.97 in pooled evaluation. This was also published and peer-reviewed.

Are foundation models good or bad for biomedical AI? The benchmarks said both. The resolution is that they were measuring different things. Cell-level drug response prediction and patient-level cancer outcome prediction are different problems. Methods optimized for one do not necessarily excel at the other. Benchmarks for each task tell you how the method does on that task, not on the other.

This is the structural problem with benchmark optimization. A benchmark measures method performance on the specific task the benchmark defines. It does not measure performance on the clinical task that motivates building the method in the first place. The gap between benchmark task and clinical task is where benchmarks lie.

INTERCEPTA's response is not to ignore benchmarks. Benchmarks have legitimate uses: they enable method comparison, they characterize specific capabilities, they inform engineering choices. The response is to refuse to confuse benchmark performance with clinical capability. Benchmark wins are inputs to validation, not validation in themselves.

## Falsification as Discipline

Karl Popper's distinction between confirmation and falsification matters here. Confirmation seeks evidence that supports a claim; falsification seeks evidence that refutes it. Strong validation requires falsification, not just confirmation.

Most computational medicine methodology focuses on confirmation: experiments designed to show that the method works. INTERCEPTA's commitment is that every claim is paired with what would falsify it, and that falsification experiments are designed and run.

For a claim like "MC-FMA outperforms baselines on cell-level drug response prediction," falsification looks like: explicit baselines defined in advance, evaluation on data not used in method development, performance differences large enough to be clinically meaningful, statistical significance with appropriate corrections. If the falsification fails — if MC-FMA does not actually outperform baselines on independent data — the claim is abandoned, not patched until the falsification stops failing.

For a claim like "the system can handle autoimmune disease," falsification looks like: cellular data from autoimmune cohorts processed through the system, mechanism inference produced, predictions made, validation against known autoimmune drug responses, characterization of where the system fails. If the falsification reveals systematic problems — if the mechanism inference does not capture autoimmune biology, if predictions for autoimmune drugs are uncalibrated — the claim that the system handles autoimmune is not made.

The discipline of falsification protects against the field's characteristic failure mode of overclaim. Claims survive only when falsification has been attempted seriously and not succeeded. Claims that have not been tested against falsification are not made publicly.

## Internal Validation Methodology

Internal validation is what INTERCEPTA does before any external claim. The methodology is structured to catch problems before they become public commitments.

**Cross-validation strategies.** Different validation splits test different things. Random splits test method consistency. Stratified splits test performance across population subgroups. Patient-level splits test that the method does not exploit per-patient information that would not be available in deployment. Disease-level splits test cross-disease generalization. The system's validation includes all of these where applicable.

**Holdout sets that are actually held out.** The temptation to peek at holdout data during method development is real. INTERCEPTA's protocols structure holdout sets so they cannot be examined during development. Final evaluation on the holdout is the validation; if performance there does not match cross-validation expectations, the method is reconsidered, not the holdout reanalyzed.

**Ablation studies.** When the system is built with multiple components, ablation studies test which components actually contribute. Removing a component should degrade performance if the component matters. If removing it does not degrade performance, the component is not earning its place. The ablation discipline ensures that the architectural complexity in INTERCEPTA is justified by components that contribute, not by components that look impressive.

**Sensitivity analysis.** Method performance often depends on choices made during development: hyperparameters, preprocessing details, validation cohort selection. Sensitivity analysis varies these choices systematically and characterizes how performance depends on them. Methods that are highly sensitive to specific choices are flagged as potentially unstable; methods robust to reasonable variation are more trustworthy.

These internal validation practices are routine in good computational science. They are also routinely violated under deadline pressure. INTERCEPTA's commitment is to do them rigorously even when deadlines suggest shortcuts.

## External Replication Requirements

Internal validation by INTERCEPTA's team is necessary but not sufficient. External replication by groups not affiliated with INTERCEPTA provides independent verification.

The commitment is operational. Major claims about system capability — claims about disease coverage, performance, novel mechanism discoveries — require external replication before being treated as established. The replication uses publicly available code (where compatible with privacy and competitive constraints), publicly described methods, and ideally publicly available data.

External replication has costs. It requires releasing methods in detail. It exposes potential weaknesses to competitors. It produces public evidence when claims do not replicate, which is uncomfortable. These costs are the price of the commitment.

The benefits are foundational. External replication is what distinguishes claims supported by evidence from claims supported only by self-assessment. The pharmaceutical industry knows this from drug development: internal data is necessary but external trials in other institutions are required for approval. Computational medicine has not yet adopted the same standard universally; INTERCEPTA's commitment helps establish it.

When replication does not succeed — when external groups cannot reproduce INTERCEPTA's reported performance — the response is investigation rather than dismissal. Replication failures may indicate problems in the method, problems in documentation, or problems in the replicating group's setup. Investigation distinguishes these. When the problem is in the method, the method is corrected. When the problem is in documentation, documentation is improved. When the problem is in the replication setup, the issue is communicated and the replication is supported through to success.

## Prospective vs Retrospective Validation

Retrospective validation evaluates a method on outcomes that have already occurred. Prospective validation evaluates a method on predictions made before outcomes occur. The distinction matters because retrospective evaluation can be inadvertently biased in ways prospective evaluation cannot.

Most computational medicine methods are validated only retrospectively. The reasons are practical: retrospective data is available; prospective evaluation requires running the system in deployment-like contexts and waiting for outcomes; ethics review for prospective evaluation is more complex.

INTERCEPTA's commitment is that prospective validation is required for clinical deployment claims. Predictions are made, recorded, and locked. Outcomes are observed in the future. Performance is evaluated on the prospective predictions against the observed outcomes. This is harder than retrospective validation but produces evidence that retrospective validation cannot.

The commitment shapes deployment phasing. Initial deployment occurs in research-context settings where prospective validation can occur without affecting clinical decisions. As prospective validation accumulates, the validated scope expands. Clinical deployment follows prospective validation, not the other way around.

Prospective validation also handles distribution shift better than retrospective validation. The method is being applied to current patients, in current contexts, with current data quality. The prospective performance reflects what the method actually does in deployment, including the effects of distribution shift between training and deployment.

## Cross-Population Validation

Performance varies across populations. A method validated on one population may perform differently on another. Cross-population validation characterizes the variation rather than assuming homogeneity.

INTERCEPTA's commitment is that performance is measured across population dimensions: ancestry, sex, age, geography, socioeconomic indicators where available, disease subtype prevalence, sample processing variation. The measurements are continuous and published.

Where cross-population performance is uniform, the method is robust. Where performance varies systematically, the variation is characterized: which populations have higher performance, which have lower, what the gap looks like. The characterization informs deployment decisions: deployment is constrained where cross-population validation reveals unacceptable gaps.

This connects to the equity commitments in Chapter 5.4 and the bias commitments in Chapter 9.1. Cross-population validation is what makes those commitments operational. Without it, equity is aspirational. With it, equity becomes measurable, addressable, and accountable.

The implementation requires investment in diverse validation cohorts. Populations underrepresented in default datasets must be actively pursued. Validation data must be acquired even when it does not advance immediate commercial goals. The investment is part of the equity commitment.

## Mechanism Validation Through Perturbation

Mechanism inference can be statistically supported but mechanistically wrong. The system might infer mechanism patterns that are correlational artifacts rather than causal relationships. Mechanism validation through perturbation experiments distinguishes causal from correlational.

Where perturbation experiments are available — gene knockouts, drug treatments with known mechanisms, CRISPR screens — INTERCEPTA's mechanism inference can be tested. If the system predicts mechanism A based on cellular state, and direct perturbation of mechanism A produces the predicted cellular state changes, the inference is mechanistically validated. If perturbation does not produce the predicted changes, the inference is mechanistically wrong despite statistical support.

The commitment is that mechanism claims with clinical implications require perturbation validation where feasible. For drug mechanism claims, drug-target perturbation experiments validate the claimed mechanism. For pathway dysregulation claims, pathway-specific perturbation experiments validate the claimed dysregulation.

The cost is significant. Perturbation experiments are expensive, time-consuming, and often outside the resources of any single lab. INTERCEPTA's commitment is partnership: collaboration with academic and industrial labs that can perform validation experiments INTERCEPTA's predictions identify as priorities. The collaborations are structured so that validation results — whether confirming or refuting predictions — are published.

The benefit is that mechanism claims become trustworthy. A claim validated through perturbation is one we know is causally correct, not just statistically supported. The trust earned through perturbation validation grounds the broader confidence in the system's mechanism reasoning.

## Regulatory Validation Pathway

INTERCEPTA's clinical deployment requires regulatory clearance. The validation pathway is structured to meet regulatory requirements while serving the broader scientific honesty commitment.

The FDA framework for software as medical device, AI/ML clinical decision support, and predetermined change control plans defines what regulatory validation looks like. The framework includes initial clearance with comprehensive validation evidence, monitoring of deployment performance, predetermined plans for system updates, and ongoing reporting requirements. Equivalent frameworks exist in other jurisdictions.

INTERCEPTA's pathway is specific:

**Initial clearance package.** Comprehensive validation evidence supporting the specific use case being submitted. Performance data across populations. Bias characterization. Failure mode documentation. Mechanism reasoning audit support. The package is structured to meet FDA evidence requirements while reflecting INTERCEPTA's broader commitments.

**Post-market surveillance.** Once cleared, deployment performance is continuously monitored. Predictions are tracked. Outcomes are observed. Performance gaps are characterized. Drift is detected. Reports are filed with FDA on the cadence the framework requires.

**Predetermined change control.** When the system updates — new training data, new methods, new disease coverage — the changes are documented in advance. FDA reviews the change control plan; subsequent specific changes within the plan can be deployed without fresh approvals. Significant changes outside the plan require new submissions.

**Adverse event reporting.** When the system contributes to adverse outcomes — predictions that turned out to be wrong, recommendations that did not produce expected benefit — the events are reported through FDA's adverse event channels. Investigation determines what happened and what corrective actions are appropriate.

The regulatory engagement is collaborative rather than adversarial. INTERCEPTA's commitments align with FDA's requirements; the alignment makes the relationship productive.

International regulatory engagement extends the same principles to other jurisdictions. EMA in Europe, MHRA in the UK, PMDA in Japan, NMPA in China, equivalent agencies elsewhere have parallel frameworks. INTERCEPTA's deployment in each jurisdiction follows the relevant framework.

## Continuous Validation in Deployment

Validation does not end at clearance. Deployment performance is continuously monitored, and the monitoring is structured to catch problems before they accumulate.

**Calibration monitoring.** As discussed in earlier chapters, calibration audit verifies that confidence estimates match empirical accuracy in deployment. Drift triggers recalibration.

**Performance monitoring across populations.** Deployment data is segmented by population dimensions. Performance gaps that were not apparent in pre-clearance validation may emerge in deployment. The monitoring catches them.

**Failure mode tracking.** When the system produces predictions that turn out to be wrong, the failures are characterized. Patterns in failures suggest systematic issues that may require methodology updates.

**User feedback integration.** Clinical users who interact with the system are sources of feedback about its actual behavior. When users report unexpected outputs, suspicious recommendations, or behaviors that do not match documentation, the reports are investigated.

**Periodic comprehensive review.** On a regular cadence, comprehensive review of deployment performance is conducted. The review aggregates calibration audit, population performance, failure mode tracking, and user feedback into an overall assessment. The assessment informs system updates and continued deployment decisions.

The continuous validation is operational infrastructure. It has ongoing cost. The cost is the price of the commitment to ensuring the system continues to work in deployment, not just at clearance time.

This chapter has specified the validation philosophy that grounds INTERCEPTA's claims. The next part of the book — Chapters 12 through 17 — addresses operational reality, technical implementation, team, sustainability, and risks. Together, the architecture of Part Two, the capabilities of Part Three, the commitments of Part Four, and the operations of Part Five constitute the full specification of what INTERCEPTA is and how it works.

---

## Figures Planned for This Chapter

**F11.1: Validation Pyramid** — Layered structure from narrow internal benchmarks at the base, through internal cross-validation, external replication, prospective validation, and ultimately clinical deployment validation at the apex. Each layer builds on the one below; claims supported by higher layers are stronger than claims supported only by lower layers.

**F11.2: Falsification Cycle** — Diagram showing the operational falsification practice. Every claim → predicted observations → falsification experiment → observation → claim refined or abandoned. The cycle as discipline that protects against overclaim.

**F11.3: Regulatory Pathway Map** — Specific pathway from concept to clinical deployment within FDA's framework. Shows specific documents required, decision points, validation requirements at each step, and the predetermined change control process for ongoing updates.
