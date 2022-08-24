package datalabs.etl.s3;


import java.util.ArrayList
import kotlin.collections.Map

import org.slf4j.Logger
import org.slf4j.LoggerFactory
import software.amazon.awssdk.services.s3.S3Client
import software.amazon.awssdk.services.s3.model.GetObjectRequest

import datalabs.task.Task


open class S3FileExtractorTask(parameters: Map<String, String>, data: ArrayList<ByteArray>):
        Task(parameters, null, S3Parameters::class.java) {
    internal val logger = LoggerFactory.getLogger(S3FileExtractorTask::class.java)

    companion object : S3Provider() { }

    override fun run() : ArrayList<ByteArray> {
        val parameters = this.parameters as S3Parameters
        val client = S3FileExtractorTask.getClient()
        val files = S3FileExtractorTask.getFiles(parameters)

        return extractFiles(client, files)
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
}
