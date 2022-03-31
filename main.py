import argparse
import os
import pathlib
import re

from tqdm import tqdm


def all_caps_to_lower(source, is_dir=None):
    _source = pathlib.Path(source)
    _destination = pathlib.Path(source)

    # If it's ALL CAPS, make it all lower
    if is_dir:
        name = _source.name
        if name == name.upper():
            name = name.lower()
        _destination = _source.with_name(name)
    else:
        stem = _source.stem
        if stem == stem.upper():
            stem = stem.lower()
        _destination = _source.with_stem(stem)

    return _destination


def make_exception(source):
    if source.parent.name == "onlyfans" and source.parent.parent.name == "onlyfans":
        return True

    return False


def final_strip(source, is_dir=None):
    _source = pathlib.Path(source)
    _destination = pathlib.Path(source)

    # Strip all dumb characters
    if is_dir:
        _destination = _source.with_name(_source.name.strip(' _-@*![]#'))
        _destination = _destination.with_name(_destination.name.rstrip('.'))
    else:
        _destination = _source.with_stem(_source.stem.strip(' _-@*![]#'))
        _destination = _destination.with_stem(_destination.stem.rstrip('.'))

    return _destination


def ws_to_underscore(source, is_dir=None):
    _source = pathlib.Path(source)
    _destination = pathlib.Path(source)

    if is_dir:
        us = _source.name
    else:
        us = _source.stem

    # Make all whitespace into underscores
    us = us.strip()
    us = us.replace(" ", "_")

    if is_dir:
        _destination = _source.with_name(us.strip('_'))
    else:
        _destination = _source.with_stem(us.strip('_'))

    return _destination


def delete_nonsense(source, is_dir=None):
    _source = pathlib.Path(source)
    _destination = pathlib.Path(source)

    if is_dir:
        us = _source.name
    else:
        us = _source.stem

    # Strip excess periods
    us = re.sub(r'[!@#$%*—•–’\'\[\]]', "", us)
    us = re.sub(r',', "_", us)
    us = re.sub(r'-_', "-", us)
    us = re.sub(r'_-', "-", us)
    us = re.sub('[-]{2,}', "-", us)

    if is_dir:
        _destination = _source.with_name(us)
    else:
        _destination = _source.with_stem(us)

    return _destination


def delete_excess_periods(source, is_dir=None):
    _source = pathlib.Path(source)
    _destination = pathlib.Path(source)

    if is_dir:
        us = _source.name
    else:
        us = _source.stem
    # Strip excess periods
    us = us.rstrip(".")
    us = re.sub('[.]{2,}', "", us)

    if is_dir:
        us = re.sub('(?!^)[.](?!$)', "", us)
        _destination = _source.with_name(us)
    else:
        _destination = _source.with_stem(us)

    return _destination


def main(args):
    cwd = os.getcwd()
    topdown = not args.recursive

    do_files = args.files_only or not args.dirs_only
    do_dirs = args.dirs_only or not args.files_only

    if do_files:
        print("Fixing files...")
    elif do_dirs:
        print("Gathering dirs...")

    _dirs_list = []
    for root, dirs, files in os.walk(cwd, topdown=topdown):
        _dirs_list.append(root)

        if do_files:
            print()
            print(root)
            for file in tqdm(files, desc="Files", total=len(files)):
                source_file = pathlib.Path(root, file)
                destination_file = ws_to_underscore(source_file, is_dir=False)
                destination_file = delete_excess_periods(destination_file, is_dir=False)
                destination_file = delete_nonsense(destination_file, is_dir=False)
                destination_file = final_strip(destination_file, is_dir=False)
                destination_file = all_caps_to_lower(destination_file, is_dir=False)

                # No Consecutive underscores
                # TODO: Move the double underscore removal to delete_nonsense()
                single_us_file = re.sub("[_]+", "_", destination_file.stem)
                destination_file = destination_file.with_stem(single_us_file)
                if args.dry_run and not destination_file.exists():
                    print(destination_file)
                elif not destination_file.exists():
                    print(destination_file)
                    source_file.replace(destination_file)
                elif source_file != destination_file:
                    print(f'Could not rename due to existing file:\n{source_file}')

        if not args.recursive:
            _dirs_list = [str(pathlib.Path(root, x)) for x in dirs]
            break

    if do_dirs:
        print("\nFixing dirs...\n")
        for _dir in tqdm(_dirs_list, desc="Directories", total=len(_dirs_list)):
            source = pathlib.Path(_dir)
            if make_exception(source):
                continue

            destination = ws_to_underscore(source, is_dir=True)
            destination = delete_excess_periods(destination, is_dir=True)
            destination = delete_nonsense(destination, is_dir=True)
            destination = all_caps_to_lower(destination, is_dir=True)

            # No Consecutive underscores
            single_us_dir = re.sub("[_]+", "_", destination.name)
            destination = destination.with_name(single_us_dir)

            if args.dry_run and not destination.exists():
                print(destination)
            elif not destination.exists():
                print(destination)
                os.rename(source, destination)
            elif source != destination:
                print(f'Could not rename due to existing directory:\n{source}')


# Entrance point
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This is a file and dir name fixer')

    parser.add_argument('-n', '--dry-run', action="store_true", default=False)
    parser.add_argument('-r', '--recursive', action="store_true", default=False)
    parser.add_argument('-f', '--files-only', action="store_true", default=False)
    parser.add_argument('-d', '--dirs-only', action="store_true", default=False)
    args = parser.parse_args()

    main(args)
