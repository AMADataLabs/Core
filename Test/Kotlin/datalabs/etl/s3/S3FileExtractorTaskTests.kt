package datalabs.etl.s3

import java.util.ArrayList
import kotlin.test.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.DisplayName
import org.junit.jupiter.api.Tag
import org.junit.jupiter.api.Test

open class S3FileExtractorTaskTests {
    private val PARAMETERS = mutableMapOf(
        "BUCKET" to "ama-none-datalake-unit-tests-us-east-1",
        "BASE_PATH" to "dir1/dir2",
        "FILES" to "something.txt,doodad.csv,ratatat.bmp",
        "EXECUTION_TIME" to "2022-02-20T20:22:02.000",
    )

    @Test
    fun filePathsAreBuiltFromParameters() {
        val task = S3FileExtractorTask(PARAMETERS, ArrayList<ByteArray>())

        val files = task.getFiles()

        assertEquals(3, files.size)
    }
}
