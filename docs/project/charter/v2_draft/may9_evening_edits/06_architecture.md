# Chapter 6: The Architecture — Immune System as Blueprint

*PART TWO: FOUNDATIONS*

---

This is the longest chapter in the book and the most important. It develops in detail the architectural translation of biological immune system principles into INTERCEPTA's computational architecture. Chapter 1 introduced the framing. This chapter does the work of justifying every architectural choice through its biological analog, specifying what each component does, and showing how the components integrate.

The chapter is technical in places. We have tried to make it accessible to readers without deep machine learning background, but some sections require comfort with the basic vocabulary of cellular biology and computational systems. Readers who want only the high-level conceptual map can read sections 6.1, 6.2, and 6.9, skipping the detailed component descriptions in between. Readers who want the full architecture should read all sections in order.

## 6.1 How the Biological Immune System Works

Before translating to computation, we need a clear picture of what we are translating. The biological immune system is a vast, distributed, multi-component defense system. It has evolved over hundreds of millions of years to solve the problem of universal pathogen response. The components and their interactions are summarized below at a level of detail sufficient to ground the architectural translation.

**Innate immunity** is the fast, generic first line of defense. Its components include macrophages, neutrophils, dendritic cells, natural killer cells, and the complement system. Innate cells recognize threats through pattern recognition receptors that respond to general molecular signatures associated with pathogens or cellular damage. They do not require prior exposure to the specific threat. They respond within minutes to hours of encounter. They are also relatively non-specific: they kill pathogens broadly, present antigens to other immune cells, and produce inflammatory signals that recruit more immune cells to the site.

**Adaptive immunity** is the slow, specific second line of defense. Its components include T lymphocytes (T cells) and B lymphocytes (B cells). Adaptive cells carry receptors generated through random recombination of gene segments, producing an enormous repertoire of receptor specificities. When a T cell or B cell encounters its specific antigen, presented appropriately by an antigen-presenting cell (typically a dendritic cell from the innate response), the cell undergoes massive clonal expansion and differentiation. The expanded clones produce the targeted response: T cells kill infected cells or coordinate the response, B cells produce antibodies. The adaptive response takes days to weeks to develop initially, but it is precise. It learns the specific threat through encounter.

**Memory** is what persists after the threat is cleared. Most expanded clones die off after the response. Some persist as memory cells, retaining the specific receptor that recognized the threat. Memory cells reside in lymphoid tissues and circulate through the body. When the same threat returns, memory cells recognize it quickly, expand more rapidly than naive cells did initially, and clear the threat before clinical disease develops. This is what immunological memory is. This is what vaccines exploit.

**Coordination** happens through cell-cell communication. Cytokines are signaling molecules that immune cells use to inform each other about what they are doing. Different cytokine profiles direct different kinds of immune response: type 1 responses against intracellular pathogens, type 2 responses against extracellular parasites, type 17 responses against fungi and certain bacteria. The coordination is decentralized — no single cell type is in charge — and adaptive — the response shape is determined by the threat detected.

**Self-tolerance** prevents the immune system from attacking the body it protects. T cells that would react to the body's own proteins are eliminated during development in the thymus through negative selection. B cells producing self-reactive antibodies are deleted, anergized, or undergo receptor editing to remove self-reactivity. Regulatory T cells actively suppress immune responses that would damage self. Self-tolerance is not perfect — autoimmune diseases occur when it fails — but it is the architectural feature that makes the rest of the immune system safe to deploy.

**Surveillance** is continuous monitoring of body tissues for signs of dysregulation. Natural killer cells patrol for cells with abnormal surface markers, including cancer cells. T cells circulate through lymphoid tissues sampling antigens. The surveillance system catches threats before they manifest as clinical disease.

**Failure modes** of the immune system are characteristic and instructive. Autoimmune disease results when self-tolerance fails and the system attacks the body it should protect. Immunodeficiency results when the system fails to mount adequate response. Allergy and hypersensitivity result when the system over-responds to non-threats or to harmless substances. These failure modes are not random; they are characteristic outcomes of the architectural pattern. Any system that does what the immune system does — pattern recognition without prior training, adaptive learning, memory, coordination, self-tolerance — will face these characteristic failure modes in its own form.

