""" File parser for CPT'S MODUL.txt file using a state machine pattern. """
from   abc import ABC, abstractmethod
from   collections import namedtuple
from   enum import Enum
import logging
import re

import pandas as pd

from datalabs.curate.parse import Parser

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


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
    Regular = 'Regular'
    Physical = 'Physical'
    LevelOne = 'Level I'
    CategoryTwo = 'Category II'
    LevelTwo = 'Level II'


Context = namedtuple('Context', 'state event data')


# pylint: disable=bad-continuation
class ModifierParser(Parser):
    # pylint: disable=line-too-long,bad-whitespace
    TRANSITION_TABLE = [
        # Start             Blank                   Text                            Modifier
        #   AppendixA              AnesthesiaPhysicalStatus    CPTLevelIModifiers          CategoryIIModifiers
        #   LevelIIModifiers
        [State.Unknown,     State.Unknown,          State.Unknown,                  State.Unknown,
            State.Unknown,          State.Unknown,              State.Unknown,              State.Unknown,
            State.Unknown],  # Unknown
        [State.Beginning,   State.Beginning,        State.Beginning,                State.Unknown,
            State.RegularModifier,  State.Unknown,              State.Unknown,              State.Unknown,
            State.Unknown],  # Beginning
        [State.Unknown,     State.RegularModifier,  State.RegularModifier,          State.RegularModifier,
            State.Unknown,          State.PhysicalModifier,     State.Unknown,              State.Unknown,
            State.Unknown],  # RegularModifier
        [State.Unknown,     State.PhysicalModifier, State.PhysicalModifier,         State.PhysicalModifier,
            State.Unknown,          State.Unknown,          State.LevelOneModifier,     State.Unknown,
            State.Unknown],  # PhysicalModifier
        [State.Unknown,     State.LevelOneModifier, State.LevelOneModifier,         State.LevelOneModifier,
            State.Unknown,          State.Unknown,          State.Unknown,              State.CategoryTwoModifier,
            State.Unknown],  # LevelOneModifier
        [State.Unknown,     State.CategoryTwoModifier, State.CategoryTwoModifier,   State.CategoryTwoModifier,
            State.Unknown,          State.Unknown,          State.Unknown,              State.Unknown,
            State.LevelTwoModifier],  # CategoryTwoModifier
        [State.Unknown,     State.LevelTwoModifier, State.LevelTwoModifier,         State.LevelTwoModifier,
            State.Unknown,          State.Unknown,          State.Unknown,              State.Unknown,
            State.Unknown],  # LevelTwoModifier
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
            None,
            AppendixAProcessor(self),
            RegularModifierProcessor(self),
            PhysicalModifierProcessor(self),
            LevelOneModifierProcessor(self),
            CategoryTwoModifier(self),
            LevelTwoModifierProcessor(self)
        ]

    def add_modifier(self, modifier_type: ModifierType, code: str, description: str):
        self._modifiers[modifier_type][code] = description

    def parse(self, text: str):
        lines = text.splitlines()

        self._parse_lines(lines)
        LOGGER.debug('Dict: \n%s', self._modifiers)

        return self._generate_dataframe()

    def _parse_lines(self, lines):
        context = Context(state=State.Beginning, event=Event.Start, data='')

        for line in lines:
            context = self._process_event(context, line.strip())

    def _generate_dataframe(self):
        rows = []

        for modifier_type, modifiers in self._modifiers.items():
            for code, descriptor in modifiers.items():
                rows.append([code, modifier_type.value, descriptor])

        return pd.DataFrame(rows, columns=['modifier', 'type', 'descriptor'])

    def _process_event(self, context, line):
        _, event, data = self._state_processors[context.state.value].process_line(context, line)

        state = self.TRANSITION_TABLE[context.state.value][event.value]

        return Context(state=state, event=event, data=data)

class StateProcessor(ABC):
    def __init__(self, parser: ModifierParser):
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
