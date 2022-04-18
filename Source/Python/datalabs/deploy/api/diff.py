""" Class to find differences between API specification YAML files. """
import logging

import yaml

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class APISpecDifferentiator:
    @classmethod
    def diff(cls, path1, path2):
        spec1 = cls._parse_api_spec(cls._load_api_spec(path1))
        spec2 = cls._parse_api_spec(cls._load_api_spec(path2))

        cls._report_new_endpoints(spec1, spec2)

        cls._report_missing_endpoints(spec1, spec2)

        cls._report_differing_elements(spec1, spec2)

    @classmethod
    def _load_api_spec(cls, spec_path) -> str:
        LOGGER.debug('API spec path: %s', spec_path)
        spec_yaml = None

        with open(spec_path, 'r') as file:
            spec_yaml = file.read()

        return spec_yaml

    @classmethod
    def _parse_api_spec(cls, spec_yaml) -> dict:
        spec = yaml.safe_load(spec_yaml)
        LOGGER.debug('API spec: %s', spec)

        return spec

    @classmethod
    def _report_new_endpoints(cls, spec1, spec2):
        new_endpoints = cls._find_new_elements(spec1['paths'], spec2['paths'])

        if len(new_endpoints) > 0:
            print('The following endpoints are new:')
            for endpoint in new_endpoints:
                print(f"\t{endpoint}")

    @classmethod
    def _report_missing_endpoints(cls, spec1, spec2):
        missing_endpoints = cls._find_missing_elements(spec1['paths'], spec2['paths'])

        if len(missing_endpoints) > 0:
            print('The following endpoints are missing:')
            for endpoint in missing_endpoints:
                print(f"\t{endpoint}")

    @classmethod
    def _report_differing_elements(cls, spec1, spec2):
        new_elements = None
        missing_elements = None
        differing_elements = None
        results = cls._find_differing_elements(spec1['paths'], spec2['paths'])
        if results:
            new_elements, missing_elements, differing_elements = results

        if new_elements:
            for endpoint, elements in new_elements.items():
                if elements:
                    print(f'The following elements are new in endpoint {endpoint}: {elements}')

        if missing_elements:
            for endpoint, elements in missing_elements.items():
                if elements:
                    print(f'The following elements are missing from endpoint {endpoint}: {elements}')

        if differing_elements:
            for endpoint, elements in differing_elements.items():
                if elements:
                    print(f'The following elements differ in endpoint {endpoint}: {elements}')

    @classmethod
    def _find_new_elements(cls, spec1, spec2):
        return cls._find_missing_elements(spec2, spec1)

    @classmethod
    def _find_missing_elements(cls, spec1, spec2):
        elements1 = spec1.keys()
        elements2 = spec2.keys()
        missing_elements = []

        for element in elements1:
            if element not in elements2:
                missing_elements.append(element)

        return missing_elements

    @classmethod
    def _find_differing_elements(cls, spec1, spec2):
        elements1 = set(spec1.keys())
        elements2 = set(spec2.keys())
        common_elements = elements1.intersection(elements2)
        new_elements = {}
        missing_elements = {}
        differing_elements = {}
        results = None

        for element in common_elements:
            if hasattr(spec1[element], 'keys') and hasattr(spec2[element], 'keys'):
                elements = cls._find_new_elements(spec1[element], spec2[element])
                if elements:
                    new_elements[element] = elements

                elements = cls._find_missing_elements(spec1[element], spec2[element])
                if elements:
                    missing_elements[element] = elements

                elements = cls._find_differing_elements(spec1[element], spec2[element])
                if elements:
                    differing_elements[element] = elements

        if new_elements or missing_elements or differing_elements:
            results = (new_elements, missing_elements, differing_elements)

        return results
