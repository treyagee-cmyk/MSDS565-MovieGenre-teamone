import sys, urllib.request
from pathlib import Path
import pandas as pd
DATA = Path("data"); OUT = DATA / "mpst_imdb_movies.csv"
def fetch(name):
    p = DATA / f"{name}.tsv.gz"
    if not p.exists():
        print(f"Downloading {name} from IMDB...")
        urllib.request.urlretrieve(f"https://datasets.imdbws.com/{name}.tsv.gz", p)
    return p
def read(name, cols, ids):
    parts = pd.read_csv(fetch(name), sep="\t", usecols=cols, na_values="\\N", dtype=str, quoting=3, chunksize=500_000)
    return pd.concat(c[c["tconst"].isin(ids)] for c in parts)
DATA.mkdir(exist_ok=True)
mpst = pd.read_csv(sys.argv[1]); ids = set(mpst["imdb_id"])
basics = read("title.basics", ["tconst","primaryTitle","startYear","runtimeMinutes","genres"], ids)
ratings = read("title.ratings", ["tconst","averageRating","numVotes"], ids)
df = (mpst[["imdb_id","plot_synopsis","synopsis_source","split"]]
      .merge(basics.rename(columns={"tconst":"imdb_id"}), on="imdb_id")
      .merge(ratings.rename(columns={"tconst":"imdb_id"}), on="imdb_id", how="left"))
df = df[df["genres"].notna()]
dum = df["genres"].str.get_dummies(sep=",")
meta = ["imdb_id","primaryTitle","plot_synopsis","synopsis_source","split","startYear","runtimeMinutes","averageRating","numVotes"]
out = pd.concat([df[meta].reset_index(drop=True), dum.reset_index(drop=True)], axis=1)
out.to_csv(OUT, index=False)
print(f"Saved {OUT}: {len(out):,} movies, {dum.shape[1]} genres")
