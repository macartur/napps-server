#!/usr/bin/env python3.6
"""Recursively extract metadata from NApps repo."""
import json
import pprint
import tarfile

from pathlib import Path

WD = Path()
REPO = WD / 'repo'


def extract_napp_json(napp_path):
    """Print NApp metadata based on a .napp file.

    Args:
        napp_path (Path): Path to the napp file to be extracted.
        extra_comma (bool): If true, and extra comma will be printed after the
            'json', in order to enable the concatenation between multiple NApps
            metadata.
    """
    with tarfile.open(napp_path, 'r:xz') as napp:
        jsonfile = napp.extractfile('kytos.json').read().decode('utf-8')
        print(jsonfile)


def walk_on_repo(repo_path=REPO):
    """Walk on a NApps' repo tree and call the extract_napp_json function.

    Args:
        repo_path (Path): The path to the repository to be 'parsed'.
    """
    napps = repo_path.glob('**/*.napp')
    first = True
    for napp in napps:
        if first:
            first = False
            print('{"napps":{ ')
        else:
            print(',')
        print('"{}": '.format(napp))
        extract_napp_json(napp)
    print('}}')

if __name__ == '__main__':
    walk_on_repo()
