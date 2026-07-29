# Chapter 7: What INTERCEPTA Does

*PART THREE: CAPABILITIES*

---

Chapter 6 specified the architecture. This chapter specifies the capabilities that the architecture produces. The distinction matters: architecture is the structure; capabilities are what the structure can do. A patient and a clinician interacting with INTERCEPTA do not see the architecture. They see the capabilities. This chapter is the catalog of those capabilities.

Each capability is described concretely: what it does, what it takes as input, what it produces as output, what its limits are. Each capability is mapped to the architectural components from Chapter 6 that produce it. Each capability is paired with its immune-system analog where the analog clarifies meaning.

The capabilities are not all of equal importance. Some — cellular state characterization, mechanism inference, drug response prediction — are core. Others — combinatorial intervention modeling, causal counterfactual prediction — are advanced and develop over time. The chapter covers all of them because all of them are required for the fullest vision; none can be omitted without compromising the system.

These capabilities are what we mean when we said in Chapter 1 that capabilities are bricks. Vision is the architecture; capabilities are the bricks that make the architecture concrete. Without these specific capabilities, working at production quality, INTERCEPTA is a beautiful idea without execution. The book emphasizes vision because vision is what most documents get wrong; it emphasizes capabilities because capabilities are what most companies fail to deliver.

## 7.1 Cellular State Characterization

The foundational capability. INTERCEPTA reads cellular data from any patient with any disease and produces a characterization of the cellular state.

Input: single-cell RNA sequencing data from a patient sample, with appropriate metadata about the sample (tissue type, processing protocol, patient demographic information where consented). The input format is standardized, reflecting the conventions of the single-cell community: cell-by-gene expression matrices in formats like AnnData or Seurat objects, with quality metrics that allow filtering of low-quality cells.

Processing: foundation model embedding produces vector representations of each cell. Quality control identifies and handles outlier cells, doublets, dead or dying cells. Cell type annotation assigns each cell to a known type or flags it as ambiguous. Cellular state inference characterizes each cell beyond type — what state it is in, what programs it is running, what trajectory position it occupies.

Output: a structured characterization including cell type composition (which types are present, in what proportions), cellular state distributions within each type (what states the cells of each type are in), trajectory positions (where cells fall on relevant developmental and functional trajectories), and quality indicators (which cells were filtered, which annotations are confident, which require additional review).

Limits: characterization quality depends on input data quality. Poorly processed samples produce limited characterization. Rare cell types may be missed if their representation is too sparse. Cell types not represented in foundation model training may be misannotated. The system flags these limitations rather than hiding them.

Architectural mapping: foundation model layer (innate response) does the embedding work. Mechanism inference layer (early stages) provides cellular state interpretation. Uncertainty layer flags edge cases.

Immune-system analog: pattern recognition by innate immune cells. The immune system characterizes the threat — what kind of pathogen, what tissue context — to inform appropriate response.

## 7.2 Mechanism Inference

Identifies which cellular pathways and processes are dysregulated in disease and which are perturbed by candidate interventions.

Input: cellular state characterization from 7.1, optionally combined with disease context information.

Processing: pathway activity inference identifies which biological pathways are activated, suppressed, or dysregulated in the patient's cellular state. KAALCURA-style mechanistic axes are inferred when applicable: for cancer, axes like proliferation, EMT, DNA damage response; for autoimmune disease, axes appropriate to that biology; for neurodegeneration, similar with disease-appropriate axes. The inference is dynamic — axes are learned per disease rather than hardcoded universally.

Causal vs correlational distinction is attempted. Pure pattern recognition identifies co-occurring features; mechanism inference goes further by identifying which features are causally related. The distinction is harder than pure pattern matching but more useful for intervention recommendation. The methods INTERCEPTA uses for this include causal graph inference, perturbation-informed analysis (where perturbation data is available), and mechanism-aware regularization that penalizes spurious correlational explanations.

Output: structured mechanism representation. For each patient, this includes which pathways are dysregulated and how, which mechanistic axes are perturbed and in what direction, which cell populations are driving the dysregulation, and which mechanisms are well-supported by the data versus which are suggestive but uncertain.

