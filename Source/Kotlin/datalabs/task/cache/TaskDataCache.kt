package datalabs.task.cache;

import java.util.ArrayList;

import datalabs.etl.s3.S3FileExtractorTask;
import datalabs.etl.s3.S3FileLoaderTask;
import datalabs.task.TaskException;


abstract class TaskDataCache(parameters: Map<String, String>) {
    enum class Direction {
        INPUT, OUTPUT
    }

    protected var parameters: Map<String, String> = parameters

    abstract fun extractData(): ArrayList<ByteArray>

    abstract fun loadData(outputData: ArrayList<ByteArray>)
}
