# Local media dataset

This directory is served by the API at `/media`.

- `source/`: downloaded research datasets; ignored by Git.
- `music/`: selected Internet Archive Creative Commons music files; ignored by Git.
- `podcast/`: selected local podcast audio files; ignored by Git.
- `music_attribution.json`: original Internet Archive identifiers, artists and
  Creative Commons licence links for each imported music item.

The database stores only a local path such as `/media/music/track.mp3` in
`source_url`; it never stores the external download URL. Keep the original
dataset licence and attribution beside each imported item.