Limits: mechanism inference depends on prior biological knowledge. When disease mechanisms are poorly understood, inference is correspondingly limited. The system flags when its mechanism representation has poor fit to the cellular data — a signal that something biological is happening that current knowledge does not capture.

Architectural mapping: adaptive response layer (per-disease learning) produces mechanism representations. Coordination layer ensures mechanism representations are usable by downstream components.

Immune-system analog: antigen presentation. Dendritic cells process and present pathogen information in forms that adaptive immune cells can act on. INTERCEPTA's mechanism inference plays a similar role: presenting structured disease information to the prediction and intervention components.

## 7.3 Phenotype Target Specification

Determines what cells should become — the phenotypic target the intervention should achieve.

Input: disease context, mechanism inference output, cellular state characterization.

Processing: for each disease, INTERCEPTA infers the appropriate phenotypic target. For most cancers, the target is apoptosis (cell death) or differentiation (loss of malignant phenotype). For autoimmune disease, the target is often quiescence (return to non-activated state) or regulatory phenotype acquisition. For regenerative medicine, the target is differentiation toward functional cell types. For neurodegeneration, targets include reduced protein aggregation, restored cellular maintenance, or neuroprotection. The targets are inferred dynamically from disease biology rather than hardcoded.

The dynamic nature of target specification is critical for universality. A static system that hardcoded "cancer = apoptosis" would fail completely for autoimmune disease, where killing cells is exactly the wrong response. INTERCEPTA's commitment is that target inference is itself learned from data and biology, not fixed at design time.

Output: explicit phenotype target specification for the patient's disease, including the target cellular state(s), the cell populations that should achieve that state, and the trajectory that should be followed to reach it.

Limits: target specification requires understanding of disease biology that may be incomplete. For poorly understood diseases, the target may be uncertain. The system flags when target specification confidence is low.

Architectural mapping: this is what we call PTS — Phenotype Target Specification — implemented as part of the adaptive response layer with significant input from the mechanism inference layer.

Immune-system analog: the immune system has implicit targets — pathogen elimination, tissue repair — that shape its response. INTERCEPTA's phenotype targets play the same role: defining what success looks like at the cellular level.

## 7.4 Intervention Space Exploration

Searches the full intervention space for candidates likely to reshape cellular state toward the phenotypic target.

Input: phenotype target, mechanism representation, patient context.

Processing: candidate intervention generation considers the full space of possible interventions. Approved drugs are searched first because they have established safety and clinical use patterns. Investigational drugs in clinical trials are considered when they target relevant mechanisms. Combination therapies are considered when single agents are insufficient. Beyond drugs, the system can consider gene therapy, cell therapy, lifestyle modification, and other intervention classes when appropriate to the disease and patient context.

The search is mechanism-driven rather than label-driven. Standard pharmacology databases organize drugs by indication ("approved for lung cancer"). INTERCEPTA searches by mechanism: which interventions target the pathways and processes dysregulated in this patient. This means a drug approved for one indication can be considered for another if its mechanism matches the patient's dysregulation. This is what enables drug repositioning at scale.

Output: ranked list of candidate interventions, with predicted mechanism of action against the patient's specific dysregulation, predicted phenotype target attainment, and confidence estimates.

Limits: intervention space exploration depends on what is in the system's knowledge. New interventions not yet characterized cannot be considered. Interventions with poorly characterized mechanisms may be ranked uncertainly. The system flags these limits.

Architectural mapping: adaptive response layer combined with structured drug knowledge graphs. The DA-DMG (Disease-Agnostic Drug Mechanism Graph) we plan to build is the structured knowledge that supports this exploration. DA-DMG encodes drugs by their mechanisms rather than their indications, enabling cross-disease search.

Immune-system analog: T cell repertoire diversity. The immune system has many different receptors available; the appropriate one for a given threat is selected through encounter. INTERCEPTA similarly has many candidate interventions; the appropriate ones for a given patient are selected through mechanism matching.

