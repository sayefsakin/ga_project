#!/usr/bin/env python3
import math
import re
import subprocess
import sys
from data_parser import DataParser


class KDNode:
    def __init__(self, start_loc, end_loc, st_time, en_time, lft=None, rt=None):
        self.location = (start_loc, end_loc)  # this is location index
        self.timestamp = (st_time, en_time)
        self.left = lft
        self.right = rt

    def getTimeWindow(self):
        return self.timestamp[1] - self.timestamp[0]

    def isLeaf(self):
        return self.left is None and self.right is None

    def isOverlap(self, sl, el, st, et):
        return sl <= self.location[1] and el >= self.location[0] and st <= self.timestamp[1] and et >= self.timestamp[0]


# equal time will go right, equal location will go down
class KDStore:
    def __init__(self):
        self.parsed_data = DataParser()
        self.parsed_data.parseTraceData('data/converted')
        self.kd_tree = self.buildKDTree()
        # self.parsed_data.combineIntervals()
        # s = 67063027

    # ignore the cases where en_index < st_index
    def findIntervalsInLocation(self, location, st_time, en_time):
        st_index = self.parsed_data.sortedEventsByLocation[location].bisect((st_time,))
        en_index = self.parsed_data.sortedEventsByLocation[location].bisect((en_time,))
        if st_index == len(self.parsed_data.sortedEventsByLocation[location]):
            st_index = None
        elif self.parsed_data.sortedEventsByLocation[location][st_index][1]['Event'] == 'LEAVE':
            st_index -= 1
        if en_index == len(self.parsed_data.sortedEventsByLocation[location]):
            en_index = None
        elif self.parsed_data.sortedEventsByLocation[location][en_index][1]['Event'] == 'ENTER':  # remove the trailing enter event
            en_index -= 1
        return (st_index, en_index)

    def buildKDTree(self):
        return self.insertIntoKDTree(0,
                                     len(self.parsed_data.info['locationNames'])-1,
                                     self.parsed_data.info['domain'][0],
                                     self.parsed_data.info['domain'][1], 0)

    def insertIntoKDTree(self, start_loc_index, end_loc_index, st_time, en_time, depth):
        if start_loc_index > end_loc_index:
            return None
        start_loc = self.parsed_data.info['locationNames'][start_loc_index]
        end_loc = self.parsed_data.info['locationNames'][end_loc_index]
        if start_loc == end_loc:
            st, en = self.findIntervalsInLocation(start_loc, st_time, en_time)
            if st is None or en is None:
                return None
            if st + 1 == en:  # this belongs to a single interval
                st_time = max(self.parsed_data.sortedEventsByLocation[start_loc][st][1]['Timestamp'], st_time)
                en_time = min(self.parsed_data.sortedEventsByLocation[start_loc][en][1]['Timestamp'], en_time)
                return KDNode(start_loc_index, end_loc_index, st_time, en_time)
            elif en <= st:
                return None
        if (depth % 2) == 0:  # vertical
            if start_loc == end_loc:
                st, en = self.findIntervalsInLocation(start_loc, st_time, en_time)
                if st is not None and en is not None:
                    st_time = max(self.parsed_data.sortedEventsByLocation[start_loc][st][1]['Timestamp'], st_time)
                    en_time = min(self.parsed_data.sortedEventsByLocation[start_loc][en][1]['Timestamp'], en_time)
            mid = math.floor((st_time + en_time) / 2)
            left = self.insertIntoKDTree(start_loc_index, end_loc_index, st_time, mid, depth + 1)
            right = self.insertIntoKDTree(start_loc_index, end_loc_index, mid+1, en_time, depth + 1)
        else:
            mid = math.floor((start_loc_index + end_loc_index) / 2)
            left = self.insertIntoKDTree(start_loc_index, mid, st_time, en_time, depth + 1)
            right = self.insertIntoKDTree(mid+1, end_loc_index, st_time, en_time, depth + 1)
        return KDNode(start_loc_index, end_loc_index, st_time, en_time, left, right)

    def queryInRange(self, start_loc_index, end_loc_index, st_time, en_time, figure_width):
        data = {}
        for lc in range(start_loc_index, end_loc_index + 1):
            data[lc] = list()
        pixel_window = (en_time - st_time) / figure_width

        def searchInKDTree(kd_node, sl_index, el_index, st, et):
            if kd_node.getTimeWindow() <= pixel_window:
                if kd_node.isLeaf() is False:
                    # if (kd_node.timestamp[1] - kd_node.timestamp[0]) / (et - st) > 0.1:
                    for loc in range(kd_node.location[0], kd_node.location[1] + 1):
                        data[loc].append((kd_node.timestamp[0], kd_node.timestamp[0]+1))
                return
            if kd_node.isLeaf():
                for loc in range(kd_node.location[0], kd_node.location[1] + 1):
                    data[loc].append((kd_node.timestamp[0], kd_node.timestamp[1]))
                return
            if kd_node.left and kd_node.left.isOverlap(sl_index, el_index, st, et):
                searchInKDTree(kd_node.left, sl_index, el_index, st, et)
            if kd_node.right and kd_node.right.isOverlap(sl_index, el_index, st, et):
                searchInKDTree(kd_node.right, sl_index, el_index, st, et)

        searchInKDTree(self.kd_tree, start_loc_index, end_loc_index, st_time, en_time)
        return data

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
    path = 'data/cannon/OTF2_archive/APEX.otf2'
    if len(sys.argv) > 1:
        path = sys.argv[1]

    print('parsing OTF2 file in data directory', path)

    processOtf2(FakeFile(path))

    # kd_store = KDStore()
    # print('hello')



