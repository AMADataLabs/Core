package datalabs.plugin;

public final class PluginImporter {
     public static Class importPlugin(String name) {
         ClassLoader classLoader = PluginImporter.class.getClassLoader();
         Class pluginClass = classLoader.loadClass("name");

         return pluginClass;
    }
}
