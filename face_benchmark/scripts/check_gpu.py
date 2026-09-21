import onnxruntime as ort


def main():
    print("=" * 60)
    print("Kinetic HR Face Benchmark")
    print("GPU Environment Check")
    print("=" * 60)

    print(f"ONNX Runtime: {ort.__version__}")

    providers = ort.get_available_providers()

    print("\nProviders:")

    for provider in providers:
        print(f"- {provider}")

    if "CUDAExecutionProvider" not in providers:
        raise RuntimeError(
            "CUDAExecutionProvider is unavailable."
        )

    print("\n[OK] CUDAExecutionProvider is available.")


if __name__ == "__main__":
    main()