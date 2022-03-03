// mvn compile
// mvn clean package shade:shade

package com.dro.samples.aws.lambda;
import com.amazonaws.services.lambda.runtime.Context;

public final class LambdaRequestHandler {
     public static String handleRequest(String arg, Context context) {
         return "The Maven compiled / packaged program has received your message, and its content is this: " + arg;
     }
 }