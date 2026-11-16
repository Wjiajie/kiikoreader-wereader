#!/usr/bin/env python3
# SPDX-License-Identifier: LicenseRef-Kiikoread-Personal-Study-1.0
"""中文：固定用户选定PR59底层字节，允许界面独立演进。/ English: Pin user-selected PR59 driver bytes while UI evolves independently."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
marker=ROOT/'.kiiko-source-view.json'
SOURCE=Path(json.loads(marker.read_text())['source']) if marker.exists() else ROOT
j=json.loads((SOURCE/'tools/fixtures/pr59-driver-baseline.json').read_text())
overrides=j.get('approved_overrides',{})
assert set(overrides)<=set(j['sha256'])
checked=skipped=0
for name,digest in j['sha256'].items():
    path=SOURCE/name
    # Pico board support removed; keep fixture history without failing CI on deleted paths.
    if name.startswith('boards/pico/') and not path.is_file():
        skipped+=1
        continue
    expected=overrides[name]['sha256'] if name in overrides else digest
    assert hashlib.sha256(path.read_bytes()).hexdigest()==expected,name
    checked+=1
print('PASS:',checked,'PR59 driver/config/waveform files (',len(overrides),'approved overrides;',skipped,'removed pico paths skipped)')
