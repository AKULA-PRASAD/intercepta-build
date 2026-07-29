# Why Now

*PART ONE: IDENTITY*

---

## Single-Cell Sequencing Reaches Clinical Viability

If you wanted to build INTERCEPTA in 2018, you could not. The most fundamental reason is that the input data — single-cell sequencing of patient samples at clinical timelines — was not available. Single-cell RNA sequencing existed, but it was research-grade. A typical experiment took weeks from sample to data. The cost per cell was high enough that comprehensive sampling was prohibitive. The protocols required specialized expertise unavailable in most clinical settings. The bioinformatics pipeline took further weeks. By the time you had data, the patient's clinical situation had often changed.

Five things changed between 2018 and 2026 that bring single-cell sequencing into clinical viability.

First, automation. The 10x Genomics Chromium platform and its competitors automated the cell-handling and library-preparation steps that previously required hours of manual technician work. The automated systems are not just faster; they are more reproducible. Library preparation that took a skilled technician half a day can now run unattended overnight on a benchtop instrument.

Second, sequencer throughput. The latest generation of sequencing instruments — Illumina NovaSeq X, Element AVITI, others — produce reads at rates that make single-cell experiments cheap on a per-cell basis. Where a 10,000-cell experiment in 2018 might cost ten thousand dollars, in 2026 it is approaching one thousand. The cost trajectory has not stopped; further reductions are expected.

Third, protocol robustness. Early single-cell protocols failed often. Cells died during processing. Doublets confounded analysis. Capture efficiency was variable. Each of these problems has been characterized, methods to mitigate them have been developed, and quality control standards have stabilized. Protocols now succeed reliably enough that a patient sample can be expected to produce usable data the vast majority of the time.

Fourth, bioinformatics pipelines. Tools like Cell Ranger, Seurat, Scanpy, and others have matured into stable, well-documented systems. The bioinformatics steps that previously required PhD-level expertise now run as standardized pipelines. Cloud platforms host these pipelines as services, removing infrastructure burden. The human time required to process single-cell data has dropped from weeks to hours.

Fifth, clinical pathology integration. Hospitals and reference laboratories have begun adopting single-cell sequencing as a clinical service. The reimbursement frameworks are being established. The regulatory pathway for clinical single-cell tests is being clarified by FDA. The clinical workflow integration — from sample collection through result delivery to electronic health record integration — is being built.

None of these five changes is complete. Single-cell sequencing in 2026 is not yet routine clinical practice in the way that, for example, basic blood chemistry is routine. But it has moved from research-only to clinically deployable for specific use cases, with the trajectory continuing toward broader clinical use. INTERCEPTA can be built in 2026 because the input data, finally, can be obtained at clinical timelines for the cases that matter most.

## Foundation Models for Cellular Data Emerge

The second necessary condition for INTERCEPTA is foundation models for cellular data. These did not exist in any usable form before 2023. Their emergence between 2023 and 2025 is the second reason 2026 is the right moment.

To understand why foundation models matter, consider the alternative. Without foundation models, every analysis of single-cell data starts approximately from scratch. You take the gene expression matrix — cells by genes — and apply standard methods: dimensionality reduction, clustering, marker gene identification. The methods work, but they treat each dataset as independent. The lessons learned from analyzing one dataset do not transfer automatically to the next. Each new dataset requires its own analysis, its own interpretation, its own integration.

Foundation models change this. A foundation model is trained, once, on a massive amount of cellular data — tens of millions of cells from thousands of conditions and tissues. The training produces a learned representation: a way of encoding any cell into a vector of numbers that captures something meaningful about its biological state. After training, the model can be applied to new cells from new datasets, and the learned representation transfers. Cells that are biologically similar end up in nearby positions in the representation space. Cell types are recognizable. Cellular states are interpretable in the context of the training distribution.

Several foundation models for single-cell data exist by 2026. scFoundation, with about 100 million parameters, was trained on roughly 50 million single cells from human tissues, providing a generic cellular representation. Geneformer, smaller, was trained on a different cell corpus and represents cells through ranked gene expression. UCE — Universal Cell Embedding — was trained across species and tissues to provide cross-species cellular representations. scGPT applied transformer architectures to cellular data and demonstrated strong performance across multiple downstream tasks. CancerFoundation specialized in malignant cells. Each of these models has trade-offs. None is perfect. But each provides a useful starting point.

The implication for INTERCEPTA is significant. We do not have to learn cellular representations from scratch. The hardest part of representing cellular state — capturing what makes a T cell a T cell, what distinguishes proliferating cells from quiescent ones, what cellular context informs drug response — has been done at large scale by teams who have invested years of compute and labeled data into it. We build on top of this work.

Foundation models also have known limitations that we treat as design constraints rather than secrets. They have biases reflecting their training data: over-representation of human and mouse cells, under-representation of plants and microbes; over-representation of immune cells, under-representation of neural cells; over-representation of cancer cells in some models, under-representation of healthy cells in others. They struggle with rare cell types not well represented in training. Their representations capture co-expression patterns but not causal relationships. They are computational; they fail when given inputs far from the training distribution. INTERCEPTA's architecture must respect these limitations, mitigate them where possible, and characterize them honestly where they cannot be mitigated.

