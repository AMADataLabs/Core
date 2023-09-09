package datalabs.etl.fs;


import java.util.ArrayList
import java.io.File
import kotlin.collections.Map

import org.slf4j.Logger
import org.slf4j.LoggerFactory

import datalabs.task.Task


open class LocalFileLoaderTask(
    parameters: Map<String, String>,
    data: ArrayList<ByteArray>
) : Task(parameters, data, FSParameters::class.java) {
    internal val logger = LoggerFactory.getLogger(LocalFileLoaderTask::class.java)

    companion object : FSProvider() { }

    override fun run() : ArrayList<ByteArray> {
        val parameters = this.parameters as FSParameters
        val files = LocalFileLoaderTask.getFiles(parameters)

        loadFiles(files)

        return ArrayList<ByteArray>()
    }

    fun loadFiles(files: List<String>) {
        for ((datum, file) in this.data.zip(files)) {
            File(file).writeBytes(datum)
        }
    }
}
