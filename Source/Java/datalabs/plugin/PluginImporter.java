package datalabs.plugin;

public class PluginImporter {
     public static Class importPlugin(String name) throws ClassNotFoundException {
        ClassLoader classLoader = PluginImporter.class.getClassLoader();
        Class pluginClass = classLoader.loadClass(name);

        return pluginClass;
    }
}