This is the system we are translating.

## 6.2 Translation to Computational Architecture

The translation is component-by-component. Each immune system function maps to a specific INTERCEPTA architectural element. The mapping is not metaphorical; it is functional. The biological component does X; the computational component does the analog of X for cellular state characterization and intervention recommendation.

Innate immunity (fast, generic threat response) maps to **foundation models for cellular data**. Foundation models embed any cell from any tissue or disease into a shared representational space. They do this without prior training on the specific patient's specific disease. They are generic and fast.

Adaptive immunity (slow, specific learning) maps to **per-disease and per-patient mechanism inference**. Disease-specific models are trained or fine-tuned for the cellular biology of specific diseases. Patient-specific characterization adapts general models to individual cellular states. The adaptive layer is slower than the innate layer but precise. It learns through encounter.

Memory cells map to **the patient encounter database and structured pattern repository**. Patterns observed across past patients — which cellular states responded to which interventions, which mechanisms predicted which outcomes — are encoded in structured knowledge that improves predictions for future patients. The system gets smarter as more patients are characterized.

Antigen presentation maps to **mechanistic representation of disease state**. Just as dendritic cells present antigens to lymphocytes for response coordination, INTERCEPTA's mechanism layer presents structured representations of dysregulated pathways and processes to the prediction and intervention selection components. The presentation is what allows different system components to act on a shared understanding of what the disease is.

Coordination through cytokines maps to **structured interfaces between system components**. Mechanism inference, prediction, uncertainty quantification, and intervention selection share information through defined interfaces. The system as a whole produces integrated outputs because the components coordinate.

Self-tolerance maps to **mechanistic uncertainty and refusal to predict beyond competence**. The system's mechanistic uncertainty layer detects when a patient's cellular state is too far from training distribution, when the relevant mechanism is poorly understood, or when the model itself has internal disagreement. In these cases, the system refuses to produce a confident prediction. This is the architectural analog of self-tolerance: refusing to act when action would be inappropriate.

Surveillance maps to **continuous monitoring of cellular states across populations**. The system tracks patterns in cellular state across many patients over time. Emerging patterns suggest novel disease subtypes, novel mechanisms, or population-level shifts. The surveillance produces early detection signals and mechanism discoveries that single-patient analysis would miss.

Failure modes — autoimmune (false positives), immunodeficiency (false negatives), allergy (miscalibration) — map to **explicit monitoring of analogous failure modes in the computational system**. False positives are claims of response where none exists. False negatives are missed real signals. Miscalibration is overconfidence. Each is monitored explicitly because we know from the biological analogy that any system with this architecture will face these failure modes in its own form.

The next sections develop each layer in detail.

## 6.3 Innate Response Layer — Foundation Models

The foundation model layer provides INTERCEPTA's fast generic response to any cellular state. Its function is to read the cellular data of any patient with any disease and produce a useful representation: a vector encoding of each cell that captures something meaningful about its biological state.

INTERCEPTA uses multiple foundation models rather than committing to a single one. Different foundation models have different strengths. scFoundation, with its larger parameter count and gene-expression-based representation, tends to capture detailed transcriptional state. Geneformer, with its rank-based gene encoding, is robust to certain kinds of normalization variation. UCE, trained across species, captures evolutionarily conserved cellular states. Specialized models like CancerFoundation provide depth on specific tissues at the cost of generality.

The architectural commitment is to ensemble across foundation models when appropriate. Different models may agree, in which case the prediction is more robust. They may disagree, in which case the disagreement itself is information about the cell — perhaps it is unusual in some way, perhaps the cell type is poorly represented in some training distributions. The disagreement is not noise to be averaged away; it is signal about confidence.

Foundation model outputs are intermediate representations, not final predictions. They feed into downstream components: mechanism inference, drug response prediction, uncertainty quantification. The foundation models do the heavy lifting of encoding cellular biology into mathematical objects; the downstream components do the work of producing clinically meaningful outputs from those representations.

