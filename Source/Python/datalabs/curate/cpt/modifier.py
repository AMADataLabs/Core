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
    UNKNOWN = 0
    BEGINNING = 1
    CATEGORY_ONE = 2
    ANESTHESIA_PHYSICAL_STATUS = 3
    AMBULATORY_SERVICE_CENTER = 4
    CATEGORY_TWO = 5
    LEVEL_TWO = 6
    END = 7


class Event(Enum):
    START = 0
    BLANK = 1
    TEXT = 2
    MODIFIER = 3
    APPENDIX_A = 4
    ANESTHESIA_PHYSICAL_STATUS = 5
    CPT_LEVEL_I_MODIFIERS = 6
    CATEGORY_II_MODIFIERS = 7
    LEVEL_II_MODIFIERS = 8


class ModifierType(Enum):
    CATEGORY_ONE = 'Category I'
    ANESTHESIA_PHYSICAL_STATUS = 'Anesthesia Physical Status'
    AMBULATORY_SERVICE_CENTER = 'Ambulatory Service Center'
    CATEGORY_TWO = 'Category II'
    LEVEL_TWO = 'Level II'


Context = namedtuple('Context', 'state event data')


class ModifierParser(Parser):
    # pylint: disable=line-too-long
    TRANSITION_TABLE = [
        # START             BLANK                             TEXT                              MODIFIER                          APPENDIX_A          ANESTHESIA_PHYSICAL_STATUS        CPT_LEVEL_I_MODIFIERS            CATEGORY_II_MODIFIERS LEVEL_II_MODIFIERS
        [State.UNKNOWN,     State.UNKNOWN,                    State.UNKNOWN,                    State.UNKNOWN,                    State.UNKNOWN,      State.UNKNOWN,                    State.UNKNOWN,                   State.UNKNOWN,        State.UNKNOWN],    # UNKNOWN
        [State.BEGINNING,   State.BEGINNING,                  State.BEGINNING,                  State.UNKNOWN,                    State.CATEGORY_ONE, State.UNKNOWN,                    State.UNKNOWN,                   State.UNKNOWN,        State.UNKNOWN],    # BEGINNING
        [State.UNKNOWN,     State.CATEGORY_ONE,               State.CATEGORY_ONE,               State.CATEGORY_ONE,               State.UNKNOWN,      State.ANESTHESIA_PHYSICAL_STATUS, State.UNKNOWN,                   State.UNKNOWN,        State.UNKNOWN],    # CATEGORY_ONE
        [State.UNKNOWN,     State.ANESTHESIA_PHYSICAL_STATUS, State.ANESTHESIA_PHYSICAL_STATUS, State.ANESTHESIA_PHYSICAL_STATUS, State.UNKNOWN,      State.UNKNOWN,                    State.AMBULATORY_SERVICE_CENTER, State.UNKNOWN,        State.UNKNOWN],    # ANESTHESIA_PHYSICAL_STATUS
        [State.UNKNOWN,     State.AMBULATORY_SERVICE_CENTER,  State.AMBULATORY_SERVICE_CENTER,  State.AMBULATORY_SERVICE_CENTER,  State.UNKNOWN,      State.UNKNOWN,                    State.UNKNOWN,                   State.CATEGORY_TWO,   State.UNKNOWN],    # AMBULATORY_SERVICE_CENTER
        [State.UNKNOWN,     State.CATEGORY_TWO,               State.CATEGORY_TWO,               State.CATEGORY_TWO,               State.UNKNOWN,      State.UNKNOWN,                    State.UNKNOWN,                   State.UNKNOWN,        State.LEVEL_TWO],  # CATEGORY_TWO
        [State.UNKNOWN,     State.LEVEL_TWO,                  State.LEVEL_TWO,                  State.LEVEL_TWO,                  State.UNKNOWN,      State.UNKNOWN,                    State.UNKNOWN,                   State.UNKNOWN,        State.UNKNOWN],    # LEVEL_TWO
    ]

    def __init__(self):
        self._modifiers = {
            ModifierType.CATEGORY_ONE: {},
            ModifierType.ANESTHESIA_PHYSICAL_STATUS: {},
            ModifierType.AMBULATORY_SERVICE_CENTER: {},
            ModifierType.CATEGORY_TWO: {},
            ModifierType.LEVEL_TWO: {},
        }
        self._state_processors = [
            None,
            AppendixAProcessor(self),
            CetegoryOneProcessor(self),
            AnesthesiaPhysicalStatusProcessor(self),
            AmbulatoryServiceCenterProcessor(self),
            CategoryTwoProcessor(self),
            LevelTwoProcessor(self)
        ]

    def add_modifier(self, modifier_type: ModifierType, code: str, description: str):
        self._modifiers[modifier_type][code] = description

    def parse(self, text: str):
        lines = text.decode('cp1252').splitlines()

        self._parse_lines(lines)
        LOGGER.debug('Dict: \n%s', self._modifiers)

        return self._generate_dataframe()

    def _parse_lines(self, lines):
        context = Context(state=State.BEGINNING, event=Event.START, data='')

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
        event = Event.START
        data = ''

        if line == 'Appendix A':
            event = Event.APPENDIX_A

        return Context(state=None, event=event, data=data)


