package datalabs.etl.s3;


import java.text.SimpleDateFormat
import java.time.OffsetDateTime
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import java.util.ArrayList
import kotlin.collections.Map

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import software.amazon.awssdk.services.s3.S3Client
import software.amazon.awssdk.services.s3.model.GetObjectRequest

import datalabs.parameter.Optional
import datalabs.parameter.KParameters
import datalabs.task.Task


open class S3FileExtractorParameters(parameters: Map<String, String>) : KParameters(parameters) {
    public lateinit var bucket: String
    public lateinit var basePath: String
    public lateinit var files: String

    @Optional
    public lateinit var executionTime: String
}


open class S3FileExtractorTask(
    parameters: Map<String, String>,
    data: ArrayList<ByteArray>
) : Task(parameters, data, S3FileExtractorParameters::class.java) {
    internal val logger = LoggerFactory.getLogger(S3FileExtractorTask::class.java)

    override fun run() : ArrayList<ByteArray>? {
        val files = getFiles()
        val outputData: ArrayList<ByteArray>?
        val client = getClient()

        outputData = extractFiles(client, files)

        return outputData
    }

    fun getFiles(): List<String> {
        val basePath = getLatestPath()
        val parameters = this.parameters as S3FileExtractorParameters
        val rawFiles = parameters.files.split(",")
        val files = mutableListOf<String>()

        if (!basePath.equals("")) {
            for (index in 0..files.size) {
                files.add(basePath + "/" + rawFiles[index].trim())
            }
        }

        return files
    }

    fun getClient(): S3Client {
        return S3Client.builder().build();
    }

    fun extractFiles(client: S3Client, files: List<String>): ArrayList<ByteArray> {
        val outputData = ArrayList<ByteArray>()

        for (file in files) {
            outputData.add(extractFile(client, file))
        }

        return outputData
    }

    fun extractFile(client: S3Client, file: String): ByteArray {
        val parameters = this.parameters as S3FileExtractorParameters
        val request = GetObjectRequest.builder().bucket(parameters.bucket).key(file).build()

        return client.getObjectAsBytes(request).asByteArray()
    }

    fun getLatestPath(): String {
        val parameters = this.parameters as S3FileExtractorParameters
        var path = parameters.basePath + "/" + SimpleDateFormat("yyyyMMdd").format(getExecutionTime())

        if (path.startsWith("/")) {
            path = path.substring(1)
        }

        return path
    }

    fun getExecutionTime(): OffsetDateTime {
        val parameters = this.parameters as S3FileExtractorParameters

        return when {
            parameters.executionTime == "" -> OffsetDateTime.now(ZoneOffset.UTC)
            else -> OffsetDateTime.parse(parameters.executionTime, DateTimeFormatter.ISO_LOCAL_DATE_TIME);
        }
    }
}
