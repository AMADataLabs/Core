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


Context = namedtuple('Context', 'state event data')


class StateProcessor(ABC):
    @abstractmethod
    def handle_event(self, context, line):
        pass


class AppendixAProcessor(EventHandler):
    def handle_event(self, data, line):
        event = Event.Start
        data = {}

        if line == 'Appendix A':
            event = Event.RegularModifier

        return Context(state=State.AppendixAHandler, event=event, data=data)


class RegularModifierProcessor(EventHandler):
    def handle_event(self, context, line):
        event = None
        data = {}
        match = re.match('[1-9][0-9] ..*')

        if line == 'Anesthesia Physical Status':
            event = Event.AnesthesiaPhysicalStatus
        elif line == '':
            event = Event.Blank
        elif match:
            event,data = self._process_match(context, match)

        return Context(state=context.state, event=event, data=data)

    def _process_match(self, context, match):
        pass


class FileParser():
    TRANSITION_TABLE = [
        # Start           Blank                      Text                       Modifier                   AppendixA              AnesthesiaPhysicalStatus  CPTLevelIModifiers      CategoryIIModifiers       LevelIIModifiers
        [State.Unknown,   State.Unkown,              State.Unkown,              State.Unkown,              State.Unkown,          State.Unkown,             State.Unkown,           State.Unkown,              State.Unkown]            # Unknown
        [State.Beginning, State.Beginning,           State.Beginning,           State.Unkown,              State.RegularModifier, State.Unkown,             State.Unkown,           State.Unkown,              State.Unknown]           # Beginning
        [State.Unknown,   State.RegularModifier,     State.RegularModifier,     State.RegularModifier,     State.Unknown,         State.PhysicalModifier,   State.Unknown,          State.Unknown,             State.Unknown]           # RegularModifier
        [State.Unknown,   State.PhysicalModifier,    State.PhysicalModifier,    PhysicalModifier,          State.Unknown,         State.Unknown,            State.LevelOneModifier, State.Unknown,             State.Unknown]           # PhysicalModifier
        [State.Unknown,   State.LevelOneModifier,    State.LevelOneModifier,    State.LevelOneModifier,    State.Unknown,         State.Unknown,            State.Unknown,          State.CategoryTwoModifier, State.Unknown]           # LevelOneModifier
        [State.Unknown,   State.CategoryTwoModifier, State.CategoryTwoModifier, State.CategoryTwoModifier, State.Unknown,         State.Unknown,            State.Unknown,          State.Unknown,             State.LevelTwoModifier]  # CategoryTwoModifier
        [State.Unknown,   State.LevelTwoModifier,    State.LevelTwoModifier,    State.LevelTwoModifier,    State.Unknown,         State.Unknown,            State.Unknown,          State.Unknown,             State.Unknown]           # LevelTwoModifier
    ]

    STATE_PROCESSORS = [
        AppendixAProcessor(),
        RegularModifierProcessor(),
        # ...
    ]

    @classmethod
    def parse(cls, input_filename: str, output_filename: str) -> dict:
        lines = _read_file(input_filename)

        data = _parse_file(lines)

        _write_data(data, output_filename)

    @classmethod
    def _read_file(cls, input_filename):
        with open(input_filename) as file:
            return file.readlines()

    @classmethod
    def _parse_file(cls, lines):
        context = Context(state=State.InitialModifiers, event=Event.Start, data={})

        for line in lines:
            context = cls._handle_event(context, line.strip())

    @classmethod
    def _process_event(cls, context, line):
        state = TRANSITION_TABLE[context.state.value][context.event.value]

        return STATE_PROCESSORS[state.value].process_line(context, line)
