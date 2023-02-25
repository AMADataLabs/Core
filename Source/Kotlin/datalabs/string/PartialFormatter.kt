package datalabs.string

import java.util.*

object PartialFormatter {
    @JvmStatic
    fun format(value: String, parameters: Map<String, Any>): String {
        var resolvedValue = value

        for ((key, value) in parameters) {
            resolvedValue = resolvedValue.replace("\\{$key\\}".toRegex(), value.toString())
        }

        return resolvedValue
    }
}
