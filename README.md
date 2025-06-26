<div align="center">

# consumet-mc

<sub>A mov-cli plugin for watching Movies,Shows and Anime based off [consumet.ts](https://github.com/consumet/consumet.ts)</sub>

[![Pypi Version](https://img.shields.io/pypi/v/film-central?style=flat)](https://pypi.org/project/film-central)

</div>

## Installation

Here's how to install and add the plugin to mov-cli.

1. Install the pip package.

```sh
pip install consumet-mc
```

2. Then add the plugin to your mov-cli config.

```sh
mov-cli -e
```

```toml
[mov-cli.plugins]
consumet = "consumet-mc"
```

## Usage

```sh
Search for TV shows, movies, or anime by title, category, or genre from  provider.

Usage:
  mov-cli -s consumet.<provider> <query> 
          [--mode <mode>]
          [--page <number>]
          [--sub-or-dub <type>]
          [--server <name>]

Arguments:
  <provider>          The content provider to use. Supported providers listed below
  <query>             The search title, category, or genre depending on --mode.

Options:
  --mode <mode>       Search mode (default: title)
                        - title     Search by name
                        - category  Use one of the categories listed below (per provider)
                        - genre     Use one of the genres listed below (per provider)
  --page <number>     Result page to fetch (default: 1)
  --sub-or-dub <type> Anime episode type (anime only):
                        - sub (default)
                        - dub
  --server <name>     Server to use for playback (see provider-specific servers below)

──────────────────────────────────────────────────────────────
Provider: allanime
  Categories: -
  Genres:     -
  Servers:    yt-mp4, mp4, fm-hls

Provider: animepahe
  Categories: latest-releases
  Genres:     -
  Servers:    kwik

Provider: aniworld
  Categories: popular-anime
  Genres:     -
  Servers:    filemoon, voe

Provider: dramacool
  Categories: recent-drama, recent-movies
  Genres:     -
  Servers:    streamwish, standard server

Provider: flixhq
  Categories: recent-movies, trending-movies, trending-tv-shows
  Genres:     -
  Servers:    upcloud, vidcloud, akcloud

Provider: hianime
  Categories: most-popular, top-airing, most-favorite, latest-completed
              recently-updated, recently-added, subbed-anime,dubbed-anime
  Genres:     -
  Servers:    hd-1, hd-2, hd-3

Provider: himovies
  Categories: recent-movies, trending-movies, trending-tv-shows
  Genres:     -
  Servers:    upcloud, vidcloud, akcloud

Provider: kisskh
  Categories: popular, ongoing, completed, movie, tv
  Genres:     -
  Servers:    kk

Provider: turkish
  Categories: series-list
  Genres:     -
  Servers:    tukipasti, engifuosi

Provider: viewasian
  Categories: most-popular-drama, recent-drama
  Genres:     -
  Servers:    vidmoly

Examples:
  mov-cli -s consumet.hianime "One Piece" -- --mode title --server hd-1 --page 1
```
