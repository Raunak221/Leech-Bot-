from tobrot.get_cfg import get_config


class Config:
    # get a token from @BotFather
    TG_BOT_TOKEN = get_config("TG_BOT_TOKEN", should_prompt=True)
    # The Telegram API things
    APP_ID = int(get_config("APP_ID", should_prompt=True))
    API_HASH = get_config("API_HASH", should_prompt=True)
    # Get these values from my.telegram.org
    # array to store the channel ID who are authorized to use the bot
    AUTH_CHANNEL = set(
        int(x) for x in get_config("AUTH_CHANNEL", should_prompt=True).split()
    )
    AUTH_CHANNEL = list(AUTH_CHANNEL)
    # the download location, where the HTTP Server runs
    DOWNLOAD_LOCATION = get_config("DOWNLOAD_LOCATION", "./DOWNLOADS")
    # Telegram maximum file upload size
    MAX_FILE_SIZE = int(get_config("MAX_FILE_SIZE", 50000000))
    TG_MAX_FILE_SIZE = int(get_config("TG_MAX_FILE_SIZE", 2097152000))
    FREE_USER_MAX_FILE_SIZE = int(get_config("FREE_USER_MAX_FILE_SIZE", 50000000))
    # chunk size that should be used with requests
    CHUNK_SIZE = int(get_config("CHUNK_SIZE", 128))
    # default thumbnail to be used in the videos
    DEF_THUMB_NAIL_VID_S = get_config(
        "DEF_THUMB_NAIL_VID_S", "https://telegra.ph/file/8b973b270f4f380a427b1.png"
    )
    # maximum message length in Telegram
    MAX_MESSAGE_LENGTH = int(get_config("MAX_MESSAGE_LENGTH", 4096))
    # set timeout for subprocess
    PROCESS_MAX_TIMEOUT = int(get_config("PROCESS_MAX_TIMEOUT", 3600))
    #
    ARIA_TWO_STARTED_PORT = int(get_config("ARIA_TWO_STARTED_PORT", 6800))
    EDIT_SLEEP_TIME_OUT = int(get_config("EDIT_SLEEP_TIME_OUT", 1))
    MAX_TIME_TO_WAIT_FOR_TORRENTS_TO_START = int(
        get_config("MAX_TIME_TO_WAIT_FOR_TORRENTS_TO_START", 600)
    )
    MAX_TG_SPLIT_FILE_SIZE = int(get_config("MAX_TG_SPLIT_FILE_SIZE", 1900000000))
    # add config vars for the display progress
    FINISHED_PROGRESS_STR = get_config("FINISHED_PROGRESS_STR", "█")
    UN_FINISHED_PROGRESS_STR = get_config("UN_FINISHED_PROGRESS_STR", "░")
    # add offensive API
    TG_OFFENSIVE_API = get_config("TG_OFFENSIVE_API", None)
    # URL for the rclone configuration
    R_CLONE_CONF_URI = get_config("R_CLONE_CONF_URI", None)
    # Destination folder for the rclone
    R_CLONE_DEST = get_config("R_CLONE_DEST", "/PublicLeech")
    # because, https://t.me/c/1494623325/5603
    SHOULD_USE_BUTTONS = get_config("SHOULD_USE_BUTTONS", False)
    #
    LOG_FILE_ZZGEVC = get_config("LOG_FILE_ZZGEVC", "PublicLeech.log")
    #
    SP_LIT_ALGO_RITH_M = get_config("SP_LIT_ALGO_RITH_M", "hjs")
    #
    DIS_ABLE_ST_GFC_COMMAND_I = get_config("DIS_ABLE_ST_GFC_COMMAND_I", False)
    # array to store the users who will have control (permissions)
    # in the bot
    SUDO_USERS = set(
        int(x) for x in get_config("SUDO_USERS", should_prompt=True).split()
    )
    SUDO_USERS = list(SUDO_USERS)