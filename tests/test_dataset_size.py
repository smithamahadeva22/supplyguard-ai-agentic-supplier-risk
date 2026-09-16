from app.data.generator import generate
import pandas as pd
from pathlib import Path

def test_generated_dataset_has_100_suppliers():
    generate()
    root = Path(__file__).resolve().parents[1]
    suppliers = pd.read_csv(root / "data/suppliers.csv")
    docs = list((root / "data/documents").glob("SUP-*.txt"))
    assert len(suppliers) == 100
    assert "SUP-0100" in set(suppliers["supplier_id"])
    assert len(docs) == 100
