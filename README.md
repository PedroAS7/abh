<img src="https://www.peteras17.me/static/images/abh.webp" style="width:100px"/>

# abh, the Aurora Borealis hunter

Welcome to the repository of the *abh* bot. It is a bot for [Telegram](https://telegram.org/) that informs you or the
groups it is added to about solar events that lead to [Aurora Borealis](https://www.swpc.noaa.gov/phenomena/aurora).

This bot is not only lightweight and fast, but it can handle multiple information scraping endpoints, and is able to handle interactions and events for different
users and groups.

It is fully written in Python, and is compatible with [Python >= 3.9](https://www.python.org/downloads/release/python-390/).

## Default endpoints scraped

By default - that is, when running the source code as-is -, this bot scrapes endpoints from two different websites:

- The USA's [National Oceanic and Atmospheric Administration](https://www.noaa.gov/)
- Germany's [GFZ German Research Centre for Geosciences](https://www.gfz-potsdam.de/)

## Running your own instance

> [!CAUTION]
> The `data` folder contains not only the bot's configuration file, but also custom settings for user and groups, as
> well as historical scraping data from previous scrapes. Deleting this folder will result in the bot running as if it
> were the first time you were running it.

First of all, you'll need a Telegram bot token. Please refer to [Telegram's Bots FAQ](https://core.telegram.org/bots/faq#how-do-i-create-a-bot)
to learn how to create one.

### Creating a configuration file

When starting the bot, it will check whether a configuration file is present in the `data` folder or not.
The configuration file name is `cfg.json`.
If the file doesn't exist, an error message will show up on the terminal:

```
Traceback (most recent call last):
File ".../abh/src/app.py", line 241, in run
    cfg = Config.read()
File ".../abh/src/config.py", line 133, in read
    raise ValueError("Configuration file does not exist")
ValueError: Configuration file does not exist
```

The configuration file is a JSON file with the following format:
```json
{
  "token": "<bot token>",
  "debug": false
}
```

If everything is set up correctly, you'll see the following message on the terminal:

```
ID:                 <bot @ on Telegram>
Name:               <full bot name>
Can join groups:    Yes
Can read all msg:   Yes
Bot is ready to get Telegram updates
```

## Licenses

This source code uses [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0). You will find separate
`LICENSE` files for licensed dependencies.
    