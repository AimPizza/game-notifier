# game-notifier

- Get notifications on wanted Steam games being on sale and this weeks free games on EpicGames.
- Python script to run in the background that checks its sources on a given interval and sends notifications via [ntfy](https://ntfy.sh)

## instructions

**(probably) required:**

- only tested on Linux
- [Pixi](https://pixi.sh/latest/)
- a ntfy [topic](https://docs.ntfy.sh) (note: those are usually public and I have not implemented auth for topics yet)

**getting started:**

- clone this repo
- edit `.env.example`, move it to `.env`
- set up databases: `pixi run start init /path/to/working-directory`
- run the script: `pixi run start /path/to/working-directory/.env`
  - make sure this path includes the `.env` file

side-note: I'm aware this isn't very neat and every help in fixing that is appreciated :]

## motivation

- the upcoming Python exam
- my partner wanting to be notified about Sims 3 being on sale (let's hope that'll happen one day)
- me being too lazy to check EpicGames every week
