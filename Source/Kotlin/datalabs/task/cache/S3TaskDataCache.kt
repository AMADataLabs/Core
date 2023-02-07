package datalabs.task.cache;

import java.util.ArrayList;
import kotlin.collections.Map

import datalabs.etl.s3.S3FileExtractorTask;
import datalabs.etl.s3.S3FileLoaderTask;
import datalabs.task.TaskException;


open class S3TaskDataCache(parameters: Map<String, String>): TaskDataCache(parameters) {
    override fun extractData(): ArrayList<ByteArray> {
        val extractor = S3FileExtractorTask(this.parameters, ArrayList<ByteArray>())

        val inputData = extractor.run()

        if (inputData == null) {
            throw TaskException("No data was extracted.")
        }

        return inputData
    }

    override fun loadData(outputData: ArrayList<ByteArray>) {
        val loader = S3FileLoaderTask(this.parameters, outputData)

        loader.run()
    }
}
