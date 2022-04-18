package datalabs.tool;

import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.stream.Stream;

import com.google.gson.Gson;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import datalabs.plugin.PluginImporter;
import datalabs.task.LocalProcess;


public class TaskRunner {
    protected static final Logger LOGGER = LoggerFactory.getLogger(TaskRunner.class);

    public static void main(String[] args) {
        Options commandLineOptions = null;

        try {
            commandLineOptions = getCommandLineOptions();

            CommandLine commandLineArgs = getCommandLineArgs(commandLineOptions, args);

            Map<String, String> runtimeParameters = getRuntimeParameters(commandLineArgs);
            System.out.println("Runtime Parameters: " + runtimeParameters);

            LocalProcess.runTask(runtimeParameters);
        } catch (ParseException exception) {
            System.out.println(exception.getMessage());

            printUsage(commandLineOptions);
        } catch (
            IllegalAccessException | InstantiationException | InvocationTargetException | NoSuchMethodException |
            ClassNotFoundException exception
        ) {
            System.out.println(exception.getMessage());

            exception.printStackTrace();
        }
    }

    static void printUsage(Options options) {
        HelpFormatter formatter = new HelpFormatter();

        formatter.printHelp("run-java-task", options);
    }

    static Options getCommandLineOptions() throws ParseException {
        Options options = new Options();

        options.addOption("h", "help", false, "Print this usage message.");
        options.addOption("a", "arg", true, "Command-line argument to send to the task wrapper.");
        options.addOption("e", "event", true, "JSON event passed in as a single command-line argument.");

        return options;
    }

    static CommandLine getCommandLineArgs(Options options, String[] args) throws ParseException {
        CommandLineParser parser = new DefaultParser();
        CommandLine commandLineArgs;

        commandLineArgs = parser.parse(options, args);

        if (commandLineArgs.hasOption("help")) {
            printUsage(options);
        }

        return commandLineArgs;
    }

    static Map<String, String> getRuntimeParameters(CommandLine args) {
        Map<String, String> parameters = new HashMap<String, String>();
        LOGGER.debug(parameters.toString());

        if (args.hasOption("arg")) {
            String commandLine = String.join(" ", args.getOptionValues("arg"));

            parameters.put("args", commandLine);
        } else if (args.hasOption("event")) {
            parameters = (Map<String, String>) new Gson().fromJson(args.getOptionValue("event"), Map.class);
        }
        LOGGER.debug("Parameters: " + parameters);

        return parameters;
    }
}