## 7.5 Drug Response Prediction

Predicts how the patient's cellular state will respond to candidate drugs.

Input: cellular state characterization, mechanism representation, candidate drug list, drug knowledge.

Processing: cell-level drug response prediction uses foundation model embeddings combined with drug response training data (GDSC, CCLE, and clinical sources where available) adapted via transfer learning to the single-cell context. Patient-level outcome prediction aggregates cell-level predictions to estimate clinical response probability. Both predictions incorporate mechanism representation, so the predictions are not just statistical pattern matching but mechanistically informed.

The bifurcation of cell-level and patient-level prediction reflects the empirical finding that these are different problems. Cell-level prediction asks: how will these specific cells respond to this drug? Patient-level prediction asks: will this patient achieve clinical benefit from this drug? The two questions have different optimal architectures. INTERCEPTA's bifurcation lets each be addressed with the methods best suited to it, rather than forcing one method to handle both.

Output: for each candidate drug, predicted cell-level response (which cell populations respond, how strongly), predicted patient-level outcome (probability of clinical benefit), confidence estimate (calibrated uncertainty), and mechanism explanation (why the drug is predicted to help, what cellular processes it modulates).

Limits: prediction quality depends on training data representativeness for the patient's specific cellular context. Predictions for cell types or disease contexts poorly represented in training are flagged as low confidence. Drugs with poorly characterized mechanisms produce more uncertain predictions.

Architectural mapping: adaptive response layer using MC-FMA approach. Coordination with mechanism inference and uncertainty quantification produces integrated predictions.

Immune-system analog: cytotoxic T cell response prediction. The immune system implicitly predicts how effective its response will be against a given pathogen; INTERCEPTA explicitly predicts how effective drug response will be for a given patient.

## 7.6 Uncertainty Quantification

Quantifies confidence in predictions with calibrated, mechanistically grounded uncertainty estimates.

Input: outputs from all upstream components.

Processing: multiple sources of uncertainty are characterized. Statistical uncertainty from prediction model variance. OOD uncertainty from input being far from training distribution. Mechanism uncertainty from poor fit between mechanism representation and data. Calibration adjustments from continuous monitoring of empirical accuracy.

Output: for each prediction, calibrated confidence estimate, decomposition of uncertainty by source (which kind of uncertainty contributes how much), explicit boundaries (cases where the system refuses to predict), and natural-language explanation of confidence appropriate to the user.

The output is not just a number. A confidence estimate of 0.65 communicates much less than "65% confidence based on strong cellular state match in training data, moderate mechanism support, and ensemble agreement; uncertainty primarily from limited prior data on this drug-cellular-state combination." The decomposition is what allows the user to weigh the prediction appropriately.

Limits: uncertainty quantification can itself be miscalibrated. Continuous calibration audit catches drift; external validation provides independent verification. The system flags when its own uncertainty estimates may be unreliable.

Architectural mapping: this is the MFMD (Mechanistic Failure Mode Detection) layer.

Immune-system analog: self-tolerance. The immune system refuses to attack what it should not attack. INTERCEPTA refuses to predict where prediction is unjustified.

## 7.7 Causal Counterfactual Prediction

Predicts 'what would happen if intervention X' rather than 'what correlates with intervention X.' The distinction is fundamental for intervention recommendation.

Input: patient state, candidate interventions, mechanism representation, prior interventional data.

Processing: causal inference techniques distinguish true intervention effects from correlated patterns. Counterfactual reasoning estimates 'what would the cellular state become if we did X' rather than just 'what cellular states have we seen with X applied.' The reasoning incorporates mechanism — interventions with known mechanisms are reasoned about more confidently than those with unknown mechanisms.

The distinction between correlational and causal prediction is technical but important. Correlational prediction says: "in the training data, when patients with this cellular state received this drug, they had these outcomes." This is informative but not directly actionable, because the outcomes might be confounded by factors that drove the treatment decision in the first place. Causal prediction says: "if we intervene on this patient with this drug, the cellular state will change in this way." This is what clinical decisions need.

