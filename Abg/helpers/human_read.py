def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["Sec.", "Min.", "Hour", "Day", "Week", "Month", "Year"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    for i in range(len(time_list)):
        time_list[i] = str(time_list[i]) + time_suffix_list[i]
    if len(time_list) == 4:
        ping_time += f"{time_list.pop()}, "
    time_list.reverse()
    ping_time += ":".join(time_list)
    return ping_time


async def convert_seconds_to_minutes(seconds: int):
    seconds = int(seconds)
    seconds %= 24 * 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)


SIZE_UNITS = ["B", "KB", "MB", "GB", "TB", "PB"]


def get_readable_file_size(size_in_bytes) -> str:
    if size_in_bytes is None:
        return "0B"
    index = 0
    while size_in_bytes >= 1024:
        size_in_bytes /= 1024
        index += 1
    try:
        return f"{round(size_in_bytes, 2)}{SIZE_UNITS[index]}"
    except IndexError:
        return "File too large"


def get_readable_bitrate(bitrate_kbps):
    if bitrate_kbps > 10000:
        bitrate = str(round(bitrate_kbps / 1000, 2)) + " " + "mbps"
    else:
        bitrate = str(round(bitrate_kbps, 2)) + " " + "kbps"

    return bitrate
