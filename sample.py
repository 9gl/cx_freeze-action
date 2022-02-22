#!/usr/bin/env python3

import os
import time
import argparse


def main(args):
    """
    Rule:
    1. Only keep directory.
    2. Paths should have not less than 3 components.
    3. Path haven't been accessed in 30 days will be removed.
    4. Path have two last same components will be removed.

    `~/.fasd` file is where to store fasd information

    """
    allow_output = True
    if args.s == "true":
        allow_output = False

    frequent_used_dir = []
    fasd_file_path = os.path.expanduser('~/.fasd')
    current_time = time.time()

    remove_count = 0
    remain_count = 0

    with open(fasd_file_path, 'r') as fasd_file:
        if allow_output:
            print("### Reading from '~/.fasd'")

        for line in fasd_file:
            if len(line) == 0:
                continue

            keep_line = False
            parts = line.split("|")

            pathComponents = parts[0].split("/")

            # Rule

            if 'Pods' in pathComponents or 'pods' in pathComponents:
                remove_count += 1
                if allow_output:
                    print("### Remove " + parts[0], ", Reason: I don't wanna search in Pods")
                continue

            # Rule 1
            if not os.path.isdir(parts[0]):
                remove_count += 1
                if allow_output:
                    print("### Remove " + parts[0], ", Reason: 🤔 It's not a Dir")
                continue

            components_count = len(pathComponents)

            # Rule 2
            # Path Components should more than 3: ["", "Users", "username"]
            # and not too long 
            if not components_count > 3:
                remove_count += 1
                if allow_output:
                    print("### Remove " + parts[0], ", Reason: 💩 Path is way too short.", end="\n")
                continue

            if not components_count <= 12:
                remove_count += 1
                if allow_output:
                    print("### Remove " + parts[0], ", Reason: 😈 Path is way too long.", end="\n")
                continue

            # data structures: path|frequent_number|last_access_time
            # remove infrequent files
            # 30 day's second is 30 * 24 * 60 * 60 = 2592000

            # Rule 3
            time_offset = current_time - float(parts[2])
            frequent_number = float(parts[1])

            if time_offset < 2592000:
                keep_line = True
            elif frequent_number > 10:
                keep_line = True
            else:
                remove_count += 1
                if allow_output:
                    print("### Remove " + parts[0] + ", Reason: 🦄  Path not used in more than 30 days", end="\n")
                continue

            if pathComponents[components_count - 1].lower() == pathComponents[components_count - 2].lower():
                remove_count += 1
                if allow_output:
                    print("### Remove " + parts[0] + ", Reason: Path's last two parts are same, it's treated as a mistaken adding", end="\n")
                continue

            if keep_line:
                frequent_used_dir.append(line)

    # Sort lines
    frequent_used_dir = sorted(frequent_used_dir)
    unique_frequent_used_dir = []

    pre_line = None
    for line in frequent_used_dir:
        if pre_line is None:
            unique_frequent_used_dir.append(line)
        elif pre_line.lower() != line.lower():
            unique_frequent_used_dir.append(line)
        else:
            remove_count += 1
            if allow_output:
                print("Remove " + line + "Reason: 🙊 Duplicated", end="\n")
        pre_line = line

    with open(fasd_file_path, 'w') as fasd_file:
        if allow_output:
            print("### Writing to '~/.fasd'")
        content = ""
        for line in unique_frequent_used_dir:
            content += line
            remain_count += 1
        fasd_file.write(content)

    if allow_output:
        print("### Remove " + str(remove_count) + " lines")
        print("### Remain " + str(remain_count) + " lines")
    return remove_count


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Clean .fasd file')
    parser.add_argument('-s', help='Silent output')
    argvs = parser.parse_args()
    t = time.process_time()
    remove_count = main(argvs)
    elapsed_time = time.process_time() - t
    # print("$ Clean .fasd finished. Remove " + str(remove_count) + " lines, cost " + '%.5f' % elapsed_time + "s")
