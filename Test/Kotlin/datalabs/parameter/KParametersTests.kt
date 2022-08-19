package datalabs.parameter

import java.util.ArrayList
import kotlin.collections.Map
import kotlin.test.assertEquals

import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.DisplayName
import org.junit.jupiter.api.Tag
import org.junit.jupiter.api.Test


open class TestParameters(parameters: Map<String, String>) : KParameters(parameters) {
    public lateinit var ping: String

    @Optional
    public lateinit var biff: String
}


open class KParametersTests {
    @Test
    fun instantiationSucceeds() {
        val parameters = TestParameters(mapOf("PING" to "pong"))

        assertEquals("pong", parameters.ping)
        assertEquals("", parameters.biff)
    }
}
