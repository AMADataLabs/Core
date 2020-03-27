""" File parser for CPT'S MODUL.txt file using a state machine pattern. """

from abc import ABC, abstractmethod
from collections import namedtuple
from enum import Enum
import re


class State(Enum):
    Unknown = 0
    Beginning = 1
    RegularModifier = 2
    PhysicalModifier = 3
    LevelOneModifier = 4
    CategoryTwoModifier = 5
    LevelTwoModifier = 6
    ParsingModifier = 7
    ParsingPhysicalModifier = 8
    End = 9


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


class FileParser():
    # pylint: disable=line-too-long,bad-whitespace
    TRANSITION_TABLE = [
        # Start           Blank                      Text                       Modifier                   AppendixA              AnesthesiaPhysicalStatus  CPTLevelIModifiers      CategoryIIModifiers       LevelIIModifiers
        [State.Unknown,   State.Unknown,             State.Unknown,             State.Unknown,             State.Unknown,         State.Unknown,            State.Unknown,          State.Unknown,             State.Unknown],           # Unknown
        [State.Beginning, State.Beginning,           State.Beginning,           State.Unknown,             State.RegularModifier, State.Unknown,            State.Unknown,          State.Unknown,             State.Unknown],           # Beginning
        [State.Unknown,   State.RegularModifier,     State.RegularModifier,     State.RegularModifier,     State.Unknown,         State.PhysicalModifier,   State.Unknown,          State.Unknown,             State.Unknown],           # RegularModifier
        [State.Unknown,   State.PhysicalModifier,    State.PhysicalModifier,    State.PhysicalModifier,    State.Unknown,         State.Unknown,            State.LevelOneModifier, State.Unknown,             State.Unknown],           # PhysicalModifier
        [State.Unknown,   State.LevelOneModifier,    State.LevelOneModifier,    State.LevelOneModifier,    State.Unknown,         State.Unknown,            State.Unknown,          State.CategoryTwoModifier, State.Unknown],           # LevelOneModifier
        [State.Unknown,   State.CategoryTwoModifier, State.CategoryTwoModifier, State.CategoryTwoModifier, State.Unknown,         State.Unknown,            State.Unknown,          State.Unknown,             State.LevelTwoModifier],  # CategoryTwoModifier
        [State.Unknown,   State.LevelTwoModifier,    State.LevelTwoModifier,    State.LevelTwoModifier,    State.Unknown,         State.Unknown,            State.Unknown,          State.Unknown,             State.Unknown],           # LevelTwoModifier
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
            # ...
        ]

    def add_modifier(self, modifier_type: ModifierType, code: str, description: str):
        self._modifiers[modifier_type][code] = description

    def parse(self, input_filename: str, output_filename: str) -> dict:
        lines = self._read_file(input_filename)

        self._parse_file(lines)

        self._write_data(output_filename)

    @classmethod
    def _read_file(cls, input_filename):
        with open(input_filename) as file:
            return file.readlines()

    def _parse_file(self, lines):
        context = Context(state=State.Beginning, event=Event.Start, data={})

        for line in lines:
            context = self._process_event(context, line.strip())

    @classmethod
    def _write_data(cls, output_filename):
        # TODO: convert self._modifiers dict to Pandas DataFrame or something
        #       and write data as CSV or push to DB
        pass

    def _process_event(self, context, line):
        state = self.TRANSITION_TABLE[context.state.value][context.event.value]

        _, event, data = self._state_processors[state.value].process_line(context, line)

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
        data = {}

        if line == 'Appendix A':
            event = Event.AppendixA

        return Context(state=None, event=event, data=data)


class RegularModifierProcessor(StateProcessor):
    def process_line(self, context, line):
        event = Event.Modifier
        data = {}
        match = re.match('[1-9][0-9] ..*', line)

        if line == 'Anesthesia Physical Status':
            event = Event.AnesthesiaPhysicalStatus
        elif line == '':
            event = Event.Blank
        elif match:
            self._process_match(match)

        return Context(state=None, event=event, data=data)

    def _process_match(self, match):
        modifier_line = match.group(0)
        code, description = modifier_line.split(' ', 1)

        self._parser.add_modifier(ModifierType.Regular, code, description)
