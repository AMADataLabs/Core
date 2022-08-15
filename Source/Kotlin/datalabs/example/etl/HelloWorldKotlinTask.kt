package datalabs.example.etl

import java.util.Vector
import kotlin.collections.Map

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import datalabs.parameter.Optional
import datalabs.parameter.KParameters
import datalabs.task.Task


open class HelloWorldKotlinParameters(parameters: Map<String, String>) : KParameters(parameters) {
    public lateinit var firstName: String

    @Optional
    public lateinit var lastName: String
}


open class HelloWorldKotlinTask(
    parameters: Map<String, String>,
    data: Vector<ByteArray>
) : Task(parameters, data, HelloWorldKotlinParameters::class.java) {
    internal val logger = LoggerFactory.getLogger(HelloWorldKotlinTask::class.java)

    override fun run() : Vector<ByteArray>? {
        logger.info("Hello, World!")
        return null
    }
}
