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

1. Then add the plugin to your mov-cli config.

```sh
mov-cli -e
```

```toml
[mov-cli.plugins]
consumet = "consumet-mc"
```

## Usage

```sh
Search for tv, movies, or anime by title, category, or genre

Usage:
  mov-cli -s consumet <query> -- [Options]

arguments:
  <query>         title, category, or genre

Options:
    --mode <mode>   Search mode: title (default), category, or genre
    --server        Video server to use for a specefic episode or movie
    --page          Search result page to grab (default 1)
    --sub_or_dub    **Anime Only** Episode type: any (default),sub, or dub


Examples:
  mov-cli -s consumet "tv" --  --mode category --sub_or_dub dub --server HD-1
```
