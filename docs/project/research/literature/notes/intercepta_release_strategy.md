# Q10 anchor 2 — INTERCEPTA release strategy considerations

## 0. Strategic considerations

If INTERCEPTA succeeds, the question becomes: **how does INTERCEPTA itself release its work?**

## 1. Options

### Option A: Full open-source release
- Charter §7 alignment: maximally open
- Trade-off: no IP protection; potential for commercial competitor to use INTERCEPTA work
- Aligned with field norms (scvi-tools, scanpy, scIB, CPA all open)

### Option B: Open code + paid premium services
- Reference implementation open; commercial cloud-hosted version with support, scaling, additional features
- Examples: Hugging Face, Databricks (Spark), Anaconda
- Trade-off: requires building services layer

### Option C: Open data + closed model weights
- Code public, model weights gated (e.g., Llama-style "open weights" with usage license)
- Examples: Meta Llama, several proprietary FMs
- Trade-off: limits research adoption

### Option D: Patent + license
- File patents on novel components (layered architecture, FM+Q3 integration, cross-disease evaluation)
- License to pharma partners
- Trade-off: slows research community access; revenue potential

## 2. Charter alignment

Charter principles include open science orientation. **Option A (full open-source) is most aligned with the Charter philosophy.**

**However:** Options B-D may be revisited at Layer 5+ depending on:
- Whether INTERCEPTA achieves the universality claim (Charter U1-U3)
- Whether commercial partners emerge
- Whether reproducibility benefits warrant withholding some components

## 3. INTERCEPTA implications

**For Q10:** Default to Option A (full open-source) per Charter alignment. **Revisit at Layer 5+ if commercial path emerges.**

— Claude (CSO), 2026-05-10
