package datalabs.tool

import java.util.HashMap

import com.google.gson.Gson
import org.apache.commons.cli.CommandLine
import org.apache.commons.cli.DefaultParser
import org.apache.commons.cli.HelpFormatter
import org.apache.commons.cli.Options
import org.apache.commons.cli.ParseException
import org.slf4j.Logger
import org.slf4j.LoggerFactory

import datalabs.task.LocalProcess


object TaskRunner {
    val logger = LoggerFactory.getLogger(TaskRunner::class.java)

    @JvmStatic
    fun main(args: Array<String>) {
        val commandLineOptions = getCommandLineOptions()

        try {
            val commandLineArgs = TaskRunner.getCommandLineArgs(commandLineOptions, args)

            val runtimeParameters = TaskRunner.getRuntimeParameters(commandLineArgs)
            println("Runtime Parameters: " + runtimeParameters)

            LocalProcess.runTask(runtimeParameters)
        } catch (exception: ParseException) {
            println(exception.message)

            TaskRunner.printUsage(commandLineOptions)
        }
    }

    fun printUsage(options: Options) {
        val formatter = HelpFormatter()

        formatter.printHelp("run-java-task", options)
    }

    fun getCommandLineOptions(): Options {
        val options = Options()

        options.addOption("h", "help", false, "Print this usage message.")
        options.addOption("a", "arg", true, "Command-line argument to send to the task wrapper.")
        options.addOption("e", "event", true, "JSON event passed in as a single command-line argument.")

        return options
    }

    fun getCommandLineArgs(options: Options, args: Array<String>): CommandLine {
        val parser = DefaultParser()
        var commandLineArgs = parser.parse(options, args)

        if (commandLineArgs.hasOption("help")) {
            printUsage(options)
        }

        return commandLineArgs
    }

    fun getRuntimeParameters(args: CommandLine): Map<String, String> {
        var parameters: Map<String, String> = HashMap<String, String>()

        if (args.hasOption("arg")) {
            val commandLine = args.getOptionValues("arg").joinToString(" ")
            val commandLineParameters: HashMap<String, String> = hashMapOf("args" to commandLine)

            parameters = commandLineParameters
        } else if (args.hasOption("event")) {
            @Suppress("UNCHECKED_CAST")
            parameters = Gson().fromJson(args.getOptionValue("event"), Map::class.java) as Map<String, String>
        }

        logger.info("Parameters: " + parameters)

        return parameters
    }
}
