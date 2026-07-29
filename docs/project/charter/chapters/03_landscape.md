# The Landscape — Where INTERCEPTA Sits

*PART ONE: IDENTITY*

---

## The Drug Discovery AI Landscape

INTERCEPTA does not enter an empty field. The application of artificial intelligence and machine learning to drug discovery has been an active area for over a decade, with significant capital invested, capable teams assembled, and meaningful technical progress achieved. Any honest articulation of why INTERCEPTA exists must include an honest accounting of where it sits relative to the actors already in this space, what they do well, what they miss, and where INTERCEPTA's distinct contribution lies.

This chapter is not a competitive analysis in the venture-pitch sense. It is an honest reckoning. We name competitors specifically. We acknowledge what they do well. We articulate what we believe they miss. We acknowledge that some of the things we believe they miss may, in retrospect, turn out to be things we missed. The goal is to locate INTERCEPTA in a real landscape, not to dismiss everyone else.

The landscape has roughly five categories of actors. Pure-tech companies that have built AI/ML platforms primarily focused on drug discovery, deployed across multiple disease areas. Pharmaceutical companies that have built internal AI/ML capabilities to support their existing pipelines. Academic research groups that have produced foundational methods which become the building blocks the rest of the field uses. Clinical decision support companies that have built tools deployed in healthcare delivery. And foundation infrastructure providers — AI labs producing the foundation models, cloud providers offering the compute, sequencing companies producing the data — without whom none of the application-layer companies could function.

INTERCEPTA is not categorically the same as any of these. The closest categorical match is the pure-tech company, but INTERCEPTA's commitments and architecture place it in a different position even within that category. The chapters that follow develop why. This chapter establishes the landscape against which the difference is visible.

## Pure-Tech Competitors

The pure-tech category includes Recursion Pharmaceuticals, Insitro, Atomwise, BenevolentAI, Exscientia, Schrödinger, and a long tail of smaller companies. Each has built a platform that uses AI/ML to advance some aspect of drug discovery, has assembled significant scientific and engineering teams, has raised substantial capital, and has produced real technical work.

Recursion Pharmaceuticals has built a phenotypic screening platform that uses cellular imaging plus machine learning to identify drug candidates from cellular morphological signatures. The company has produced an enormous proprietary dataset of cellular images under chemical perturbation, applied deep learning to identify patterns linking morphology to disease and drug response, and built a pipeline of drug candidates from this approach. The company is publicly traded, has multiple programs in clinical development, and has demonstrated that the imaging-based approach can produce viable candidates.

Insitro applies machine learning across multiple modalities — including transcriptomics, imaging, and other cellular measurements — to build predictive models of disease biology and drug response. The company emphasizes generating proprietary data through automated experimental platforms and using the data to train models that inform target identification and drug design. Insitro has partnerships with major pharmaceutical companies and a pipeline of internally-developed candidates.

Atomwise built one of the earliest deep-learning platforms for structure-based drug design, applying convolutional neural networks to predict binding affinity between candidate molecules and protein targets. The company has scaled this approach to screen vast chemical libraries and has produced candidates across multiple disease areas. Atomwise's approach is upstream of cellular biology — operating at the molecule-target interaction level — and is complementary rather than competitive with cellular-data approaches.

BenevolentAI built a knowledge graph approach combining literature mining, multi-omics data, and reasoning over biological relationships to identify novel drug targets and repositioning opportunities. The company has produced candidates including treatments advanced into clinical development.

Exscientia built generative chemistry capabilities — using machine learning to design novel molecules optimized for desired properties. The company has produced multiple drug candidates that progressed to clinical trials, including the first AI-designed candidates to enter human studies.

Schrödinger has been the leader in physics-based computational drug discovery for decades, with its primary expertise in molecular dynamics, free energy calculation, and structure-based design. The company has integrated machine learning into its platform while maintaining its physics-based foundation.

Each of these companies does substantial work that INTERCEPTA does not. Recursion's morphological imaging captures phenotypic information that complements transcriptomic approaches. Insitro's multi-modal data generation produces datasets that the broader field benefits from. Atomwise's structure-based screening is upstream of where INTERCEPTA operates. BenevolentAI's knowledge graph integration captures relationships that pure data-driven approaches miss. Exscientia's generative chemistry is a capability INTERCEPTA does not have. Schrödinger's physics-based foundation provides rigor that machine-learning-only approaches lack.

What these companies share, with substantial variation in degree, is a focus on drug discovery as a pipeline. The output is drug candidates, advanced through stages from target identification to lead optimization to clinical development. The customer is, ultimately, the pharmaceutical industry — either as partner or as competitor for clinical assets. The success metric is candidates that succeed clinically.

