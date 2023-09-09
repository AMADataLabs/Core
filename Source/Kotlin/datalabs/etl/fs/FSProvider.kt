package datalabs.etl.fs

import java.time.LocalDateTime
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter

import datalabs.parameter.Optional
import datalabs.parameter.KParameters


open class FSParameters(parameters: Map<String, String>) : KParameters(parameters) {
    public lateinit var basePath: String
    public lateinit var files: String
    public lateinit var executionTime: String

    public lateinit var unknowns: Map<String, String>
}


open class FSProvider {
    fun getFiles(parameters: FSParameters): List<String> {
        val rawFiles = parameters.files.split(",")
        val files = mutableListOf<String>()

        for (file in rawFiles) {
            files.add(when (parameters.basePath) {
                "" -> file.trim()
                else -> parameters.basePath + "/" + file.trim()
            })
        }

        return files
    }
}
