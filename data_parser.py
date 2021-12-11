#!/usr/bin/env python3
import copy
import math
import re
from sortedcontainers import SortedList

# Tools for handling OTF2 traces
eventLineParser = re.compile(r'^((?:ENTER)|(?:LEAVE))\s+(\d+)\s+(\d+)\s+(.*)$')
attrParsers = {
    'ENTER': r'(Region): "([^"]*)"',
    'LEAVE': r'(Region): "([^"]*)"'
}
addAttrLineParser = re.compile(r'^\s+ADDITIONAL ATTRIBUTES: (.*)$')
addAttrSplitter = re.compile(r'\), \(')
addAttrParser = re.compile(r'\(?"([^"]*)" <\d+>; [^;]*; ([^\)]*)')


# Helper function from https://stackoverflow.com/a/4836734/1058935 for
# human-friendly location name sorting
def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)

# adopted from https://github.com/hdc-arizona/traveler-integrated/blob/main/data_store/_otf2_functions.py
class DataParser:
    def __init__(self):
        self.sortedEventsByLocation = None
        self.primitives = None
        self.info = None
        self.intervals = None

    def processPrimitive(self, primitiveName):
        primitive = self.primitives.get(primitiveName, {'parents': [], 'children': []})
        updatedSources = False
        # if self.debugSources:
        #     primitive['sources'] = primitive.get('sources', [])
        #     if source is not None and source not in primitive['sources']:
        #         primitive['sources'].append(source)
        #         updatedSources = True
        if primitiveName in self.primitives:
            # Already existed
            if updatedSources:
                # tell the primitives diskcache that there was an update
                self.primitives[primitiveName] = primitive
            return (primitive, 0)
        primitiveChunks = primitiveName.split('$')
        primitive['name'] = primitiveChunks[0]
        if len(primitiveChunks) >= 3:
            primitive['line'] = primitiveChunks[-2]
            primitive['char'] = primitiveChunks[-1]
        self.primitives[primitiveName] = primitive
        return (primitive, 1)


    def processEvent(self, event):
        newR = seenR = 0

        if 'Region' in event:
            # Identify the primitive (and add to its counter)
            primitiveName = event['Region'].replace('::eval', '')
            event['Primitive'] = primitiveName
            del event['Region']
            primitive, newR = self.processPrimitive(primitiveName)
            seenR = 1 if newR == 0 else 0
            # if self.debugSources is True:
            #     if 'eventCount' not in primitive:
            #         primitive['eventCount'] = 0
            #     primitive['eventCount'] += 1
            self.primitives[primitiveName] = primitive
        # Add enter / leave events to per-location lists
        if event['Event'] == 'ENTER' or event['Event'] == 'LEAVE':
            if not event['Location'] in self.sortedEventsByLocation:
                # TODO: use BPlusTree instead of blist? For big enough runs, piling
                # all this up in memory could be a problem...
                self.sortedEventsByLocation[event['Location']] = SortedList()
            self.sortedEventsByLocation[event['Location']].add((event['Timestamp'], event))
        return (newR, seenR)

    def parseTraceData(self, file):
        # Temporary counters / lists for sorting
        numEvents = 0
        self.sortedEventsByLocation = {}
        self.primitives = {}
        self.info = {}
        print('Parsing OTF2 events (.=2500 events)')
        newR = seenR = 0
        currentEvent = None
        unsupportedSkippedLines = 0
        badAddAttrLines = 0
        min_time = math.inf
        max_time = 0

        with open(file, 'r') as file:
            for line in file:
                eventLineMatch = eventLineParser.match(line)
                addAttrLineMatch = addAttrLineParser.match(line)
                if currentEvent is None and eventLineMatch is None:
                    # This is a blank / header line
                    continue
                if eventLineMatch is not None:
                    # This is the beginning of a new event; process the previous one
                    if currentEvent is not None:
                        counts = self.processEvent(currentEvent)
                        # Log that we've processed another event
                        numEvents += 1
                        # if numEvents % 2500 == 0:
                        #     await log('.', end='')
                        # if numEvents % 100000 == 0:
                        #     await log('processed %i events' % numEvents)
                        # Add to primitive / guid counts
                        newR += counts[0]
                        seenR += counts[1]
                    currentEvent = {'Event': eventLineMatch.group(1),
                                    'Location': eventLineMatch.group(2),
                                    'Timestamp': int(eventLineMatch.group(3))}
                    min_time = min(min_time, currentEvent['Timestamp'])
                    max_time = max(max_time, currentEvent['Timestamp'])
                    attrs = eventLineMatch.group(4)
                    for attrMatch in re.finditer(attrParsers[currentEvent['Event']], attrs):
                        currentEvent[attrMatch.group(1)] = attrMatch.group(2)
                elif currentEvent is not None and addAttrLineMatch is not None:
                    # This line contains additional event attributes
                    attrList = addAttrSplitter.split(addAttrLineMatch.group(1))
                    for attrStr in attrList:
                        attr = addAttrParser.match(attrStr)
                        if attr is None:
                            badAddAttrLines += 1
                            print('\nWARNING: omitting data from bad ADDITIONAL ATTRIBUTES line:\n%s' % line)
                            continue
                        currentEvent[attr.group(1)] = attr.group(2) #pylint: disable=unsupported-assignment-operation
                else:
                    # This is a line that we aren't capturing (yet), e.g. MPI_SEND
                    unsupportedSkippedLines += 1
            # The last event will never have had a chance to be processed:
            if currentEvent is not None:
                counts = self.processEvent(currentEvent)
                newR += counts[0]
                seenR += counts[1]
            print('')
            print('Finished processing %i events' % numEvents)
            print('New primitives: %d, References to existing primitives: %d' % (newR, seenR))
            print('Additional attribute lines skipped: %d' % badAddAttrLines)
            print('Lines skipped because they are not yet supported: %d' % unsupportedSkippedLines)
            self.info['locationNames'] = natural_sort(self.sortedEventsByLocation.keys())
            self.info['domain'] = [min_time, max_time]