By 2026, the landscape of foundation models for cellular data is rich enough to provide options, mature enough to provide reliable tooling, and well-characterized enough that we know what to do with each one. This was not true in 2023. It enables INTERCEPTA in 2026.

## Drug Response Transfer Learning Becomes Real

The third necessary condition for INTERCEPTA is methods that bridge from large-scale bulk drug response data — the GDSC and CCLE databases of cancer cell line drug screens — to the single-cell context where INTERCEPTA operates. This bridge did not exist in usable form before 2022.

The need is straightforward. Drug response training data at the single-cell level is scarce. There are perhaps a few thousand single-cell experiments where drug responses have been measured at the cellular level. By contrast, the GDSC and CCLE databases contain bulk drug response measurements for hundreds of drugs across hundreds of cell lines — orders of magnitude more data, but at the bulk rather than single-cell level. To predict drug response at single-cell resolution, we need methods that can take this bulk-trained knowledge and apply it to single-cell contexts.

Several methods now exist that do this. scDEAL, published in Nature Communications in 2022, was the first major framework. It uses a Domain-Adaptive Neural Network architecture, training on bulk RNA-sequencing drug response data and then adapting via Maximum Mean Discrepancy minimization to predict drug responses on single-cell data. Reported performance on benchmark datasets is strong: F1 scores around 0.74, AUROC around 0.89 on Cisplatin response in oral squamous cell carcinoma single-cell data. SCAD, published in 2023, used adversarial domain adaptation as an alternative architecture, achieving comparable or better performance with different inductive biases. scAdaDrug, published in 2024, extended these approaches with multi-source domain adaptation, achieving SOTA performance on both single-cell and patient-level drug response prediction. scATD, published in Briefings in Bioinformatics in 2025, integrated foundation model embeddings with domain adaptation, achieving strong performance with substantially faster inference than its predecessors.

The lineage of these methods matters because it shows the field converging on a viable architectural pattern: foundation model embedding plus domain adaptation. INTERCEPTA's Layer 2A — the cell-level drug response prediction layer — builds directly on this pattern, while extending it with mechanism-aware constraints that the existing methods lack.

There are also limits to what these methods have demonstrated. They have shown that bulk-to-single-cell transfer is feasible. They have not yet demonstrated that the transfer holds up at clinical scale, across diverse cohorts, with the kind of distributional robustness that clinical deployment requires. The Elmarakeby et al. evaluation from Dana Farber, published in October 2025, found that single-cell foundation models showed limited advantages over simpler baselines for predicting patient-level cancer outcomes — even though scDrugMap, published earlier in 2025, showed that the same foundation models perform impressively at cell-level drug response prediction. This apparent conflict, examined carefully in our own analysis, resolves through task definition: cell-level and patient-level prediction are different problems, and methods optimized for one do not automatically excel at the other. INTERCEPTA's bifurcation of Layer 2 into cell-level (FM-based) and patient-level (baseline-based) tracks reflects this resolution.

In 2026, the methods exist, the limitations are known, the resolution of apparent conflicts is becoming clearer, and the architectural patterns are stabilizing. INTERCEPTA can pick up where the field is, rather than starting from architectural first principles.

## Computational Infrastructure Catches Up

INTERCEPTA needs computational resources at clinical scale. By 2026, these resources are accessible in a way they were not in earlier years.

GPU clusters that can run foundation model inference at clinical timelines exist and are widely available. Major cloud providers — AWS, Google Cloud, Microsoft Azure — offer GPU instances that can process foundation model inference on cellular data within minutes per sample. University HPC clusters, including the one INTERCEPTA's development uses at Northeastern, provide GPU resources at research scale. The cost per inference has dropped to levels where clinical deployment is economically feasible.

Storage of cellular atlases at the millions-of-cells scale is no longer prohibitive. The LuCA non-small-cell lung cancer atlas, with about 3 million cells across 30 studies, occupies on the order of 100 gigabytes — easily handled by current storage systems. Comprehensive multi-disease atlases at the tens of millions of cells scale are similarly feasible. The Cell Atlas project, the Human Cell Atlas, and disease-specific atlases provide the reference data that INTERCEPTA needs.

Distributed computation frameworks — Slurm, Kubernetes, Ray — provide the orchestration layer that lets INTERCEPTA scale from research prototype to production deployment without re-architecting. The same code that runs on a researcher's laptop can run on a GPU cluster at scale, with appropriate configuration.

Machine learning frameworks — PyTorch, JAX, Hugging Face Transformers — provide the building blocks that make foundation model deployment routine rather than research-grade. Models trained by other groups can be loaded, fine-tuned, and served with off-the-shelf tooling.

Together, these infrastructure pieces mean that the systems work required to build INTERCEPTA is challenging but bounded. We are not having to invent the infrastructure. We are using infrastructure that is now routine. This was not true in 2020.

## Regulatory Frameworks Become Receptive

