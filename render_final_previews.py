"""Render proof of motion from the exact validated atlas; no character editing."""

import argparse
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

from pet_layout import ROW_DURATIONS


def write_gif(frames, durations, path):
    frames[0].save(path, save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, disposal=2, optimize=False)


def labeled(cell, label):
    out = Image.new('RGB', (192, 240), '#f2f3f5')
    out.paste(cell, (0, 32), cell)
    ImageDraw.Draw(out).text((8, 10), label, fill='#26344b')
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--atlas', required=True)
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    atlas = Image.open(args.atlas).convert('RGBA')
    if atlas.size != (1536, 2288):
        raise ValueError('Expected final v2 atlas')
    durations = ROW_DURATIONS
    cells = {}
    all_frames, all_durations = [], []
    for row, (state, times) in enumerate(durations.items()):
        folder = out / 'frames' / state
        folder.mkdir(parents=True, exist_ok=True)
        cells[state] = []
        for col, ms in enumerate(times):
            cell = atlas.crop((col * 192, row * 208, (col + 1) * 192, (row + 1) * 208))
            cell.save(folder / f'{col:02d}.png')
            cells[state].append(cell)
            all_frames.append(labeled(cell, f'{state}  {col + 1}/{len(times)}'))
            all_durations.append(ms)
    write_gif(all_frames, all_durations, out / 'all-states.gif')
    transition = cells['idle'] + cells['jumping'] + cells['idle']
    transition_times = durations['idle'] + durations['jumping'] + durations['idle']
    write_gif(transition, transition_times, out / 'idle-jump-idle.gif')
    looks = []
    labels = ['000', '022.5', '045', '067.5', '090', '112.5', '135', '157.5',
              '180', '202.5', '225', '247.5', '270', '292.5', '315', '337.5']
    for index, label in enumerate(labels):
        row, col = 9 + index // 8, index % 8
        cell = atlas.crop((col * 192, row * 208, (col + 1) * 192, (row + 1) * 208))
        looks.append(labeled(cell, 'look ' + label))
    write_gif(looks, [180] * 16, out / 'look-loop.gif')
    stills = [labeled(cells['idle'][0], 'idle'), labeled(cells['waving'][2], 'waving'),
              labeled(cells['jumping'][2], 'jump peak'), labeled(cells['review'][3], 'review')]
    still_sheet = Image.new('RGB', (192 * 4, 240), '#f2f3f5')
    for index, still in enumerate(stills):
        still_sheet.paste(still, (index * 192, 0))
        still.save(out / f'still-{index + 1}.png')
    still_sheet.save(out / 'four-state-stills.png')
    command = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo',
               '-pixel_format', 'rgb24', '-video_size', '384x480', '-framerate', '25',
               '-i', '-', '-an', '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
               '-movflags', '+faststart', str(out / 'all-states.mp4')]
    flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                               creationflags=flags)
    for frame, ms in zip(all_frames, all_durations):
        data = frame.resize((384, 480), Image.Resampling.NEAREST).tobytes()
        for _ in range(max(1, round(ms / 40))):
            process.stdin.write(data)
    process.stdin.close()
    error = process.stderr.read().decode('utf-8', errors='replace')
    if process.wait() != 0:
        raise RuntimeError(error)
    report = {'ok': True, 'atlas': str(Path(args.atlas).resolve()),
              'output_dir': str(out.resolve()), 'standard_frames': len(all_frames),
              'look_frames': len(looks), 'source': 'Exact final atlas cell crops'}
    (out / 'preview-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
