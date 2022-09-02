package datalabs.etl.s3

import java.nio.file.Path
import kotlin.test.assertEquals
import org.junit.jupiter.api.Assumptions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.DisplayName
import org.junit.jupiter.api.Tag
import org.junit.jupiter.api.Test

open class S3FileLoaderTaskTests {
    val PARAMETERS = mutableMapOf(
        "BUCKET" to "ama-sbx-datalake-ingest-us-east-1",
        "BASE_PATH" to "AMA/Test",
        "FILES" to "s3_file_loader_task_tests.txt",
        "EXECUTION_TIME" to "4096-08-16T20:22:02.000",
    )

    val DATA = arrayListOf<ByteArray>(
        "\"Never underestimate the power of human stupidity\" -Robert A. Heinlein".toByteArray(Charsets.UTF_8)
    )

    @Test
    fun loadFileToBucket() {
        Assumptions.assumeTrue(System.getenv("ENABLE_INTEGRATION_TESTS")?.uppercase() ?: "False" == "TRUE")

        val task = S3FileLoaderTask(PARAMETERS, DATA)

        task.run()
    }
}