Limitations of foundation models are characterized explicitly. Their training data has known biases — over-representation of human and mouse cells, immune cells, cancer cells in some models. Their performance on rare cell types is weaker than on common ones. Their representations capture co-expression patterns rather than causal relationships. They fail in characteristic ways when given inputs far from training distribution. The downstream components are designed to compensate for these limitations: mechanism inference adds biological structure that pure FM representations lack, uncertainty quantification detects when FM outputs are unreliable, and the architecture as a whole does not depend on FM perfection.

A practical detail worth noting: the field's empirical evidence on foundation model utility for clinical applications is mixed. The scDrugMap evaluation showed scFoundation performing impressively at cell-level drug response prediction (F1 of 0.971 pooled). The Elmarakeby Dana Farber evaluation showed limited FM advantage for patient-level cancer outcome prediction. These are not contradictory findings; they are findings about different tasks. Cell-level prediction and patient-level prediction are different problems with different optimal architectures. INTERCEPTA's architecture bifurcates Layer 2 to handle both honestly: cell-level processing using FM-based methods, patient-level processing using approaches better suited to that task.

## 6.4 Adaptive Response Layer — Per-Disease Learning

Adaptive response provides INTERCEPTA's specific learned response to particular diseases and particular patients. While the innate response treats every cell with generic processing, the adaptive response specializes.

The adaptive layer's core technology is what we call MC-FMA: Mechanism-Constrained Foundation Model Adaptation. The MC-FMA approach takes foundation model embeddings and adapts them through fine-tuning that incorporates mechanistic constraints. The constraints come from biological knowledge — pathway activity inference, cellular program decomposition, KAALCURA-style mechanistic axes — and they shape the adaptation so that the resulting representations are both data-driven and biologically meaningful.

MC-FMA differs from standard fine-tuning in important ways. Standard fine-tuning optimizes a representation for a specific downstream task without regard to biological structure. MC-FMA optimizes for the downstream task while regularizing the representation toward biological meaningfulness. The result is a representation that performs well on the task and is also interpretable in biological terms — a property essential for clinical deployment where mechanism explanation matters.

Per-disease adaptation produces models specialized to the cellular biology of specific diseases. Lung adenocarcinoma adaptation produces a model that handles lung cellular states at single-cell resolution, with mechanism representations specific to lung tumor biology. Rheumatoid arthritis adaptation produces a model that handles synovial tissue, with mechanism representations specific to joint inflammation biology. The per-disease specialization is what allows INTERCEPTA to perform with depth on each disease characterized.

Per-patient adaptation, where data permit, refines representations for individual patients. A patient with longitudinal samples — for instance, baseline tumor sample and post-treatment sample — provides data that can refine prediction specifically for that patient's tumor evolution. The adaptation respects the individual's biology rather than averaging it into population-level patterns.

The adaptive response is slower than the innate response. Per-disease adaptation requires substantial data; per-patient adaptation requires longitudinal samples that may not always be available. The slowness is acceptable because the innate response provides immediately usable output while adaptive response is being computed, just as in biological immunity. The two layers operate on different timescales and serve different purposes.

KAALCURA deserves specific mention. KAALCURA is the mechanistic axes framework that originated in our cancer drug response work, where three axes — proliferation, EMT (epithelial-mesenchymal transition), and DNA damage response — captured key dimensions of cellular state relevant to drug response. The framework worked: GDSC validation showed mean AUROC of 0.6715 across 286 drugs, with PARP inhibitors showing perfectly aligned mechanistic predictions (negative DDR coefficients across all five PARP inhibitors tested). The lesson from that validation is not that those three axes are universal — they are not, they were chosen for cancer biology and would not generalize to autoimmune or neurodegeneration — but that mechanism-aware axis decomposition produces useful representations. INTERCEPTA's commitment is dynamic axis inference: axes are learned per disease from cellular biology, not hardcoded across all diseases.

## 6.5 Memory and Scaling Intelligence

Memory is what makes immunity get better with use. The same is true for INTERCEPTA's intelligence. The memory layer's function is to encode patterns observed across past patients in ways that improve predictions for future patients.

The memory is structured rather than just accumulated data. Raw data accumulation is necessary but not sufficient. Structured memory means: patterns of cellular state that predict response to specific interventions, mechanisms that explain treatment failure, novel subtypes identified through cross-patient clustering, drug-disease relationships that become apparent only when many patients are aggregated. These are structured insights, not just bigger datasets.

