import subprocess
from pathlib import Path


def compile_po_files(base_dir: Path):
    po_files = list(base_dir.rglob("*.po"))
    if not po_files:
        print("No .po files found.")
        return

    for po_path in po_files:
        mo_path = po_path.with_suffix(".mo")
        print(f"Compiling {po_path} -> {mo_path}")
        subprocess.run(["msgfmt", "-o", str(mo_path), str(po_path)], check=True)


if __name__ == "__main__":
    src_dir = Path(__file__).resolve().parent.parent / "src" / "dama_bot"
    compile_po_files(src_dir)
    print("Done compiling locale catalogs.")
