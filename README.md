<div align="center">

# consumet-mc

<sub>A mov-cli plugin for watching Movies,Shows and Anime based off consumet.ts.</sub>

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
mov-cli -s consumet.kisskh demon
```
