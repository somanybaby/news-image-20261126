[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/somanybaby/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/somanybaby/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

# news-image-20261126 entry

One image that sums up the world news of **Thursday 26 November 2026**, drawn
as a newspaper front page: the date in large type, the day's lead story
(US proposes new tariffs on 14 trading partners), and five more panels —
Trump and NATO chief urge Russia not to widen the war, Israeli strikes kill
at least nine in Gaza, Kim Jong Un vows to build more nuclear weapons, the
EU split over its budget and a $49bn loan to Ukraine, and the Bangkok oil
depot blast and Cairo tanker crash. Every story was checked against that
day's reporting (Reuters, AP, AFP, Al Jazeera, SCMP).

## How it works

`main.py` (Python 3, standard library only) contains **no embedded image
data**. The front page is drawn at run time by the program itself: a
hand-defined 5x7 bitmap font, a small word-wrapping typesetter, and a
minimal PNG writer built on `struct` and `zlib`. Running the program
renders the whole page — deep blue background, masthead, lead panel and
five story panels — pixel by pixel, then writes it out as a PNG.

## Run it

```sh
python3 main.py                        # writes /output/entry.png
MAKEFUN_OUTPUT_DIR=/tmp/out python3 main.py
```

The output goes to `$MAKEFUN_OUTPUT_DIR/entry.png` (default
`/output/entry.png`). The render is fully deterministic: repeated runs
produce byte-for-byte identical files.

## Output

- Format: PNG, 1024x1024, 8-bit RGB
- Size: 19266 bytes
- sha256: 747bb7cfc40aaccca3d037098a70360a81deb1c711a5bba46798e0c7fb7f5baa