Output: for each candidate intervention, predicted counterfactual cellular state (what the cells would become), confidence in the counterfactual prediction, and explicit acknowledgement of confounding factors that might affect the prediction.

Limits: counterfactual prediction is fundamentally harder than correlational prediction. When training data has limited interventional content, counterfactual predictions are correspondingly weak. The system flags counterfactuals that are highly extrapolatory.

Architectural mapping: this is what we call CCP — Causal Counterfactual Prediction — integrated across mechanism inference and prediction layers.

Immune-system analog: predicting how the body will respond to a vaccine before deploying the vaccine. The biological version uses prior similar pathogens to predict; the computational version does the same with cellular states and interventions.

## 7.8 Combinatorial Intervention Modeling

Predicts response to drug combinations, models synergy and antagonism, prunes combinatorial space intelligently.

Input: patient state, candidate combination interventions, single-agent prediction data.

Processing: combination prediction goes beyond simple linear addition of single-agent effects. Synergy is predicted when two drugs target complementary mechanisms. Antagonism is predicted when drugs interfere with each other. The combinatorial space is pruned using mechanism-based criteria — only combinations with mechanistically plausible synergy are evaluated in detail.

The combinatorial space is large. Even with just 1,000 candidate drugs, pairwise combinations number 500,000; triplets exceed 100 million. Brute-force search is infeasible. Mechanism-aware pruning makes the space tractable: combinations that hit complementary pathways are prioritized; combinations targeting the same pathway are deprioritized; combinations with predicted antagonism are flagged as unfavorable.

Output: ranked combination recommendations with predicted joint response, synergy score, mechanism explanation, and confidence estimate.

Limits: combination training data is sparse compared to single-agent data. Predictions extrapolate from limited evidence. The system flags combinations where extrapolation is heavy.

Architectural mapping: this is what we call CIM — Combinatorial Intervention Modeling — built on top of single-agent prediction with explicit modeling of interaction effects.

Immune-system analog: coordinated immune response involving multiple cell types. The immune system rarely uses single-component responses; it deploys multiple cell types in coordinated combinations.

## 7.9 Trajectory Prediction

Predicts how cellular state evolves over time under intervention.

Input: baseline cellular state, intervention specification, mechanism representation, time horizon.

Processing: trajectory prediction is not just static response prediction. The system models how cells evolve in response to intervention over time. Some interventions produce rapid response. Others produce delayed response. Some produce transient response with relapse. Some produce sustained response. The trajectory shape matters for clinical decision-making.

The methods include trajectory inference from longitudinal training data, dynamical systems modeling for cellular state evolution, and continuous-time prediction architectures for asking "what will the state look like at time T?"

Output: predicted trajectory of cellular state under intervention. Time points at which clinical effects are expected. Probabilities of trajectory variations including non-response, partial response, complete response, and relapse.

Limits: trajectory prediction requires longitudinal training data. Where such data is sparse, trajectory predictions are uncertain. The system flags this.

Architectural mapping: this is what we call CSTDP — Cellular State Trajectory Drug Prediction — extending static drug response prediction to temporal dynamics.

Immune-system analog: immune response kinetics. The immune system response unfolds over time with characteristic dynamics; INTERCEPTA models intervention response with similar attention to dynamics.

## 7.10 Mechanism Discovery

Identifies novel mechanisms through pattern recognition across patients.

Input: aggregated cellular data and outcomes across many patients.

Processing: pattern recognition algorithms identify recurring relationships not captured by current biological knowledge. Novel cellular state clusters that recur across patients suggest novel disease subtypes. Recurring intervention failure patterns suggest novel resistance mechanisms. Cross-disease pattern similarities suggest universal mechanisms.

The architectural commitment for mechanism discovery is that the system generates hypotheses, not authoritative findings. Hypotheses must be validated experimentally before being treated as established mechanism. INTERCEPTA's role is pattern recognition at scale that humans alone cannot perform; humans' role is experimental validation of hypotheses worth pursuing.

