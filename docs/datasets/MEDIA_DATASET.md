# Media Dataset Manifest

The demo dataset is represented in `app.seed.MEDIA_SEED` and should be uploaded
as MP3 files to Supabase Storage. Audio files are not committed to Git.

## Storage Layout

Bucket:

```text
media-demo
```

Object paths:

| Type | Count | Path pattern |
|---|---:|---|
| Music | 10 | `music/NN-name.mp3` |
| Podcast/spoken audio | 10 | `podcast/NN-name.mp3` |

Every file should be:

- Format: `.mp3`
- Duration: 20 seconds
- License: royalty-free, public-domain, Creative Commons with compatible terms,
  or created by the team for demo use

## Current Seed Items

| Type | Category | Title | Object path |
|---|---|---|---|
| song | relax | Calm Morning Pad | `music/01-calm-morning-pad.mp3` |
| song | relax | Soft Rain Keys | `music/02-soft-rain-keys.mp3` |
| song | focus | Low Focus Pulse | `music/03-low-focus-pulse.mp3` |
| song | focus | Clean Study Loop | `music/04-clean-study-loop.mp3` |
| song | sleep | Night Breath Drone | `music/05-night-breath-drone.mp3` |
| song | happy | Light Steps | `music/06-light-steps.mp3` |
| song | happy | Warm Smile Beat | `music/07-warm-smile-beat.mp3` |
| song | sad_support | Gentle Hold | `music/08-gentle-hold.mp3` |
| song | anger_release | Grounding Low Tone | `music/09-grounding-low-tone.mp3` |
| song | energy_recover | Small Energy Rise | `music/10-small-energy-rise.mp3` |
| podcast | relax | Bai tho 4-7-8 | `podcast/01-breathing-478.mp3` |
| podcast | relax | Dung lai mot phut | `podcast/02-one-minute-pause.mp3` |
| podcast | focus | Bat dau tap trung | `podcast/03-start-focus.mp3` |
| podcast | sleep | Chuan bi nghi ngoi | `podcast/04-prepare-rest.mp3` |
| podcast | happy | Giu nang luong tot | `podcast/05-keep-good-energy.mp3` |
| podcast | sad_support | O canh noi buon | `podcast/06-with-sadness.mp3` |
| podcast | sad_support | Tu noi loi tu te | `podcast/07-kind-self-talk.mp3` |
| podcast | anger_release | Ha nhiet con gian | `podcast/08-cool-down-anger.mp3` |
| podcast | energy_recover | Nap lai nang luong | `podcast/09-energy-recover.mp3` |
| podcast | relax | Goi ten cam xuc | `podcast/10-name-the-feeling.mp3` |

## Suggested Preparation Flow

Use source audio that the team is allowed to use, then cut and encode each file:

```bash
ffmpeg -i source.mp3 -ss 00:00:10 -t 20 -vn -acodec libmp3lame -b:a 128k output.mp3
```

Place the output files in a local folder matching the object paths, for example
`media-dataset/music/01-calm-morning-pad.mp3`, then upload:

```bash
python scripts/upload_media_dataset.py --dataset-dir ./media-dataset
```

After upload, seed metadata:

```bash
python -m app.seed
```

When `SUPABASE_URL` is configured, seed data stores public object URLs like:

```text
https://<project-ref>.supabase.co/storage/v1/object/public/media-demo/music/01-calm-morning-pad.mp3
```

Without `SUPABASE_URL`, seed data stores placeholder URLs:

```text
supabase://media-demo/music/01-calm-morning-pad.mp3
```

## License Tracking

For the final report/demo, record one row per file:

| Object path | Source URL | License | Original author | Clip range |
|---|---|---|---|---|
| `music/01-calm-morning-pad.mp3` | TBD | TBD | TBD | 00:00-00:20 |

Do not use copyrighted commercial songs or podcast episodes unless the team has
explicit permission.
