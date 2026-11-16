"""One-command index rebuild entry point."""
import argparse
from app.ingest import build_index

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true")
    args = ap.parse_args()
    build_index(refresh=args.refresh)
