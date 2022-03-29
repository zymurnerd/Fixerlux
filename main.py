import argparse
import os
import pathlib
import re

from tqdm import tqdm


def final_strip(source):
    _source = pathlib.Path(source)
    _destination = pathlib.Path(source)

    # Strip all dumb characters
    _destination = _source.with_stem(_source.stem.strip(' _-@*![]#'))
    _destination = _destination.with_stem(_destination.stem.rstrip('.'))

    return _destination


def ws_to_underscore(source):
    _source = pathlib.Path(source)
    _destination = pathlib.Path(source)

    # Make all whitespace into underscores
    us = _source.stem.strip()
    us = us.replace(" ", "_")
    _destination = _source.with_stem(us.strip('_'))

    return _destination


def delete_nonsense(source):
    _source = pathlib.Path(source)
    _destination = pathlib.Path(source)

    # Strip excess periods
    us = re.sub(r'[!@#$%*•’\'\[\]]', "", _source.stem)
    us = re.sub(r'-_', "-", us)
    us = re.sub(r'_-', "-", us)
    us = re.sub('[-]{2,}', "-", us)
    _destination = _source.with_stem(us)

    return _destination


def delete_excess_periods(source):
    _source = pathlib.Path(source)
    _destination = pathlib.Path(source)

    # Strip excess periods
    us = _source.stem.rstrip(".")
    us = re.sub('[.]{2,}', "", us)
    _destination = _source.with_stem(us)

    return _destination


def main(args):
    cwd = os.getcwd()
    topdown = not args.recursive

    print("Fixing files...")
    _dirs_list = []
    for root, dirs, files in os.walk(cwd, topdown=topdown):
        print()
        print(root)
        _dirs_list.append(root)
        if not args.recursive:
            _dirs_list = [str(pathlib.Path(root, x)) for x in dirs]
        for file in tqdm(files, desc="Files", total=len(files)):
            source_file = pathlib.Path(root, file)
            destination_file = ws_to_underscore(source_file)
            destination_file = delete_excess_periods(destination_file)
            destination_file = delete_nonsense(destination_file)
            destination_file = final_strip(destination_file)

            # No Consecutive underscores
            single_us_file = re.sub("[_]+", "_", destination_file.stem)
            destination_file = destination_file.with_stem(single_us_file)
            if args.dry_run and not destination_file.exists():
                print(destination_file)
            elif not destination_file.exists():
                source_file.replace(destination_file)

        if not args.recursive:
            break

    print("\nFixing dirs...\n")
    for dir in tqdm(_dirs_list, desc="Directories", total=len(_dirs_list)):
        source = pathlib.Path(dir)
        destination = ws_to_underscore(source)
        destination = delete_nonsense(destination)

        # No Consecutive underscores
        single_us_dir = re.sub("[_]+", "_", destination.stem)
        destination = destination.with_stem(single_us_dir)

        if args.dry_run and not destination.exists():
            print(destination)
        elif not destination.exists():
            os.rename(source, destination)


# Entrance point
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This is a file and dir name fixer')

    parser.add_argument('-n', '--dry-run', action="store_true", default=False)
    parser.add_argument('-r', '--recursive', action="store_true", default=False)
    parser.add_argument('-f', '--files-only', action="store_true", default=False)
    parser.add_argument('-d', '--dirs-only', action="store_true", default=False)
    args = parser.parse_args()

    main(args)
