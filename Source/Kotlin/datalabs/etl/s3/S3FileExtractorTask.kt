package datalabs.etl.s3;


import java.time.LocalDateTime
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import java.util.ArrayList
import kotlin.collections.Map

import org.slf4j.Logger
import org.slf4j.LoggerFactory
import software.amazon.awssdk.core.internal.http.loader.DefaultSdkHttpClientBuilder
import software.amazon.awssdk.http.SdkHttpClient
import software.amazon.awssdk.http.SdkHttpConfigurationOption
import software.amazon.awssdk.services.s3.S3Client
import software.amazon.awssdk.services.s3.model.GetObjectRequest
import software.amazon.awssdk.utils.AttributeMap

import datalabs.parameter.Optional
import datalabs.parameter.KParameters
import datalabs.task.Task


open class S3FileExtractorParameters(parameters: Map<String, String>) : KParameters(parameters) {
    public lateinit var bucket: String
    public lateinit var basePath: String
    public lateinit var files: String

    @Optional("True")
    public lateinit var includeDatestamp: String
    @Optional
    public lateinit var executionTime: String

    public lateinit var unknowns: Map<String, String>
}


open class S3FileExtractorTask(parameters: Map<String, String>, data: ArrayList<ByteArray>):
        Task(parameters, null, S3FileExtractorParameters::class.java) {
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

        for (file in rawFiles) {
            files.add(when (basePath) {
                "" -> file.trim()
                else -> basePath + "/" + file.trim()
            })
        }

        return files
    }

    fun getClient(): S3Client {
        val attributeMap = AttributeMap.builder()
                .put(SdkHttpConfigurationOption.TRUST_ALL_CERTIFICATES, true)
                .build();

        var httpClient: SdkHttpClient = when(System.getenv("AWS_NO_VERIFY_SSL")) {
            "True" -> DefaultSdkHttpClientBuilder().buildWithDefaults(attributeMap)
            else -> DefaultSdkHttpClientBuilder().build()
        }

        return S3Client.builder().httpClient(httpClient).build();
    }

    fun extractFiles(client: S3Client, files: List<String>): ArrayList<ByteArray> {
        val outputData = ArrayList<ByteArray>()

        for (file in files) {
            logger.info("Extracting file ${file}")

            outputData.add(extractFile(client, file))

            logger.debug("Extracted data: " + String(outputData.get(outputData.size-1), Charsets.UTF_8))
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
        val datestamp = DateTimeFormatter.ofPattern("yyyyMMdd").format(getExecutionTime())
        var path = parameters.basePath

        if (parameters.includeDatestamp.uppercase() == "TRUE") {
            path += "/" + datestamp
        }

        if (path.startsWith("/")) {
            path = path.substring(1)
        }

        return path
    }

    fun getExecutionTime(): LocalDateTime {
        val parameters = this.parameters as S3FileExtractorParameters

        return when {
            parameters.executionTime == "" -> LocalDateTime.now(ZoneOffset.UTC)
            else -> LocalDateTime.from(DateTimeFormatter.ISO_LOCAL_DATE_TIME.parse(parameters.executionTime))
        }
    }
}
