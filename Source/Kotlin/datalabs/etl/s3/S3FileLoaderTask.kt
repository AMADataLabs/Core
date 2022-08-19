package datalabs.etl.s3;


import java.text.SimpleDateFormat
import java.time.OffsetDateTime
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import java.util.ArrayList
import kotlin.collections.Map

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import software.amazon.awssdk.core.sync.RequestBody
import software.amazon.awssdk.services.s3.S3Client
import software.amazon.awssdk.services.s3.model.PutObjectRequest

import datalabs.parameter.Optional
import datalabs.parameter.KParameters
import datalabs.task.Task


open class S3FileLoaderParameters(parameters: Map<String, String>) : KParameters(parameters) {
    public lateinit var bucket: String
    public lateinit var basePath: String
    public lateinit var files: String

    @Optional
    public lateinit var executionTime: String
}


open class S3FileLoaderTask(
    parameters: Map<String, String>,
    data: ArrayList<ByteArray>
) : Task(parameters, data, S3FileLoaderParameters::class.java) {
    internal val logger = LoggerFactory.getLogger(S3FileLoaderTask::class.java)

    override fun run() : ArrayList<ByteArray>? {
        val files = getFiles()
        val client = getClient()

        loadFiles(client, files)

        return null
    }

    fun getFiles(): List<String> {
        val basePath = getLatestPath()
        val parameters = this.parameters as S3FileLoaderParameters
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

    fun loadFiles(client: S3Client, files: List<String>) {
        for ((datum, file) in this.data.zip(files)) {
            loadFile(client, datum, file)
        }
    }

    fun loadFile(client: S3Client, data: ByteArray, file: String) {
        val parameters = this.parameters as S3FileLoaderParameters
        val request = PutObjectRequest.builder().bucket(parameters.bucket).key(file).build()

        client.putObject(request, RequestBody.fromBytes(data))
    }

    fun getLatestPath(): String {
        val parameters = this.parameters as S3FileLoaderParameters
        var path = parameters.basePath + "/" + SimpleDateFormat("yyyyMMdd").format(getExecutionTime())

        if (path.startsWith("/")) {
            path = path.substring(1)
        }

        return path
    }

    fun getExecutionTime(): OffsetDateTime {
        val parameters = this.parameters as S3FileLoaderParameters

        return when {
            parameters.executionTime == "" -> OffsetDateTime.now(ZoneOffset.UTC)
            else -> OffsetDateTime.parse(parameters.executionTime, DateTimeFormatter.ISO_LOCAL_DATE_TIME);
        }
    }
}
