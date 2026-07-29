# Glossary

*Specialized terms used throughout this book.*

**Adaptive immunity:** The slow, specific component of the biological immune system. Mapped in INTERCEPTA to per-disease learning and patient-specific mechanism inference.

**Causal counterfactual prediction:** Predicting "what would happen if intervention X" rather than "what correlates with intervention X." Required for true intervention recommendation.

**Dynamic universality:** Architectural principle where every component is learned and adaptive rather than hardcoded. Enables the system to handle any disease without per-disease engineering.

**Foundation model:** A large pretrained neural network producing useful representations for downstream tasks. In single-cell context: scFoundation, Geneformer, UCE, scGPT.

**Innate immunity:** The fast, generic component of the biological immune system. Mapped in INTERCEPTA to foundation model embeddings and shared cellular representation.

**KAALCURA:** A mechanistic axes framework for cellular state characterization originating in cancer drug response prediction. Generalizable to other diseases through dynamic axis inference.

**MC-FMA:** Mechanism-Constrained Foundation Model Adaptation. INTERCEPTA's core technical approach combining foundation model embeddings with mechanistic constraints from KAALCURA-style axes.

**Mechanism inference:** The capability of identifying which cellular pathways and processes are dysregulated in disease and which are perturbed by intervention.

**Phenotype target:** The cellular state an intervention should produce. Cancer = apoptosis. Autoimmune = quiescence. Regeneration = differentiation. Inferred dynamically rather than hardcoded.

**Single-cell RNA sequencing (scRNA-seq):** Technology to read gene expression in individual cells. Foundation of cellular state characterization in INTERCEPTA.

*[Additional terms to be added as the book is written.]*
