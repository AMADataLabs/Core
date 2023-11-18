""" xml converter. """

from re import sub
import xmltodict


class XMLToDictConverter:
    def parse_xml_to_dict(self, xml):
        return xmltodict.parse(
            xml.decode("utf-8"),
            xml_attribs=False,
            postprocessor=self._format_xml_element
        )

    # pylint: disable=unused-argument
    def _format_xml_element(self, path, key, value):
        formatted_value = value

        if value is not None and isinstance(value, str):
            try:
                formatted_value = int(value)
            except ValueError:
                formatted_value = self._convert_boolean_value(value)

        return self._format_as_snake_case(key), formatted_value

    @classmethod
    def _convert_boolean_value(cls, value):
        return_value = value

        if value.lower() == "true":
            return_value = True
        elif value.lower() == "false":
            return_value = False

        return return_value

    @classmethod
    def _format_as_snake_case(cls, text):
        return "_".join(sub("([A-Z][a-z]+)", r" \1", sub("([A-Z]+)", r" \1", text.replace("-", " "))).split()).lower()
