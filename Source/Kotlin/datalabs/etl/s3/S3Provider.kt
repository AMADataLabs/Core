package datalabs.etl.s3

import java.time.LocalDateTime
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import software.amazon.awssdk.core.internal.http.loader.DefaultSdkHttpClientBuilder
import software.amazon.awssdk.http.SdkHttpClient
import software.amazon.awssdk.http.SdkHttpConfigurationOption
import software.amazon.awssdk.services.s3.S3Client
import software.amazon.awssdk.utils.AttributeMap

import datalabs.parameter.Optional
import datalabs.parameter.KParameters


open class S3Parameters(parameters: Map<String, String>) : KParameters(parameters) {
    public lateinit var bucket: String
    public lateinit var basePath: String
    public lateinit var files: String

    @Optional("True")
    public lateinit var includeDatestamp: String
    @Optional
    public lateinit var executionTime: String

    public lateinit var unknowns: Map<String, String>
}


open class S3Provider {
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

    fun getFiles(parameters: S3Parameters): List<String> {
        val includeDatestamp = parameters.includeDatestamp.uppercase() == "TRUE"
        val basePath = getRunPath(
            parameters.basePath,
            parameters.executionTime,
            includeDatestamp
        )
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

    fun getRunPath(basePath: String, executionTime: String, includeDatestamp: Boolean): String {
        val datestamp = DateTimeFormatter.ofPattern("yyyyMMdd").format(parseExecutionTime(executionTime))
        var path = basePath

        if (includeDatestamp) {
            path += "/" + datestamp
        }

        if (path.startsWith("/")) {
            path = path.substring(1)
        }

        return path
    }

    fun parseExecutionTime(executionTime: String): LocalDateTime {
        return when (executionTime) {
            "" -> LocalDateTime.now(ZoneOffset.UTC)
            else -> LocalDateTime.from(DateTimeFormatter.ISO_LOCAL_DATE_TIME.parse(executionTime))
        }
    }
}