INTERCEPTA differs in several specific ways. INTERCEPTA's primary unit of analysis is the patient's cellular state, not the molecule. INTERCEPTA's deliverables include not only drug candidates but patient stratification predictions, mechanism discoveries, validation data for regulators, and decision support for clinicians. INTERCEPTA's architecture is multi-stakeholder from the start, not pharma-partnership-first. INTERCEPTA's commitment to scientific honesty as institutional practice is a different kind of commitment than competitive optimization for clinical asset value. INTERCEPTA's universality commitment — handling any disease through architectural principles rather than per-disease engineering — is a different scope than the disease-by-disease pipeline development most pure-tech companies pursue.

These are differences of orientation more than differences of technology. The technologies overlap. The orientations are distinct.

## Pharmaceutical In-House Programs

Major pharmaceutical companies have built substantial internal AI/ML drug discovery programs. AstraZeneca, Pfizer, Roche, Novartis, Merck, GSK, Sanofi, Bayer, Eli Lilly, AbbVie, and most others have either acquired AI/ML capabilities, built internal teams, or partnered with pure-tech players.

These programs have advantages that pure-tech companies and INTERCEPTA do not. They have proprietary data: clinical trial results, molecular characterization of legacy compounds, biomarker measurements from prior development programs, real-world evidence from deployed therapies. They have validation capacity at scale: ability to advance candidates through preclinical and clinical development, to test predictions empirically, to learn from clinical outcomes that academic and pure-tech actors cannot easily access. They have regulatory experience: long-standing relationships with FDA, EMA, and other regulators, accumulated knowledge of submission requirements, validated quality systems.

At the same time, pharmaceutical in-house programs have constraints. Their incentives are pipeline-specific: AI/ML capabilities are deployed primarily to advance the company's existing programs and competitive position. Cross-disease generalization, while valuable, is not the primary metric. Public publication of methods and results is constrained by intellectual property considerations. Failure publication is rare; the same negative results that INTERCEPTA commits to publishing are typically held internally because publishing them would advantage competitors. Cross-disease integration of insights is limited by organizational structure: different therapeutic areas often operate as relatively independent business units with their own data, methods, and decisions.

INTERCEPTA can do things pharmaceutical in-house programs structurally cannot. INTERCEPTA can publish negative results because INTERCEPTA's value depends on the field's trust rather than on competitive secrecy. INTERCEPTA can integrate insights across diseases because INTERCEPTA's architecture is universal across diseases. INTERCEPTA can serve multiple pharmaceutical companies as partners without conflicts of interest because INTERCEPTA does not compete with any of them on assets. INTERCEPTA can advance the field's overall capability because INTERCEPTA's mission is the field's capability, not any single company's pipeline.

This is not a criticism of pharmaceutical in-house programs. Their incentives are appropriate to their position and produce real value. INTERCEPTA's incentives are appropriate to a different position, and the difference matters.

## Academic Research Groups

Many of the methodological foundations that INTERCEPTA builds on came from academic research groups. The single-cell sequencing protocols, the foundation model architectures, the drug response transfer learning frameworks, the validation methodologies — most of these were originated by academic groups, often years before they were adopted commercially.

scDrugMap came from the Song lab at the University of Florida and the Wang lab at UConn. scDEAL came from a collaboration between the Han lab at the University of Utah and others. SCAD came from work at the Jiao Tong University and collaborators. scAdaDrug came from research groups working on multi-source domain adaptation. scATD emerged from a 2025 collaboration. scFoundation came from a multi-institutional collaboration including Tsinghua and BioMap. Geneformer came from the Theodoris lab at Boston Children's Hospital. UCE came from the Snap Stanford group. scGPT came from the Bo Wang lab at the University of Toronto.

These groups produce methodological innovation. They publish methods publicly, document them carefully, and contribute to the field's ability to do better work. They are essential. INTERCEPTA exists because they exist; without their foundational work, INTERCEPTA's architecture would have to invent rather than integrate.

Academic groups also have characteristic constraints. They are typically organized around specific methodological contributions rather than around integrated systems. Their incentive structure rewards publications and scientific impact more than deployment. The infrastructure required to build a deployable system — software engineering at production quality, regulatory pathway navigation, ongoing operational maintenance — is typically beyond what academic groups can sustain. The translation gap between academic method and deployed system is real and not the academic groups' responsibility to close.

INTERCEPTA's relationship with academic research is not competitive. We build on academic methods. We acknowledge them explicitly. We aim to publish our own methodological contributions in ways that academic groups can build on. We aim to deploy at clinical scale in ways that academic groups typically cannot. The two roles — methodological innovation and deployed system — are complementary.

## Clinical Decision Support Tools

A different category of competitor operates in clinical decision support: companies that have built tools deployed in clinical settings to inform diagnosis, treatment selection, or care management. Tempus, Foundation Medicine, Caris Life Sciences, and others operate in this space, primarily focused on oncology.

