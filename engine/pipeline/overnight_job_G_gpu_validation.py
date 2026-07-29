#!/usr/bin/env python
"""
INTERCEPTA Layer 1 Overnight Job G: GPU Validation
==================================================

Tiny diagnostic. Checks whether GPU is accessible on Northeastern Explorer.
Tests:
1. Can we run on GPU partition?
2. Is CUDA/PyTorch importable?
3. Is a GPU device visible?
4. What GPU model and memory?

Output: results/gpu_validation_report.json

Per charter Q9: validates infrastructure prerequisite for foundation model work.
"""
import json
import sys
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

OUTPUT = Path("/scratch/akula.pra/INTERCEPTA/results/gpu_validation_report.json")

def main():
    print("=" * 70)
    print("INTERCEPTA Layer 1 Job G: GPU Validation")
    print("Started: " + datetime.now(timezone.utc).isoformat())
    print("=" * 70)
    
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "hostname": platform.node(),
        "python_version": sys.version,
    }
    
    # nvidia-smi
    print("\n[1/4] Running nvidia-smi...")
    try:
        result = subprocess.run(
            ["nvidia-smi"],
            capture_output=True, text=True, timeout=30
        )
        report["nvidia_smi_returncode"] = result.returncode
        report["nvidia_smi_stdout"] = result.stdout
        report["nvidia_smi_stderr"] = result.stderr
        if result.returncode == 0:
            print("  nvidia-smi OK")
            print(result.stdout[:500])
        else:
            print("  nvidia-smi FAILED: " + result.stderr[:200])
    except Exception as e:
        report["nvidia_smi_error"] = str(e)
        print("  nvidia-smi exception: " + str(e))
    
    # PyTorch CUDA
    print("\n[2/4] Testing PyTorch CUDA...")
    try:
        import torch
        report["torch_version"] = torch.__version__
        report["torch_cuda_available"] = torch.cuda.is_available()
        if torch.cuda.is_available():
            report["torch_cuda_device_count"] = torch.cuda.device_count()
            report["torch_cuda_devices"] = []
            for i in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(i)
                report["torch_cuda_devices"].append({
                    "index": i,
                    "name": props.name,
                    "total_memory_gb": round(props.total_memory / 1e9, 2),
                    "major": props.major,
                    "minor": props.minor,
                })
            print("  CUDA available: {} devices".format(torch.cuda.device_count()))
            for d in report["torch_cuda_devices"]:
                print("    [{}] {} ({} GB)".format(d["index"], d["name"], d["total_memory_gb"]))
        else:
            print("  CUDA not available via PyTorch")
    except ImportError as e:
        report["torch_import_error"] = str(e)
        print("  PyTorch not installed: " + str(e))
    except Exception as e:
        report["torch_error"] = str(e)
        print("  PyTorch error: " + str(e))
    
    # Tiny tensor test
    print("\n[3/4] Tiny tensor test on GPU...")
    try:
        import torch
        if torch.cuda.is_available():
            t = torch.randn(1000, 1000, device="cuda")
            result_tensor = t @ t.T
            report["gpu_tensor_test"] = "SUCCESS"
            report["gpu_tensor_test_result_shape"] = list(result_tensor.shape)
            print("  Tensor multiplication on GPU: OK ({}x{})".format(*result_tensor.shape))
            del t, result_tensor
            torch.cuda.empty_cache()
        else:
            report["gpu_tensor_test"] = "SKIPPED_NO_GPU"
            print("  Skipped (no GPU)")
    except Exception as e:
        report["gpu_tensor_test"] = "FAILED"
        report["gpu_tensor_test_error"] = str(e)
        print("  Tensor test failed: " + str(e))
    
    # HuggingFace ecosystem check
    print("\n[4/4] Checking HuggingFace ecosystem...")
    for pkg in ["transformers", "huggingface_hub", "accelerate", "peft"]:
        try:
            module = __import__(pkg)
            version = getattr(module, "__version__", "unknown")
            report["pkg_" + pkg] = version
            print("  {}: {}".format(pkg, version))
        except ImportError:
            report["pkg_" + pkg] = "NOT_INSTALLED"
            print("  {}: NOT INSTALLED".format(pkg))
    
    # Decision summary
    print("\n" + "=" * 70)
    decisions = []
    if report.get("torch_cuda_available"):
        decisions.append("GPU_ACCESSIBLE")
    else:
        decisions.append("GPU_NOT_ACCESSIBLE_FROM_THIS_NODE")
    if report.get("gpu_tensor_test") == "SUCCESS":
        decisions.append("GPU_FUNCTIONAL")
    if report.get("pkg_transformers", "NOT_INSTALLED") != "NOT_INSTALLED":
        decisions.append("HUGGINGFACE_READY")
    else:
        decisions.append("HUGGINGFACE_NEEDS_INSTALL")
    
    report["decisions"] = decisions
    print("DECISIONS: " + ", ".join(decisions))
    print("=" * 70)
    
    # Write report
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print("\nReport written: " + str(OUTPUT))
    print("Finished: " + datetime.now(timezone.utc).isoformat())


if __name__ == "__main__":
    main()
