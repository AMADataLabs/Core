package datalabs.etl.s3

import java.util.ArrayList
import kotlin.test.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.DisplayName
import org.junit.jupiter.api.Tag
import org.junit.jupiter.api.Test

open class S3FileExtractorTaskTests {
    private val PARAMETERS = S3Parameters(
        mutableMapOf(
            "BUCKET" to "ama-none-datalake-unit-tests-us-east-1",
            "BASE_PATH" to "dir1/dir2",
            "FILES" to "something.txt, doodad.csv, ratatat.bmp ",
            "EXECUTION_TIME" to "2022-02-20T20:22:02.000",
        )
    )

    @Test
    fun filePathsAreBuiltFromParameters() {
        val files = S3Provider().getFiles(PARAMETERS)

        assertEquals(3, files.size)
        assertEquals("dir1/dir2/20220220/something.txt", files[0])
        assertEquals("dir1/dir2/20220220/doodad.csv", files[1])
        assertEquals("dir1/dir2/20220220/ratatat.bmp", files[2])
    }

    @Test
    fun datestampIsOmittedWhenIncludeDatestampIsFalse() {
        PARAMETERS.includeDatestamp = "False"

        val files = S3Provider().getFiles(PARAMETERS)

        assertEquals(3, files.size)
        assertEquals("dir1/dir2/something.txt", files[0])
        assertEquals("dir1/dir2/doodad.csv", files[1])
        assertEquals("dir1/dir2/ratatat.bmp", files[2])
    }
}
