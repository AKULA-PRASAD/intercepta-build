# Short abstract for the bioRxiv portal (~300 words)

*Paste this into the portal's Abstract field; the full two-paragraph Abstract remains in the manuscript body.*

---

When a new or neglected pathogen — or any disease — presents with **zero activity data**, how far can a computational system
get toward credible intervention targets from sequence, structure, and transferable prior knowledge alone, and where does it
break? We built a series of pre-registered, reproduced-twice, open-data experiments that map this frontier honestly. For
bacteria, we establish a well-controlled negative (homology-based target-ID does not beat a conservation null and can fail
silently) and the one signal that breaks the ceiling: mechanistic **flux-balance gene-essentiality**, which — tested against
independent published gene-knockout data — is enriched for experimentally essential genes across six curated metabolic models
spanning three phyla, and, in a **prospective-blind suite spanning all three domains of life** (predictions locked before the answer was
consulted), clears the gate across bacteria of multiple phyla (*N. gonorrhoeae* OR 6.1, *C. jejuni* OR 3.9,
*B. thetaiotaomicron* — a new phylum — OR 8.0) and an archaeon (*M. maripaludis* OR 4.2), while failing — first-class and
un-tuned — on exactly the two organisms that break its invariant (a host-scavenging kinetoplastid parasite, OR 0.6; and an
extremely sparse de-novo model, OR 3.0). The failures fall precisely on the boundary of the "self-contained metabolism"
invariant — the signature of genuine generalization, not memorization — giving a real, mechanistically-explained deployment
envelope rather than a suspiciously-perfect sweep.

We then ask whether this extends to *any* disease class, and formalize the answer as a **transfer-condition law**: each
label-free signal transfers only as far as the biological invariant it rides on is conserved. Viruses: sequence homology to
drugged proteins is below detection, but blind **structural** homology recovers the correct drugged-enzyme class across five
viruses. A fungal pathogen (*Candida*) passes the essentiality gate; host-dependent parasites are GEM- and base-rate-specific
(*Toxoplasma* passes, *Plasmodium* sits at the statistical noise floor — a claim we correct on our own evidence). For human
cancer, a functional-dependency signal recovers known targets, generalizes to held-out cell lines, and is enriched for
patient-tumour drivers even after study-bias correction. Two load-bearing **negatives** bound the work: that dependency signal
does not transfer label-free to a zero-screen organism, and patient drug-response prediction fails external replication.
Finally these validated signals compose into an explicit **biology-class-aware router** that applies what is validated and
**abstains** where it is not — "any disease" as honest decision coverage, not a universal model. No claim is clinical; the
remaining distance to a drug is gated by new experimental information, not more computation.
