# game-notifier

- Get notifications on wanted Steam games being on sale and this weeks free games on EpicGames.
- Python script to run in the background that checks its sources on a given interval and sends notifications via [ntfy](https://ntfy.sh)

## instructions

### requirements

- only tested on Linux
- [Pixi](https://pixi.sh/latest/)
- a ntfy [topic](https://docs.ntfy.sh) (note: those are usually public and I have not implemented auth for topics yet)

### getting started

see below first in case your setup differs from linux standards

- clone this repo
- copy `.env.example` to `.env` and edit the values
- set up databases (and systemd service): `pixi run start --install --config-dir /path/to/configuration --script-dir /path/to/script/main.py`
- view with `journalctl --user -u game-notifier@game-notifier -f`
- remove service with `pixi run rmservice`

side-note: I'm aware this isn't very neat and every help in fixing that is appreciated :]

### development

- enter dev environment: `pixi shell`

### usage on NixOS

help wanted: this is impure and not a proper flake

- edit and include `game-notifier-service.nix` in your configuration
- when setting up the database, pass `--no-service`
- rebuild your configuration and enjoy

monitor with: `journalctl -u gameNotifierService.service -f`

## TODO

- allow for configuration changes (without relying on re-installation)

## motivation

- the upcoming Python exam
- my partner wanting to be notified about Sims 3 being on sale (let's hope that'll happen one day)
- me being too lazy to check EpicGames every week
