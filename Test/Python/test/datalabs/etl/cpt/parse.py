""" Test Parser class """
import pandas


class TestParser:
    # pylint: disable=no-self-use
    def parse(self, text):
        return pandas.DataFrame([text])
