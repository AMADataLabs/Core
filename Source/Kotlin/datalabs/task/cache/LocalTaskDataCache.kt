package datalabs.task.cache;

import java.util.ArrayList;

import datalabs.etl.fs.LocalFileExtractorTask;
import datalabs.etl.fs.LocalFileLoaderTask;
import datalabs.task.TaskException;


open class LocalTaskDataCache(parameters: Map<String, String>): TaskDataCache(parameters) {
    override fun extractData(): ArrayList<ByteArray> {
        val extractor = LocalFileExtractorTask(this.parameters, ArrayList<ByteArray>())

        val inputData = extractor.run()

        @Suppress("SENSELESS_COMPARISON")  // This is empirically not always null
        if (inputData == null) {
            throw TaskException("No data was extracted.")
        }

        return inputData
    }

    override fun loadData(outputData: ArrayList<ByteArray>) {
        val loader = LocalFileLoaderTask(this.parameters, outputData)

        loader.run()
    }
}
