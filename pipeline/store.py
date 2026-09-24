"""Data store = assets on a GitHub release (tag `data`) in a private data repo.

Repo: DATA_REPO (e.g. mattdwyer01/racing-data), falling back to this repo (GITHUB_REPOSITORY).
Token: DATA_TOKEN (fine-grained, Contents read/write on the data repo), falling back to GITHUB_TOKEN.
Keeping the data in a separate private repo lets this code repo be public without publishing the data.

Keeps data files out of git history (no repo bloat), needs no extra account,
and each file can be up to 2GB. Works with the Actions GITHUB_TOKEN
(workflow needs `permissions: contents: write`) or a personal token locally.

    python pipeline/store.py get  rq_gps_runs.parquet data/interim/rq_gps_runs.parquet
    python pipeline/store.py put  data/interim/rq_gps_runs.parquet
    python pipeline/store.py list
    python pipeline/store.py migrate owner/old-repo   # copy every asset from another repo's `data` release
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import requests

TAG = os.environ.get("DATA_RELEASE_TAG", "data")
API = "https://api.github.com"


def _repo() -> str:
    r = os.environ.get("DATA_REPO") or os.environ.get("GITHUB_REPOSITORY")
    if not r:
        sys.exit("DATA_REPO / GITHUB_REPOSITORY not set (owner/repo)")
    return r


def _h() -> dict:
    t = os.environ.get("DATA_TOKEN") or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not t:
        sys.exit("DATA_TOKEN / GITHUB_TOKEN not set")
    return {"Authorization": f"Bearer {t}", "Accept": "application/vnd.github+json"}


def release() -> dict:
    r = requests.get(f"{API}/repos/{_repo()}/releases/tags/{TAG}", headers=_h(), timeout=30)
    if r.status_code == 404:
        r = requests.post(f"{API}/repos/{_repo()}/releases", headers=_h(), timeout=30,
                          json={"tag_name": TAG, "name": "data store",
                                "body": "Pipeline data files. Managed by pipeline/store.py.",
                                "prerelease": True})
    r.raise_for_status()
    return r.json()


def assets() -> dict[str, dict]:
    rel = release()
    out, page = {}, 1
    while True:
        r = requests.get(f"{API}/repos/{_repo()}/releases/{rel['id']}/assets",
                         headers=_h(), params={"per_page": 100, "page": page}, timeout=30)
        r.raise_for_status()
        batch = r.json()
        out.update({a["name"]: a for a in batch})
        if len(batch) < 100:
            return out
        page += 1


def get(name: str, dest: str | Path) -> bool:
    """Download asset `name` to `dest`. Returns False if it doesn't exist yet."""
    a = assets().get(name)
    if not a:
        return False
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(a["url"], headers={**_h(), "Accept": "application/octet-stream"},
                      stream=True, timeout=300) as r:
        r.raise_for_status()
        with dest.open("wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
    return True


def put(path: str | Path, name: str | None = None) -> None:
    """Upload (replacing any asset of the same name)."""
    path = Path(path)
    name = name or path.name
    rel = release()
    old = assets().get(name)
    if old:
        requests.delete(f"{API}/repos/{_repo()}/releases/assets/{old['id']}",
                        headers=_h(), timeout=30).raise_for_status()
    upload = rel["upload_url"].split("{")[0]
    with path.open("rb") as f:
        r = requests.post(upload, params={"name": name}, data=f, timeout=600,
                          headers={**_h(), "Content-Type": "application/octet-stream"})
    r.raise_for_status()
    print(f"uploaded {name} ({path.stat().st_size:,} bytes)")


def migrate(src: str) -> None:
    """Copy every asset of `src`'s data release into the store repo (skips names already there).
    Reads the source with SRC_TOKEN if set (e.g. the Actions GITHUB_TOKEN), else the store token."""
    import tempfile
    sh = {**_h(), "Authorization": f"Bearer {os.environ['SRC_TOKEN']}"} if os.environ.get("SRC_TOKEN") else _h()
    have = assets()
    r = requests.get(f"{API}/repos/{src}/releases/tags/{TAG}", headers=sh, timeout=30)
    r.raise_for_status()
    rel_id, page, todo = r.json()["id"], 1, []
    while True:
        b = requests.get(f"{API}/repos/{src}/releases/{rel_id}/assets", headers=sh,
                         params={"per_page": 100, "page": page}, timeout=30)
        b.raise_for_status()
        todo += b.json()
        if len(b.json()) < 100:
            break
        page += 1
    for a in todo:
        if a["name"] in have and have[a["name"]]["size"] == a["size"]:
            print(f"skip {a['name']} (already there)")
            continue
        with tempfile.TemporaryDirectory() as d:
            dest = Path(d) / a["name"]
            with requests.get(a["url"], headers={**sh, "Accept": "application/octet-stream"},
                              stream=True, timeout=600) as g:
                g.raise_for_status()
                with dest.open("wb") as f:
                    for chunk in g.iter_content(1 << 20):
                        f.write(chunk)
            put(dest)
    print(f"migrated {len(todo)} assets from {src} to {_repo()}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    if cmd == "get":
        ok = get(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else sys.argv[2])
        print("downloaded" if ok else f"{sys.argv[2]} not in store yet")
    elif cmd == "put":
        for p in sys.argv[2:]:
            put(p)
    elif cmd == "migrate":
        migrate(sys.argv[2])
    else:
        for n, a in sorted(assets().items()):
            print(f"{a['size']:>12,}  {a['updated_at']}  {n}")
