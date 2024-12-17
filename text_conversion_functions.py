# Text to seconds and seconds to text conversion for various screens. Also stats_update() function.

def convert_text_to_seconds(value):
    """
    Does the opposite of the convert_seconds_to_text function
    :param value: the text that needs to be converted into seconds.
    :return: Seconds.
    """

    value = value.split(":")
    seconds = int(value[-1])
    print("seconds: ", seconds)

    # I couldn't think of a better way to do this. I think I'm going to have a hard time with lesser languages.
    try:
        minutes = value[-2]
        if minutes[0] == "0":
            minutes = int(minutes[1]) * 60
        else:
            minutes = int(minutes) * 60
        print("minutes successful")
    except IndexError:
        minutes = 0
    print("minutes: ", minutes)

    try:
        hours = value[-3]
        if hours[0] == "0":
            hours = int(hours[1]) * 3600
        else:
            hours = int(hours) * 3600
        print("hours successful")
    except IndexError:
        hours = 0

    print("hours: ", hours)

    time_value = seconds + minutes + hours

    return time_value


def convert_seconds_to_text(value):
    """
    Converts seconds to text.
    For example:
        self.convert_seconds_to_text(60) --> return 1:00
        self.convert_seconds_to_text(3600) --> return 1:00:00
    :param value: the seconds that need to be converted
    :return: the text that gets converted
    """
    k = False
    hours = value // 3600
    minutes = (value // 60) % 60
    seconds = value % 60

    if hours:
        k = True

    # A pretty cool way to get text from time. Made it myself!
    # k is needed, so it doesn't display like :10:00.
    text = str(str(hours) * k + k * ":" + ((2 - len(str(minutes))) * "0") + str(minutes) + ":" +
               ((2 - len(str(seconds))) * "0") + str(seconds))

    return text


# TODO: make this function. It is unfinished.
def update_stats(index, data):
    i = -1
    new_stats = []
    with open("stats.txt", encoding="utf-8") as stats_file:
        old_stats = stats_file.readlines()
        while True:
            i += 1
            if index == i:
                new_stats.append(str(data) + "\n")
            else:
                try:
                    new_stats.append(old_stats[i])
                except IndexError:
                    break
