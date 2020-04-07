""" File parser for CPT'S MODUL.txt file using a state machine pattern. """

from abc import ABC, abstractmethod
from collections import namedtuple
from enum import Enum
import re
import pandas as pd
import boto3
import os


class State(Enum):
    Unknown = 0
    Beginning = 1
    RegularModifier = 2
    PhysicalModifier = 3
    LevelOneModifier = 4
    CategoryTwoModifier = 5
    LevelTwoModifier = 6
    # ParsingModifier = 7
    # ParsingPhysicalModifier = 8
    End = 8


class Event(Enum):
    Start = 0
    Blank = 1
    Text = 2
    Modifier = 3
    AppendixA = 4
    AnesthesiaPhysicalStatus = 5
    CPTLevelIModifiers = 6
    CategoryIIModifiers = 7
    LevelIIModifiers = 8


class ModifierType(Enum):
    Regular = 'regular'
    Physical = 'physical'
    LevelOne = 'level_one'
    CategoryTwo = 'category_two'
    LevelTwo = 'level_two'


Context = namedtuple('Context', 'state event data')


class FileParser:
    # pylint: disable=line-too-long,bad-whitespace
    TRANSITION_TABLE = [
        # Start           Blank                      Text                       Modifier                   AppendixA              AnesthesiaPhysicalStatus  CPTLevelIModifiers      CategoryIIModifiers       LevelIIModifiers
        [State.Unknown, State.Unknown, State.Unknown, State.Unknown, State.Unknown, State.Unknown, State.Unknown,
         State.Unknown, State.Unknown],  # Unknown
        [State.Beginning, State.Beginning, State.Beginning, State.Unknown, State.RegularModifier, State.Unknown,
         State.Unknown, State.Unknown, State.Unknown],  # Beginning
        [State.Unknown, State.RegularModifier, State.RegularModifier, State.RegularModifier, State.Unknown,
         State.PhysicalModifier, State.Unknown, State.Unknown, State.Unknown],  # RegularModifier
        [State.Unknown, State.PhysicalModifier, State.PhysicalModifier, State.PhysicalModifier, State.Unknown,
         State.Unknown, State.LevelOneModifier, State.Unknown, State.Unknown],  # PhysicalModifier
        [State.Unknown, State.LevelOneModifier, State.LevelOneModifier, State.LevelOneModifier, State.Unknown,
         State.Unknown, State.Unknown, State.CategoryTwoModifier, State.Unknown],  # LevelOneModifier
        [State.Unknown, State.CategoryTwoModifier, State.CategoryTwoModifier, State.CategoryTwoModifier, State.Unknown,
         State.Unknown, State.Unknown, State.Unknown, State.LevelTwoModifier],  # CategoryTwoModifier
        [State.Unknown, State.LevelTwoModifier, State.LevelTwoModifier, State.LevelTwoModifier, State.Unknown,
         State.Unknown, State.Unknown, State.Unknown, State.Unknown],  # LevelTwoModifier
    ]

    def __init__(self):
        self._modifiers = {
            ModifierType.Regular: {},
            ModifierType.Physical: {},
            ModifierType.LevelOne: {},
            ModifierType.CategoryTwo: {},
            ModifierType.LevelTwo: {},
        }
        self._state_processors = [
            AppendixAProcessor(self),
            RegularModifierProcessor(self),
            PhysicalModifierProcessor(self),
            LevelOneModifierProcessor(self),
            CategoryTwoModifier(self),
            LevelTwoModifierProcessor(self)
        ]

    def add_modifier(self, modifier_type: ModifierType, code: str, description: str):
        self._modifiers[modifier_type][code] = description

    def parse(self, input_filename: str, output_filename: str) -> dict:
        lines = self._read_file(input_filename)

        self._parse_file(lines)

        self._write_data(output_filename, self._modifiers)

    @classmethod
    def _read_file(cls, input_filename):
        with open(input_filename) as file:
            return file.readlines()

    def _parse_file(self, lines):
        context = Context(state=State.Beginning, event=Event.Start, data='')

        for line in lines:
            context = self._process_event(context, line.strip())

    @classmethod
    def _write_data(cls, output_filename, modifiers):
        dataframes = []
        i = 0
        while i < 5:
            for l in modifiers:
                d = pd.DataFrame(list(modifiers[l].items()), columns=['mod_code', 'mod_description'], index=None)
                d['mod_type'] = str(list(modifiers.keys())[i]).split('.')[1]
                dataframes.append(d)
                i = i + 1
        df_merged = pd.concat(dataframes, ignore_index=True)
        df_merged.to_csv('modifiers.csv', sep='\t')

        s3 = boto3.client('s3')

        try:
            s3.upload_file('modifiers.csv', 'ama-hsg-datalabs-datalake-ingestion-sandbox', 'modifiers.csv')
            return True
        except FileNotFoundError:
            print("The file was not found")
            return False
        pass

    def _process_event(self, context, line):
        state = self.TRANSITION_TABLE[context.state.value][context.event.value]

        _, event, data = self._state_processors[state.value - 1].process_line(context, line)

        return Context(state=state, event=event, data=data)