INTERCEPTA's vision includes clinical deployment, which means regulatory approval. The regulatory landscape for AI/ML in clinical decision support has changed dramatically between 2020 and 2026.

The FDA's Software as Medical Device framework has matured. The 2021 Action Plan for AI/ML-Based Software as a Medical Device, the predetermined change control plan guidance, and the framework for adaptive AI systems together provide a regulatory pathway that did not exist in usable form before. AI systems can be approved with explicit provision for continued learning post-deployment, with predetermined change control plans that specify what kinds of model updates require new submissions and what kinds do not.

The Good Machine Learning Practice principles, developed jointly by FDA, Health Canada, and the UK Medicines and Healthcare products Regulatory Agency, provide guidance on validation, transparency, and ongoing monitoring that aligns with INTERCEPTA's commitments. Where INTERCEPTA's architecture commits to honest characterization of training data biases and explicit boundaries of competence, the GMLP principles ask for exactly these characterizations. Where INTERCEPTA commits to continuous validation in deployment, GMLP asks for the same. The alignment is not coincidental; the regulatory frameworks have been informed by years of dialogue between regulators, technology developers, and clinical communities.

The 21st Century Cures Act provided the legal framework distinguishing clinical decision support that requires FDA review from clinical decision support that does not. INTERCEPTA's positioning as decision support — augmenting clinician judgment rather than replacing it — fits within this framework. The specific regulatory pathway depends on the specific use case, but pathways exist.

European regulators (EMA, MHRA), Asian regulators (PMDA, NMPA), and others have developed parallel frameworks. The specifics differ but the broad direction is similar: AI in clinical decision support is welcome conditional on rigorous validation, transparent operation, and ongoing oversight.

This receptive regulatory environment is a precondition for INTERCEPTA. Five years ago, the regulatory pathway for a system like INTERCEPTA was unclear. Many AI healthcare startups built products that ultimately could not be approved because the regulatory framework had not yet defined how they should be approved. Today, the framework exists, the pathway is clear, and our commitments align with what regulators ask for.

## Trust Debt Creates an Opening

The final reason 2026 is the right moment for INTERCEPTA is uncomfortable to articulate. The field of computational drug discovery has accumulated significant trust debt, and the rebuilding of trust through demonstrated rigor creates an opening that whoever fills it will benefit from substantially.

Trust debt is the gap between what a field has claimed and what it has delivered. In computational drug discovery and AI for healthcare, the gap is real. Major investments — billions of dollars across hundreds of companies — have produced impressive demonstrations of computational capability that have not translated into deployed clinical impact at the scale promised. Drugs discovered by AI methods exist, but they are few. Clinical decision support tools deployed at scale and demonstrably improving outcomes exist, but they are also few. The gap between promise and delivery has been documented enough that regulators, clinicians, payers, and patients have become appropriately skeptical.

This skepticism is not the field's fault in any simple sense. The science is genuinely hard. The translation from computational prediction to clinical reality is genuinely complex. The funding incentives that drive overclaim are systemic. But the result is real: trust must be rebuilt before computational drug discovery achieves the scale of impact its underlying potential could support.

Whoever rebuilds the trust will benefit asymmetrically. The first computational drug discovery system that earns regulatory approval through demonstrated rigor, deploys clinically with documented benefit, and continues to improve through deployment will become the reference model. Subsequent systems will be measured against it. The first mover in trustworthy computational medicine wins not just market share but field-defining position.

INTERCEPTA's commitment to scientific honesty as institutional practice is a direct response to this opening. We are not committed to honesty because we are virtuous. We are committed to honesty because honesty is the path. Without it, the field continues to oscillate between hype and disappointment. With it — practiced rigorously, defended institutionally, demonstrated through deployment — the path to clinical impact opens.

The opening exists in 2026 because of the trust debt accumulated over preceding years. It will not stay open indefinitely. Eventually, some computational drug discovery system will demonstrate the trustworthy deployment that earns the field-defining position. The question is which system, and on what terms. INTERCEPTA's bet is that we can be that system, and that the architectural choices required to be it are choices we are willing to make.

Together, the six conditions discussed in this chapter — clinical-viability single-cell sequencing, mature foundation models for cellular data, working drug response transfer learning methods, accessible computational infrastructure, receptive regulatory frameworks, and the trust-debt opening — make 2026 the right moment for INTERCEPTA. None of these alone would be sufficient. All of them together are.

---

## Figures Planned for This Chapter

**F2.1: Technology Readiness Timeline** — Horizontal timeline 2015-2030 showing maturity curves for the six enabling conditions: single-cell sequencing, foundation models, transfer learning methods, computational infrastructure, regulatory frameworks, and trust dynamics. INTERCEPTA's launch positioned at the inflection point where all six curves cross into clinical viability.

**F2.2: Trust Debt Curve** — Two crossing curves over time: the field's accumulated trust debt rising through years of overclaim, and the trust dividend earned by systems that practice scientific honesty rigorously. INTERCEPTA positioned at the crossover point, with the dividend curve continuing upward as the debt curve plateaus.
