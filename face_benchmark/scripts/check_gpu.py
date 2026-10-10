import onnxruntime as ort


def main():

    print("=" * 60)
    print("Kinetic HR")
    print("GPU Environment Check")
    print("=" * 60)

    print()

    print(
        f"ONNX Runtime Version: "
        f"{ort.__version__}"
    )

    print()

    # =====================================
    # CUDA / cuDNN DLL Preload
    # =====================================

    try:

        ort.preload_dlls(
            directory=""
        )

        print(
            "[OK] CUDA/cuDNN DLL preload"
        )

    except Exception as error:

        print(
            "[ERROR] CUDA/cuDNN DLL preload failed"
        )

        print(error)

        raise

    print()

    # =====================================
    # Execution Providers
    # =====================================

    providers = (
        ort.get_available_providers()
    )

    print(
        "Available Providers:"
    )

    for provider in providers:

        print(
            f"  - {provider}"
        )

    print()

    if (
        "CUDAExecutionProvider"
        not in providers
    ):

        raise RuntimeError(
            "CUDAExecutionProvider "
            "is unavailable."
        )

    print(
        "[OK] CUDAExecutionProvider "
        "is available."
    )

    print()

    # =====================================
    # Debug Info
    # =====================================

    print(
        "ONNX Runtime Debug Info:"
    )

    try:

        ort.print_debug_info()

    except Exception as error:

        print(
            f"[WARN] "
            f"Debug info unavailable: "
            f"{error}"
        )


if __name__ == "__main__":
    main()