class StateProcessor(ABC):
    def __init__(self, parser: FileParser):
        self._parser = parser

    @abstractmethod
    def process_line(self, context: Context, line: str) -> Context:
        pass


class AppendixAProcessor(StateProcessor):
    def process_line(self, context, line):
        event = Event.Start
        data = ''

        if line == 'Appendix A':
            event = Event.AppendixA

        return Context(state=None, event=event, data=data)


class RegularModifierProcessor(StateProcessor):
    def process_line(self, context, line):
        event = context.event
        data = context.data
        match = re.match('[1-9][0-9] ..*', line)

        if line == 'Anesthesia Physical Status':
            event = Event.AnesthesiaPhysicalStatus
            data = ''

        elif context.event != Event.Modifier and match:
            event = Event.Modifier
            data = data + ' ' + line

        elif context.event == Event.Modifier and line != '':
            data = data + ' ' + line

        elif context.event == Event.Modifier and line == '':
            event = Event.Blank
            match = data.strip()
            self._process_match(match)
            data = ''
        elif line == '':
            event = Event.Blank

        else:
            event = Event.Text

        return Context(state=None, event=event, data=data)

    def _process_match(self, match):
        code, description = match.split(' ', 1)
        self._parser.add_modifier(ModifierType.Regular, code, description)


class PhysicalModifierProcessor(StateProcessor):
    def process_line(self, context, line):

        data = context.data
        event = Event.Modifier
        match = re.match('.*(P[0-9]):(.*)', line)

        if line == 'CPT Level I Modifiers':
            event = Event.CPTLevelIModifiers

        elif line == '':
            event = Event.Blank

        elif match:
            self._process_match(match)

        elif line != '':
            event = Event.Text

        elif line == '':
            event = Event.Blank

        return Context(state=None, event=event, data=data)

    def _process_match(self, match):
        code = match.group(1)
        description = match.group(2)
        self._parser.add_modifier(ModifierType.Physical, code, description)


class LevelOneModifierProcessor(StateProcessor):
    def process_line(self, context, line):

        event = context.event
        data = context.data
        match = re.match('[1-9][0-9] ..*', line)

        if line == 'Category II Modifiers':
            event = Event.CategoryIIModifiers
            data = ''

        elif context.event != Event.Modifier and match:
            event = Event.Modifier
            data = data + ' ' + line

        elif context.event == Event.Modifier and line != '':
            data = data + ' ' + line

        elif context.event == Event.Modifier and line == '':
            event = Event.Blank
            self._process_match(data.strip())
            data = ''
        elif line != '':
            event = Event.Text

        elif line == '':
            event = Event.Blank

        return Context(state=None, event=event, data=data)

    def _process_match(self, code_description_line):
        code, description = code_description_line.split(' ', 1)
        self._parser.add_modifier(ModifierType.LevelOne, code, description)


class CategoryTwoModifier(StateProcessor):
    def process_line(self, context, line):

        event = context.event
        data = context.data
        match = re.match('[1-9][A-Z] ..*', line)

        if line == 'Level II (HCPCS/National) Modifiers':
            event = Event.LevelIIModifiers
            data = ''

        elif context.event != Event.Modifier and match:
            event = Event.Modifier
            data = data + ' ' + line

        elif context.event == Event.Modifier and line != '':
            data = data + ' ' + line

        elif context.event == Event.Modifier and line == '':
            event = Event.Blank
            self._process_match(data.strip())
            data = ''
        elif line != '':
            event = Event.Text

        elif line == '':
            event = Event.Blank

        return Context(state=None, event=event, data=data)

    def _process_match(self, code_description_line):
        code, description = code_description_line.split(' ', 1)
        self._parser.add_modifier(ModifierType.CategoryTwo, code, description)


class LevelTwoModifierProcessor(StateProcessor):
    def process_line(self, context, line):

        data = context.data
        event = Event.Modifier
        match = re.match('([A-Z][0-9A-Z])(.*)', line)

        if line == '':
            event = Event.Blank

        elif match:
            self._process_match(match)

        else:
            event = Event.Text

        return Context(state=None, event=event, data=data)

    def _process_match(self, match):
        code = match.group(1)
        description = match.group(2)
        self._parser.add_modifier(ModifierType.LevelTwo, code, description)


def main():
    test_object = FileParser()
    s3 = boto3.client('s3')
    s3.download_file('ama-hsg-datalabs-datalake-ingestion-sandbox', 'AMA/CPT/20200131/standard/MODUL.txt', 'modul1.txt')
    test_object.parse('modul1.txt', "modul.csv")
    os.remove("modul1.txt")


if __name__ == "__main__":
    main()