Encoding insights into memory is a continuous process. As INTERCEPTA encounters new patients and observes outcomes, the memory layer updates. Pattern recognition algorithms identify recurring relationships. Statistical methods quantify them. New mechanism hypotheses are generated and tested. The memory becomes denser and more useful over time.

Retrieval from memory uses similarity to current patient cellular state. When a new patient's cellular data arrives, the system identifies past patients with similar cellular states and uses their outcomes to inform predictions for the current patient. The similarity is computed in the foundation model representation space, ensuring that biologically similar states are recognized as similar even when their gene expression vectors differ in details.

Scaling intelligence is the emergent property of structured memory accumulating and being retrieved appropriately. Each new patient encountered makes predictions for similar future patients better. Each disease characterized expands the boundary of confident prediction. Each intervention outcome refines the calibration of related predictions. The system's capability grows with use.

This is a different scaling pattern from most ML systems, which scale primarily through training data size and compute investment. INTERCEPTA scales through clinical encounter and structured insight accumulation. The implications for business strategy are addressed in Chapter 15. The architectural implication is that memory is not an afterthought but a first-class component, designed and engineered with the same care as the prediction components themselves.

A concrete example illustrates the difference. A traditional ML drug response system, deployed clinically, produces predictions that are no better at the millionth patient than at the thousandth. The model is fixed; only the predictions update. INTERCEPTA, by contrast, produces predictions at the millionth patient that benefit from observed outcomes of the previous 999,999 patients. The improvement is structured: similar patients inform predictions for the current patient through retrieval; mechanism patterns become clearer through aggregation; calibration is continuously updated. The result is a system whose value compounds over time.

## 6.6 Coordination Across Components

The immune system works because cells coordinate. Macrophages present antigens to T cells. T cells direct B cells to make antibodies. Dendritic cells migrate from tissue to lymph node carrying antigen information. Cytokines signal across cell populations. The coordination is what produces integrated response from many independent components.

INTERCEPTA's components coordinate similarly. Mechanism inference produces a structured representation of disease state. The representation is consumed by intervention prediction, which uses it to identify candidate interventions likely to reshape that mechanism. Uncertainty quantification consumes both the mechanism representation and the prediction outputs to characterize confidence. Intervention selection consumes all of the above to produce a recommendation. Each component depends on the others; no component produces useful output in isolation.

The coordination is implemented through structured interfaces — defined data schemas that components use to communicate. The interfaces specify what mechanism inference must produce, what prediction must consume, what uncertainty must quantify. The interfaces are stable contracts that allow components to be developed and improved independently while ensuring the system as a whole works coherently.

Decoupled components, coordinated through defined interfaces, is the architectural pattern that makes the system both maintainable and improvable. A better foundation model can be substituted without rewriting downstream components. A better mechanism inference algorithm can replace the current one without breaking the system. The coordination layer is the architectural feature that enables this evolvability.

The coordination also enables multi-stakeholder serving. The same architectural components produce outputs appropriate to different stakeholders by varying which outputs are surfaced and how they are presented. Pharmaceutical partners receive drug candidate outputs with stratification predictions. Clinicians receive intervention recommendations with mechanism explanations. Researchers receive mechanism discoveries and pattern aggregations. Regulators receive validation data and uncertainty characterizations. Each stakeholder receives outputs in formats appropriate to their role, but all outputs are produced by the same architectural components operating on the same patient data. The coordination layer is what allows this multi-stakeholder serving without architectural redundancy.

## 6.7 Self-Tolerance and Uncertainty

The self-tolerance analog in INTERCEPTA is the most important architectural feature for safe deployment. The system must refuse to predict beyond its competence. Without this refusal, the system will produce confident wrong answers in cases where confidence is unjustified, and clinical decisions made on those answers will harm patients.

The uncertainty layer is built around what we call MFMD: Mechanistic Failure Mode Detection. MFMD has multiple components.

