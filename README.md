# Twitch Highlight Saver

This script queries a given Twitch channel's highlights and identifies highlights at risk of deletion based on view counts. It exports the links of these at-risk highlights to a `.txt` file and a `.json` file with all the information about the channel and its highlights that are at risk. Additionally, it can download the at-risk highlights using `youtube-dl`.

## Prerequisites

- Python 3.x
- `requests` library (install using `pip install requests`)
- `youtube-dl` (install using `pip install youtube-dl` or follow the instructions [here](https://github.com/ytdl-org/youtube-dl#installation))

## Setup

1. Clone the repository:
    ```sh
    git clone <repository_url>
    cd Twitch-Highlight-Saver
    ```

2. Create a `config.json` file in the root directory with your Twitch API credentials:
    ```json
    {
        "client_id": "your_client_id",
        "client_secret": "your_client_secret"
    }
    ```

3. Ensure the `config.json` file is added to `.gitignore` to avoid committing sensitive information.

## Usage

1. Run the script from the command line with the mode and Twitch channel name as arguments:
    ```sh
    python main.py <mode> <channel_name>
    ```

    - `<mode>`: The mode of operation. Can be `check` or `backup`.
    - `<channel_name>`: The name of the Twitch channel.

2. The script will generate two files in the root directory if the mode is `check`:
    - `at_risk_highlights_<channel_name>.txt`: Contains the links of at-risk highlights.
    - `at_risk_highlights_<channel_name>.json`: Contains detailed information about the at-risk highlights.

3. If the mode is `backup`, the script will download the at-risk highlights into a folder named after the Twitch channel.

## Example

To check for at-risk highlights:
```sh
python main.py check sharkhat87
```

To backup at-risk highlights:
```sh
python main.py backup sharkhat87
```

This will generate:
- `at_risk_highlights_sharkhat87.txt`
- `at_risk_highlights_sharkhat87.json`
- A folder named `sharkhat87` containing the downloaded highlights (if in `backup` mode).