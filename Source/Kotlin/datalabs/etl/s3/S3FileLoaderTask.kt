package datalabs.etl.s3;


import java.text.SimpleDateFormat
import java.time.OffsetDateTime
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import java.util.ArrayList
import kotlin.collections.Map

import org.slf4j.Logger
import org.slf4j.LoggerFactory
import software.amazon.awssdk.core.internal.http.loader.DefaultSdkHttpClientBuilder
import software.amazon.awssdk.http.SdkHttpClient
import software.amazon.awssdk.http.SdkHttpConfigurationOption
import software.amazon.awssdk.core.sync.RequestBody
import software.amazon.awssdk.services.s3.S3Client
import software.amazon.awssdk.services.s3.model.PutObjectRequest
import software.amazon.awssdk.utils.AttributeMap

import datalabs.parameter.Optional
import datalabs.parameter.KParameters
import datalabs.task.Task


open class S3FileLoaderTask(
    parameters: Map<String, String>,
    data: ArrayList<ByteArray>
) : Task(parameters, data, S3Parameters::class.java) {
    internal val logger = LoggerFactory.getLogger(S3FileLoaderTask::class.java)

    companion object : S3Provider() { }

    override fun run() : ArrayList<ByteArray> {
        val parameters = this.parameters as S3Parameters
        val client = S3FileLoaderTask.getClient()
        val files = S3FileLoaderTask.getFiles(parameters)

        loadFiles(client, files)

        return ArrayList<ByteArray>()
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
}