Out-of-distribution detection identifies when a patient's cellular state is unusual relative to training data. If the cellular state is far from anything the system has seen before, the system flags this and either refuses to predict or attaches very low confidence to the prediction. OOD detection uses methods including density estimation in foundation model representation space, distance metrics from training distribution centroids, and reconstruction-based scores from autoencoders trained on the training distribution.

Mechanism mismatch detection identifies when the mechanism representation does not fit the cellular data well. If the system cannot construct a coherent mechanistic story for what is happening in this patient's cells, that incoherence is itself a signal. The prediction may be unreliable not because of statistical uncertainty but because the underlying biology is not well-modeled. Mechanism mismatch detection uses goodness-of-fit metrics for the inferred mechanism representation, residual analysis comparing observed to mechanism-predicted gene expression, and consistency checks across different mechanism inference approaches.

Internal disagreement detection identifies when different system components produce inconsistent predictions. If foundation model ensembles disagree, if different mechanism inference approaches yield different conclusions, if drug response predictions vary across model architectures, the disagreement is information about confidence. Internal disagreement detection uses ensemble variance, cross-method correlation, and prediction interval analysis.

Calibration audit ensures that the uncertainty estimates the system produces are accurate. When the system says it is 70% confident, it should be right approximately 70% of the time. Continuous calibration audit catches drift and triggers recalibration when calibration degrades. The audit uses held-out validation data with known outcomes, examining whether the system's stated confidence matches its empirical accuracy.

Together, these components implement the architectural commitment to refuse confident prediction when confidence is unjustified. The clinical deployment can trust the system because the system distinguishes its confident predictions from its uncertain ones, and refuses entirely when neither is appropriate.

The architectural significance of self-tolerance cannot be overstated. A system without it is a system that will harm patients. A clinician relying on a confident prediction that turns out to be wrong is worse than a clinician with no system at all, because the clinician's own judgment is displaced by the system's misleading confidence. INTERCEPTA's commitment to refusing predictions when confidence is unjustified is what makes the system safe to deploy in clinical contexts where wrong answers cause real harm.

## 6.8 Surveillance and Prevention

Surveillance is the immune system's patrolling function. INTERCEPTA's analog is continuous monitoring of cellular states across populations to detect emerging patterns.

Cross-patient pattern detection identifies recurring relationships that single-patient analysis would miss. Novel disease subtypes emerge as cellular state clusters across many patients. Mechanism patterns become clear when many cases are aggregated. Drug response patterns at the population level inform predictions for individuals.

Drift monitoring detects when cellular state distributions shift over time. A new disease subtype appearing, an existing disease evolving, environmental exposure manifesting in cellular signatures — these are detectable in INTERCEPTA's data before they are clinically obvious. The detection produces early warning signals that public health systems and researchers can investigate.

Population-level prediction extends individual-level prediction. While individual predictions guide individual care, population-level predictions inform broader decisions: which interventions to develop, which subpopulations to study, which screening programs to deploy. The population view is not separate from the individual view but is built from many individual views aggregated.

Mechanism discovery emerges from surveillance. When patterns repeat across patients in ways that current biological knowledge does not explain, the patterns suggest novel mechanisms. INTERCEPTA generates hypotheses for experimental validation. The hypotheses are not the system's authoritative claims about biology; they are leads for human researchers to investigate, with the system providing the pattern recognition that humans alone could not perform.

Prevention is the long-term goal of surveillance. Cellular states detected before clinical disease manifests can suggest preventive interventions. The system characterizes pre-disease patterns — cellular signatures that precede clinical manifestation — and uses them to inform screening, monitoring, and early intervention. This is the most ambitious aspect of INTERCEPTA's vision and the longest-horizon. It depends on accumulated clinical encounter data sufficient to characterize what pre-disease cellular states look like across many diseases. We expect this capability to develop substantively only after several years of clinical deployment.

## 6.9 Failure Modes by Architectural Component

Every architectural component has characteristic failure modes. Naming them allows the system to monitor for them explicitly rather than discovering them in deployment.

**Foundation model failures.** FMs fail when inputs are far from training distribution, when cells are of types poorly represented in training, when normalization or processing differs from training preprocessing. The system detects these failures through OOD detection in MFMD and through ensemble disagreement across multiple FMs. Mitigation involves flagging affected predictions as low confidence and, in extreme cases, refusing to predict entirely.

