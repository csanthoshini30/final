"""
Master Training Script - Train All Models
"""
import sys
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from training.train_engine import run_engine_training
from training.train_electrical import run_electrical_training
from training.train_hydraulic import run_hydraulic_training

def main():
    """Train all models"""
    start_time = time.time()

    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "AIRCRAFT PREDICTIVE MAINTENANCE SYSTEM" + " " * 10 + "║")
    print("║" + " " * 20 + "COMPLETE TRAINING PIPELINE" + " " * 12 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    try:
        # Train Engine Models
        print("\n[1/3] Training Engine Models...")
        print("-" * 60)
        engine_results = run_engine_training()
        print("\n✓ Engine training completed!")

        # Train Electrical Models
        print("\n[2/3] Training Electrical Models...")
        print("-" * 60)
        electrical_results = run_electrical_training()
        print("\n✓ Electrical training completed!")

        # Train Hydraulic Models
        print("\n[3/3] Training Hydraulic Models...")
        print("-" * 60)
        hydraulic_results = run_hydraulic_training()
        print("\n✓ Hydraulic training completed!")

        # Summary
        elapsed_time = time.time() - start_time
        minutes, seconds = divmod(int(elapsed_time), 60)

        print("\n")
        print("╔" + "=" * 58 + "╗")
        print("║" + " " * 15 + "TRAINING COMPLETED SUCCESSFULLY" + " " * 12 + "║")
        print("║" + " " * 58 + "║")
        print(f"║  Total Time: {minutes}m {seconds}s".ljust(59) + "║")
        print("║" + " " * 58 + "║")
        print("║  All models have been trained and saved to:".ljust(59) + "║")
        print("║  - models/engine/".ljust(59) + "║")
        print("║  - models/electrical/".ljust(59) + "║")
        print("║  - models/hydraulic/".ljust(59) + "║")
        print("║" + " " * 58 + "║")
        print("║  Next steps:".ljust(59) + "║")
        print("║  1. Build RAG knowledge base: python rag/build_index.py".ljust(59) + "║")
        print("║  2. Run dashboard: streamlit run dashboard/app.py".ljust(59) + "║")
        print("╚" + "=" * 58 + "╝")
        print()

        return 0

    except Exception as e:
        print(f"\n✗ Error during training: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
