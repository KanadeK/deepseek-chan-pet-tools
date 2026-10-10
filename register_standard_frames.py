"""Correct row-union fitting scale while preserving connected extracted pixels."""

import argparse
import json
import shutil
from pathlib import Path

from PIL import Image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--frames-root', required=True)
    parser.add_argument('--report', required=True)
    args = parser.parse_args()
    root = Path(args.frames_root)
    backup = root.with_name(root.name + '-before-registration')
    if backup.exists():
        raise FileExistsError('Registration already has a preserved input; do not run twice')
    shutil.copytree(root, backup)
    with Image.open(root / 'idle/00.png') as opened:
        idle_box = opened.convert('RGBA').getbbox()
    jump_boxes = []
    for index in (0, 4):
        with Image.open(root / f'jumping/{index:02d}.png') as opened:
            jump_boxes.append(opened.convert('RGBA').getbbox())
    jump_height = sum(box[3] - box[1] for box in jump_boxes) / 2
    scale = jump_height / (idle_box[3] - idle_box[1])
    if not 0.80 <= scale <= 1.0:
        raise ValueError(f'Requires source review: unexpected cross-row scale {scale}')
    width, height = round(192 * scale), round(208 * scale)
    x = round(96 - 96 * scale)
    y = round(203 - 203 * scale)
    rows = []
    for folder in sorted(path for path in root.iterdir() if path.is_dir()):
        if folder.name == 'jumping':
            rows.append({'state': folder.name, 'scale': 1.0, 'offset': [0, 0]})
            continue
        for path in sorted(folder.glob('*.png')):
            with Image.open(path) as opened:
                resized = opened.convert('RGBA').resize((width, height), Image.Resampling.LANCZOS)
            frame = Image.new('RGBA', (192, 208), (0, 0, 0, 0))
            frame.alpha_composite(resized, (x, y))
            frame.save(path)
        rows.append({'state': folder.name, 'scale': scale, 'offset': [x, y]})
    report = {'input_backup': str(backup.resolve()), 'idle_height_before': idle_box[3] - idle_box[1],
              'jump_rest_height': jump_height, 'rows': rows,
              'reason': 'Bundled extraction fits the jumping union with headroom. Apply one shared transform to every non-jump row to match body size; keep jumping lift and all temporal order.'}
    Path(args.report).write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
