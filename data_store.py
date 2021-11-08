#!/usr/bin/env python3
import subprocess
import sys

class Intervals:
    def __init__(self, st, en, loc):
        self.start_time = st
        self.end_time = en
        self.location = loc

class KDStore:
    pass

class FakeFile: #pylint: disable=R0903
    def __init__(self, name):
        self.name = name

    def __iter__(self):
        # otfPipe = subprocess.Popen(['otf2-print', self.name], stdout=subprocess.PIPE)
        otfPipe = subprocess.Popen(['otf2-print', self.name], stdout=subprocess.PIPE)
        for bytesChunk in otfPipe.stdout:
            yield bytesChunk.decode()
            otfPipe.stdout.flush()


def processOtf2(file):
    count = 0
    with open('data/converted', 'w') as f:
        for line in file:
            f.writelines(line)
            count += 1
            if count % 2500 == 0:
                print('.', end='')
            if count % 100000 == 0:
                print('processed %i intervals' % count)


if __name__ == "__main__":
    print('hello')
    path = 'data/cannon/OTF2_archive/APEX.otf2'
    processOtf2(FakeFile(path))


