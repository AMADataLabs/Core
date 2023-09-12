package datalabs.etl.fs;


import java.util.ArrayList
import java.io.File
import kotlin.collections.Map

import org.slf4j.Logger
import org.slf4j.LoggerFactory

import datalabs.task.Task


@Suppress("UNUSED_PARAMETER")
open class LocalFileExtractorTask(parameters: Map<String, String>, data: ArrayList<ByteArray>):
        Task(parameters, null, FSParameters::class.java) {
    internal val logger = LoggerFactory.getLogger(LocalFileExtractorTask::class.java)

    companion object : FSProvider() { }

    override fun run() : ArrayList<ByteArray> {
        val parameters = this.parameters as FSParameters
        val files = LocalFileExtractorTask.getFiles(parameters)

        return extractFiles(files)
    }

    fun extractFiles(files: List<String>): ArrayList<ByteArray> {
        val outputData = ArrayList<ByteArray>()

        for (file in files) {
            logger.info("Extracting file ${file}")

            outputData.add(File(file).readBytes())

            logger.debug("Extracted data: " + String(outputData.get(outputData.size-1), Charsets.UTF_8))
        }

        return outputData
    }
}
