""" source: datalabs.plugin """
import datalabs.plugin as plugin


def test_plugin_loads():
    TestPlugin = plugin.import_plugin('test.datalabs.test_plugin.Plugin')  # pylint: disable=invalid-name
    test_plugin = TestPlugin()

    assert hasattr(test_plugin, 'do_stuff')

    assert test_plugin.do_stuff()


class Plugin:
    @classmethod
    def do_stuff(cls):
        return True