**Mechanism inference failures.** Mechanism inference fails when relevant biology is not captured by the pathway databases or other prior knowledge sources. It fails when novel mechanisms exist that current biological knowledge does not encode. The system detects these failures through mechanism mismatch detection: poor fit between mechanism representation and cellular data. Mitigation involves flagging the mismatch and triggering deeper investigation — potentially mechanism discovery work that hypothesizes the missing biology.

**Drug response prediction failures.** Drug response prediction fails when training data does not represent the patient's cellular context, when the drug's mechanism is misunderstood, when the relevant target population is underrepresented. The system detects these failures through internal disagreement detection and through population-specific calibration audit. Mitigation includes flagging predictions for underrepresented populations, prioritizing data acquisition to close gaps, and refusing predictions where confidence is unsupportable.

**Uncertainty layer failures.** The uncertainty layer itself can fail by being miscalibrated, by missing OOD inputs that should have been flagged, or by being overly conservative and refusing predictions where confidence would be justified. The system detects these failures through periodic calibration audit and through external benchmarking. Mitigation includes recalibration when drift is detected and methodology updates when systematic miscalibration is identified.

**Coordination failures.** Components can produce outputs inconsistent with each other in ways that suggest the coordination layer has problems. The system detects these failures through consistency checks across component outputs and through end-to-end testing on known cases. Mitigation involves diagnosing where the coordination broke down and updating the relevant interfaces or components.

Failure modes mapped to immune system analogs:

Autoimmune-equivalent (false positives, claiming response where none exists) is monitored through specificity audit on known negative cases. The system should not predict response where mechanism does not support it. When false positives are detected, investigation focuses on whether mechanism inference is producing spurious patterns or whether prediction is uncoupled from mechanism in ways that should not occur.

Immunodeficiency-equivalent (false negatives, missing real signal) is monitored through sensitivity audit on known positive cases. The system should not miss responses that mechanism predicts. When false negatives are detected, investigation focuses on whether the relevant cellular states are being characterized correctly and whether mechanism inference is missing important biology.

Allergy-equivalent (miscalibration, overconfidence) is monitored through calibration audit. The system's confidence should match its empirical accuracy. When miscalibration is detected — confidence systematically higher than accuracy supports — recalibration is triggered, often along with investigation of what produced the overconfidence.

These three failure modes are characteristic of any system with INTERCEPTA's architectural pattern. Monitoring for them explicitly is the architectural commitment that ensures failures are detected and addressed rather than hidden.

This architecture, taken as a whole, is what INTERCEPTA is. The chapters that follow specify what INTERCEPTA does (Chapter 7), what it delivers (Chapter 8), how its commitments operate (Chapters 9-11), how it operates in practice (Chapter 12), the technical milestones that build it (Chapter 13), and the human, economic, and risk dimensions that surround it (Chapters 14-17). The architecture is the spine that holds the rest together.

---

## Figures Planned for This Chapter

**F6.1: Master Architecture Diagram** — Already produced. The single most important figure in the book. Full INTERCEPTA architecture with all six layers labeled, immune-system parallels indicated alongside each layer, data flow arrows showing component coordination, failure modes panel at bottom.

**F6.2: Innate vs Adaptive Layers** — Side-by-side detailed comparison. Innate layer (FM ensemble, fast, generic, applies to anything) versus adaptive layer (per-disease learning, slow, specific, gets better with exposure). Shows how the two layers coordinate, what each handles, where the handoff happens.

**F6.3: Memory Dynamics** — Visual showing how patient encounters become structured knowledge over time. Encoding processes (pattern detection, mechanism extraction, calibration update) shown explicitly. Retrieval processes (similarity computation, evidence aggregation) shown explicitly. Memory size and structure depicted as growing function of patient encounters.

**F6.4: Failure Mode Mapping** — Architectural diagram showing each component with its characteristic failure modes and the detection mechanisms that monitor for them. Mirror diagram showing immune system failure modes (autoimmune, immunodeficiency, allergy) for each computational failure mode (false positive, false negative, miscalibration).
