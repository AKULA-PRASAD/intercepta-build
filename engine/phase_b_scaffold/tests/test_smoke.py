"""Stage 1 smoke test — verifies the package imports cleanly.

Per L4.1 §2.3 Stage 1 handoff criteria: "Repository structure created
and pushed to GitHub" + "Conda environment installs cleanly" require
this trivial smoke test to pass on CI before Stage 1 hands off.
"""

import sys


def test_intercepta_imports():
    """Verify intercepta package imports without error."""
    import intercepta
    assert hasattr(intercepta, "__version__")
    assert intercepta.__version__ == "0.0.1.dev0"


def test_python_version_compatible():
    """Verify running on Python 3.11+ per environment.yml."""
    assert sys.version_info >= (3, 11), \
        f"INTERCEPTA requires Python 3.11+, got {sys.version_info}"


def test_subpackages_importable():
    """Verify all 7 subpackages import per L4.1 §2.2 repo structure."""
    from intercepta import data, substrates, l7, ood, interpretability, validation, utils
    # The subpackages are empty in Stage 1; importing them is the contract


def test_pytorch_installed():
    """Verify torch importable; key dependency."""
    import torch
    assert torch.__version__.startswith("2."), \
        f"INTERCEPTA requires torch 2.x, got {torch.__version__}"


def test_anndata_installed():
    """Verify anndata importable; key dependency."""
    import anndata
    # AnnData is the canonical data structure for scRNA-seq throughout INTERCEPTA
