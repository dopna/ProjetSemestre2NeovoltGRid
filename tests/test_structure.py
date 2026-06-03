from pathlib import Path


def test_project_structure_exists():
    root = Path(__file__).resolve().parents[1]
    assert (root / "src" / "train_model.py").exists()
    assert (root / "data" / "raw" / "releves_consommation.csv").exists()