Output: hypotheses about novel mechanisms, with evidence summarized, with experimental validation suggestions, with confidence estimates.

Limits: mechanism discoveries are hypotheses, not authoritative findings. They require experimental validation by human researchers. The system explicitly notes this.

Architectural mapping: this depends on the surveillance layer plus mechanism inference. The AHG (Autonomous Hypothesis Generator) we plan to build is the system component that orchestrates mechanism discovery.

Immune-system analog: somatic hypermutation in B cells. The immune system actively explores receptor space looking for better matches to threats; INTERCEPTA explores mechanism space looking for better explanations of disease.

## 7.11 Continuous Learning

Updates the system's predictions, calibrations, and knowledge as new data arrives.

Input: outcomes from past predictions, new patient data, new biological knowledge.

Processing: as outcomes are observed, they feed back into the system. Calibration updates ensure that confidence estimates remain calibrated. Mechanism understanding refines as new evidence accumulates. Drug response models update as more outcome data becomes available. The updates respect privacy boundaries — federated learning approaches are used where appropriate.

Update protocols include audit, validation, and rollback capability. Not every update is automatic; significant updates undergo review before deployment. The architecture supports both automatic minor updates (calibration drift correction) and reviewed major updates (mechanism inference algorithm changes, foundation model substitutions). The protocols protect against drift in unintended directions.

Output: updated system that produces better predictions for similar future patients.

Limits: continuous learning requires care to avoid drift in unintended directions. Update protocols include audit, validation, and rollback capability if updates degrade performance. The system flags significant updates so users know what has changed.

Architectural mapping: memory layer combined with calibration audit and update protocols.

Immune-system analog: memory cell persistence and re-encounter response improvement. The immune system gets better at responses through repeated encounter; INTERCEPTA does the same through patient encounters.

## 7.12 Each Capability Mapped to Immune-System Parallel

The capabilities above are not independent. They form a coordinated whole, mirroring the coordinated whole of the immune system. Summary table of capability-to-immune-system mappings:

- **Cellular state characterization** maps to **pattern recognition by innate cells**. Both characterize the situation before responding.
- **Mechanism inference** maps to **antigen processing and presentation**. Both produce structured representations of the threat for downstream response.
- **Phenotype target specification** maps to **implicit immune targets** like pathogen elimination and tissue repair. Both define what success looks like.
- **Intervention space exploration** maps to **T cell repertoire diversity**. Both maintain breadth of options to match diverse threats.
- **Drug response prediction** maps to **predicted T cell response effectiveness**. Both estimate how well the response will work.
- **Uncertainty quantification** maps to **self-tolerance refusal mechanisms**. Both refuse to act when action is inappropriate.
- **Causal counterfactual prediction** maps to **vaccine response anticipation**. Both predict counterfactuals from prior similar cases.
- **Combinatorial intervention modeling** maps to **multi-cell-type coordinated response**. Both deploy components in combination.
- **Trajectory prediction** maps to **immune response kinetics**. Both attend to temporal dynamics of response.
- **Mechanism discovery** maps to **somatic hypermutation exploration**. Both actively explore for better matches/explanations.
- **Continuous learning** maps to **memory cell persistence and improvement**. Both improve through encounter.

The architectural coherence is visible in this mapping. INTERCEPTA's capabilities are not arbitrary collection of features; they are the computational analog of an immune system's coordinated response to threats. This is what makes the architecture defensible and the capabilities coherent.

Vision is what we are building. Capabilities are how we build it. Vision and capabilities together — neither overshadowing the other — are what makes INTERCEPTA real.

---

## Figures Planned for This Chapter

**F7.1: Capability Map** — All 11 capabilities visualized as a coordinated architecture. Each capability has its inputs (where data flows from), outputs (where data flows to), and dependencies on other capabilities. The map makes the integration visible: no capability stands alone; all are connected.

**F7.2-F7.12: Individual Capability Diagrams** — One detailed diagram per capability showing: inputs to the capability, internal processing, outputs, architectural component mapping, immune-system analog. These figures support deep understanding of each capability for readers who want to dig in.
