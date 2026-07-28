# S&M Realty — Site + Auto-Update Pipeline

## What's in here
- `index.html`, `listings.html`, `properties/`, `css/`, `js/` — the site itself
  (currently includes all 158 listings from your latest AlterEstate pull)
- `known_listings.json` — tracks which listings are already on the site, so the
  pipeline only adds genuinely new ones each run
- `pipeline/` — the Python scripts that fetch, generate, and update pages
- `.github/workflows/update-listings.yml` — runs the pipeline once a day

## One-time setup

1. **Push this folder to a new GitHub repo** (e.g. `sm-realty-site`).
2. **Add your AlterEstate token as a secret**: repo → Settings → Secrets and
   variables → Actions → New repository secret → name it `AETOKEN`, paste
   your token.
3. **Connect Netlify to this repo**: Netlify → Add new site → Import an
   existing project → GitHub → select this repo. Leave the build command
   blank, set the publish directory to `/`.

That's it — from here on, the workflow runs daily, checks AlterEstate for
new listings, generates their property pages, updates `listings.html`, and
pushes the change. Netlify picks up every push automatically and redeploys.

## Manually running it
From the Actions tab in GitHub, you can also click "Run workflow" any time
to check for new listings immediately instead of waiting for the daily run.

## Known issue to watch for
A batch of listings can occasionally come back from AlterEstate's API with
full data (photos, description, etc.) even though the live listing has
actually been taken down. If a newly-added property page 404s when you
click it live, that's this happening — just delete that one
`properties/<slug>.html` file, remove its card from `listings.html`, and
remove its slug from `known_listings.json` (or ask Claude to do it for you
next time).