Tempus has built a platform integrating molecular characterization (genomic, transcriptomic, proteomic) with clinical data, deployed at scale across cancer centers. The company provides results that inform treatment selection for individual patients. Tempus has accumulated substantial real-world evidence that informs both individual patient decisions and broader research questions.

Foundation Medicine, now part of Roche, provides comprehensive genomic profiling for cancer patients, with results integrated into clinical workflows for treatment selection. Foundation has FDA-approved tests, established reimbursement pathways, and broad clinical adoption.

Caris Life Sciences provides multi-omic profiling with similar clinical positioning, including transcriptomics that overlaps with the data INTERCEPTA uses.

These companies have advantages INTERCEPTA does not. They have clinical adoption, regulatory clearance, reimbursement infrastructure. They have integration into electronic health record systems. They have established relationships with the clinical decision-makers whose decisions their tools inform.

They also have characteristic limitations. Most operate at bulk rather than single-cell resolution. Most focus on oncology rather than spanning the full disease continuum. Most provide annotation and information rather than mechanism inference and intervention recommendation. Their decision support is more 'here is what we measured' than 'here is what intervention would help and why.'

INTERCEPTA's positioning is different. INTERCEPTA operates at single-cell resolution. INTERCEPTA spans diseases beyond oncology. INTERCEPTA recommends interventions, not just reports measurements. The distinction matters: clinical decision support that says 'this patient has these mutations, here are some FDA-approved drugs targeting them' is genuinely useful but different from clinical decision support that says 'based on this patient's cellular state, this intervention is predicted to reshape it toward the desired phenotypic target with this confidence and this mechanism.'

## What Everyone Does Well

It is necessary to be honest: the actors described above do real work. Not all of it. Not all of the time. But enough that INTERCEPTA's existence is not justified by the field being broken. The field has produced value.

Foundation models for cellular data exist because dedicated teams invested years of compute and labeled data into producing them. The transfer learning methods that bridge bulk to single-cell exist because methodological researchers worked through the architectural choices required. The drug discovery pipelines at major pharma have produced approved therapies. The clinical decision support tools at Tempus and Foundation have informed treatment decisions for hundreds of thousands of patients. Real value has been delivered, real patients have benefited, real science has been advanced.

INTERCEPTA's contribution is not to replace this work. It is to integrate, extend, and complete what the field has built. We use foundation models built by others. We adapt transfer learning methods developed by others. We build on the conceptual frameworks pharmaceutical research has produced. We complement the clinical decision support that exists. The chapters that follow specify what we add, but the addition exists in dialogue with what already exists, not in opposition to it.

## What Everyone Misses

Equally, it is necessary to be honest about what the field misses. INTERCEPTA exists because there are gaps the field has not yet filled. Naming the gaps clearly is essential to articulating INTERCEPTA's contribution.

The integration gap. The pieces exist. Foundation models, transfer learning, mechanism inference, uncertainty quantification, intervention prediction, validation methodology. They exist as separate pieces. The integrated system that brings them together into a single coherent architecture serving the entire disease continuum has not been built. Each actor in the field has built some of the pieces. None has built the integration.

The universality gap. Most actors operate disease-by-disease. The architectural pattern is: pick a disease, build a system tuned to it, validate it on that disease's data. This is rational for individual companies. It is also a structural limit on what the field as a whole can deliver. A system built tuned to lung cancer does not handle rheumatoid arthritis. A system built for autoimmune disease does not handle neurodegeneration. Each disease requires its own engineering effort. The cumulative effort across diseases is enormous; the resulting capability is fragmented.

INTERCEPTA's bet is that the universality is achievable through architecture rather than through per-disease engineering. The immune system manages it. We believe a computational system can too. But this requires architectural commitments — particularly to dynamic mechanism representation rather than hardcoded mechanism axes — that few existing actors have made.

The multi-stakeholder gap. Most actors design for one customer. Pure-tech companies design for pharma partnerships and clinical asset value. Pharma in-house programs design for their internal pipelines. Clinical decision support tools design for clinicians at point of care. Each design optimizes for its primary customer. None integrates the multi-stakeholder design that the disease continuum actually requires.

INTERCEPTA's design is multi-stakeholder from day one. Pharma receives drug candidates plus stratification. Clinicians receive decision support. Patients receive personalized recommendations through their clinicians. Researchers receive mechanism discoveries. Regulators receive validation data. Public health receives surveillance signals. Each stakeholder's use generates value for others; the system's value compounds across stakeholders rather than being concentrated for one.

