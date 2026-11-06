# price-watch-pipeline

A tiny price watcher I run from home in Vienna. It checks a few product
search pages once or twice a day, keeps the history in SQLite, and appends
every price change to `changes.csv` so I can eyeball it in a spreadsheet.

## Why

I want to buy a couple of specific things (a TV, a monitor) and I would
rather wait for a real price drop than guess. Refreshing five tabs by hand
every day is exactly how I know I will stop doing it in a week.

## What it watches

Configured in `config.json` — right now:

- a product search on Mediamarkt AT
- the same query on Geizhals (price comparison)
- a willhaben search, because used is often cheaper

## How it works

- `sources.py` fetches a page and normalises the rows. The pages are picked
  to be boring: server-rendered, no login.
- `store.py` upserts into SQLite keyed by the listing's stable id and keeps
  a price history table.
- `watch.py` is the loop: fetch, diff, append the changed rows to
  `changes.csv`.

No framework on purpose. It has to survive me forgetting about it for a
month, and `python -m pipeline.watch --config config.json` should still give
me answers.

## Running

    python -m pipeline.watch

Takes ~30 seconds, stdlib only, Python 3.10+.
