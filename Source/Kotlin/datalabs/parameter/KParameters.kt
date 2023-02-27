package datalabs.parameter

import java.util.ArrayList
import kotlin.collections.Map
import kotlin.reflect.KProperty1
import kotlin.reflect.KMutableProperty1
import kotlin.reflect.full.memberProperties
import kotlin.reflect.full.findAnnotation

import datalabs.parameter.Optional
import datalabs.parameter.Parameters


open class KParameters(parameters: Map<String, String>)  : Parameters() {
    init {
        val fields = this::class.java.declaredFields
        for (field in fields) {
            val annotation = field.getAnnotation(Optional::class.java)
            @Suppress("UNCHECKED_CAST")
            val property = this::class.members.first { it.name == field.name }  as KMutableProperty1<Any, *>
            val key = standardizeName(field.name)

            if (key in parameters) {
                println("Setting value of property \"${field.name}\" to \"${parameters[key]}\"")
                property.setter.call(this, parameters[key])
            } else if (field.isAnnotationPresent(Optional::class.java)) {
                println("Setting value of property \"${field.name}\" to the default: \"${annotation.value}\"")
                property.setter.call(this, annotation.value)
            } else if (key != "UNKNOWNS") {
                throw IllegalArgumentException("Property \"${field.name}\" is required.")
            }
        }
    }
}
