package datalabs.example.etl

import java.util.ArrayList
import kotlin.test.assertNull
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.DisplayName
import org.junit.jupiter.api.Tag
import org.junit.jupiter.api.Test

open class HelloWorldKotlinTaskTests {
    private val PARAMETERS = mapOf("FIRST_NAME" to "Peter")

    @Test
    fun instantiationWithRequiredParametersSucceeds() {
        val task = HelloWorldKotlinTask(PARAMETERS, ArrayList<ByteArray>())

        val outputData = task.run()

        assertNull(outputData)
    }
}
