package datalabs.plugin;

public final class PluginImporter {
     public static Class importPlugin(String name) {
         ClassLoader classLoader = PluginImporter.class.getClassLoader();
         Class plugin_class = classLoader.loadClass("name");

         return plugin_class.newInstance()
    }