class CetegoryOneProcessor(StateProcessor):
    def process_line(self, context, line):
        event = context.event
        data = context.data
        match = re.match('[1-9][0-9] ..*', line)

        if line == 'Anesthesia Physical Status':
            event = Event.ANESTHESIA_PHYSICAL_STATUS
            data = ''
        elif context.event != Event.MODIFIER and match:
            event = Event.MODIFIER
            data = data + ' ' + line
        elif context.event == Event.MODIFIER and line != '':
            data = data + ' ' + line
        elif context.event == Event.MODIFIER and line == '':
            event = Event.BLANK
            match = data.strip()
            self._process_match(match)
            data = ''
        elif line == '':
            event = Event.BLANK
        else:
            event = Event.TEXT

        return Context(state=None, event=event, data=data)

    def _process_match(self, match):
        code, description = match.split(' ', 1)
        self._parser.add_modifier(ModifierType.CATEGORY_ONE, code, description)


class AnesthesiaPhysicalStatusProcessor(StateProcessor):
    def process_line(self, context, line):

        data = context.data
        event = Event.MODIFIER
        match = re.match('.*(P[0-9]):(.*)', line)

        if line == 'CPT Level I Modifiers':
            event = Event.CPT_LEVEL_I_MODIFIERS

        elif line == '':
            event = Event.BLANK

        elif match:
            self._process_match(match)

        elif line != '':
            event = Event.TEXT

        elif line == '':
            event = Event.BLANK

        return Context(state=None, event=event, data=data)

    def _process_match(self, match):
        code = match.group(1)
        description = match.group(2)
        self._parser.add_modifier(ModifierType.ANESTHESIA_PHYSICAL_STATUS, code, description)


class AmbulatoryServiceCenterProcessor(StateProcessor):
    def process_line(self, context, line):

        event = context.event
        data = context.data
        match = re.match('[1-9][0-9] ..*', line)

        if line == 'Category II Modifiers':
            event = Event.CATEGORY_II_MODIFIERS
            data = ''

        elif context.event != Event.MODIFIER and match:
            event = Event.MODIFIER
            data = data + ' ' + line

        elif context.event == Event.MODIFIER and line != '':
            data = data + ' ' + line

        elif context.event == Event.MODIFIER and line == '':
            event = Event.BLANK
            self._process_match(data.strip())
            data = ''
        elif line != '':
            event = Event.TEXT

        elif line == '':
            event = Event.BLANK

        return Context(state=None, event=event, data=data)

    def _process_match(self, code_description_line):
        code, description = code_description_line.split(' ', 1)
        self._parser.add_modifier(ModifierType.AMBULATORY_SERVICE_CENTER, code, description)


class CategoryTwoProcessor(StateProcessor):
    def process_line(self, context, line):

        event = context.event
        data = context.data
        match = re.match('[1-9][A-Z] ..*', line)

        if line == 'Level II (HCPCS/National) Modifiers':
            event = Event.LEVEL_II_MODIFIERS
            data = ''

        elif context.event != Event.MODIFIER and match:
            event = Event.MODIFIER
            data = data + ' ' + line

        elif context.event == Event.MODIFIER and line != '':
            data = data + ' ' + line

        elif context.event == Event.MODIFIER and line == '':
            event = Event.BLANK
            self._process_match(data.strip())
            data = ''
        elif line != '':
            event = Event.TEXT

        elif line == '':
            event = Event.BLANK

        return Context(state=None, event=event, data=data)

    def _process_match(self, code_description_line):
        code, description = code_description_line.split(' ', 1)
        self._parser.add_modifier(ModifierType.CATEGORY_TWO, code, description)


class LevelTwoProcessor(StateProcessor):
    def process_line(self, context, line):

        data = context.data
        event = Event.MODIFIER
        match = re.match('([A-Z][0-9A-Z])(.*)', line)

        if line == '':
            event = Event.BLANK

        elif match:
            self._process_match(match)

        else:
            event = Event.TEXT

        return Context(state=None, event=event, data=data)

    def _process_match(self, match):
        code = match.group(1)
        description = match.group(2)
        self._parser.add_modifier(ModifierType.LEVEL_TWO, code, description)