The honesty gap. This is the hardest to articulate without sounding self-righteous, but it is the one we believe matters most. The field has accumulated trust debt because actors have systematically chosen to optimize for benchmarks, demonstrations, investor narratives, and competitive positioning at the expense of honest characterization of what their systems can and cannot do. This is not a moral failing of the actors involved — the incentive structures push toward this — but it is a structural feature of the field's current state.

INTERCEPTA's commitment to scientific honesty as institutional practice is the response to this gap. We do not claim universality before we earn it. We publish failures alongside successes. We characterize biases explicitly. We refuse to deploy where confidence is insufficient. These commitments compromise short-term metrics. We believe they are required for long-term success.

## Where INTERCEPTA Wins

Putting the pieces together: INTERCEPTA's distinct contribution is the integrated, dynamically universal, multi-stakeholder, institutionally honest computational immune response system for disease that no existing actor is building.

Three vectors of distinction:

First, integration. INTERCEPTA brings cellular characterization, mechanism inference, intervention prediction, uncertainty quantification, validation, and continuous learning into a single coherent architecture. The architecture is the immune system's, translated to computation. The integration is the deliverable that no fragment-builder can match.

Second, dynamic universality. INTERCEPTA earns universality through architectural commitment — every component dynamic, learned from data, adaptable across diseases — rather than through per-disease engineering. This means INTERCEPTA's value scales with the number of diseases characterized, while disease-specific systems' values are bounded by their target diseases.

Third, scientific honesty as institutional practice. INTERCEPTA's commercial moat is not technological — most of the technologies are public or licensable. The moat is institutional: the architectural and operational commitments that earn regulatory trust and clinical adoption over time. These commitments are hard to copy because they require choices most companies are not willing to make.

These three together produce the position INTERCEPTA occupies. Each vector alone is not sufficient. All three together are.

## Where INTERCEPTA Might Lose

It is necessary to articulate honestly where INTERCEPTA might fail. The same scientific honesty we commit to about our products applies to ourselves. Three failure modes are most plausible.

First, a major pharmaceutical company could decide to build the integrated system internally with substantially more resources than INTERCEPTA can muster. Pharmaceutical companies have data, clinical validation capacity, and regulatory experience that we do not. If one of them committed to the architectural pattern INTERCEPTA pursues, with comparable scientific honesty commitments, they could outpace us. Mitigation: scientific honesty commitments are structurally hard for companies whose primary incentive is clinical asset value, which constrains the commitment most pharma companies can credibly make. INTERCEPTA's positioning as a mission-aligned independent actor serving multiple pharma partners is a position pharma companies cannot occupy.

Second, the foundation model layer that INTERCEPTA builds on could plateau. Current foundation models for cellular data are trained on similar data with similar architectures. They may have hit a ceiling on what they can extract. If they have, INTERCEPTA's performance is bounded by their performance, and we depend on advances we do not control. Mitigation: INTERCEPTA's architecture is not foundation-model-locked; we can substitute different foundation approaches, and our mechanism layer adds capability that pure foundation models lack. But the dependency is real.

Third, the bet on scientific honesty as commercial moat could be wrong. The field has accumulated trust debt, but the market may not, in fact, reward the rebuilding of trust at the scale required. If sales cycles for trustworthy tools are slower than for impressive demonstrations, INTERCEPTA's economics may not work. Mitigation: we structure the business to require less capital and longer time horizons than competitors, so that economic patience is feasible. But the bet is real.

Other failure modes — regulatory failure, technical failure, ethical failure, team failure, financial failure — are addressed in Chapter 16. The three above are the strategic risks specific to INTERCEPTA's positioning relative to the landscape.

Naming risks does not eliminate them. It does mean we are operating with eyes open. The chapters that follow describe the architecture, capabilities, and commitments that we believe make these risks manageable. The fact that they are real is the price of building something genuinely new.

---

## Figures Planned for This Chapter

**F3.1: Competitive Landscape Map** — Two-dimensional positioning map. X-axis: breadth of capability, from single-purpose tools to integrated systems. Y-axis: scientific honesty practice, from overclaim to honest characterization. Major actors plotted by position. INTERCEPTA positioned at top-right (most integrated, most honest), with the position currently unoccupied.

**F3.2: Capability Comparison Matrix** — Detailed table. Rows: 12-15 capability dimensions including foundation model integration, drug response prediction, mechanism inference, multi-stakeholder design, dynamic universality, etc. Columns: ~10 major actors including INTERCEPTA. Cells indicate capability presence and depth. Visual reveals where INTERCEPTA's distinct combination lives.

**F3.3: Differentiation Map** — Concentric rings showing what is commodity (single-cell sequencing, FM embeddings), what is competitive (drug response prediction, transfer learning), and what is INTERCEPTA's moat (immune-system architecture, dynamic universality, scientific honesty as institutional practice). The rings make explicit what INTERCEPTA depends on versus what INTERCEPTA contributes.
