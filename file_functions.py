from os import path


def write_new_exercise_rest_time(rest_time, exercise):
    #  I'm sure there is a better way to do this
    new_info = list()
    with open(path.join("exercises", (exercise + ".txt")), "r", encoding='utf-8') as file:
        file_info = file.readlines()
        s_name, old_rest_time, *args = file_info
        new_info.append(s_name)
        new_info.append((str(rest_time) + '\n'))
        # I tried doing list comprehension, but it appended the actual generator (whatever that means).
        for x in args:
            new_info.append(x)
        print(new_info)
    with open(path.join("exercises", (exercise + ".txt")), "w", encoding='utf-8') as file:
        for i in new_info:
            file.write(str(i))
