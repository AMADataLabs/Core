package datalabs.etl.cpt.build;

import java.io.*;
import java.lang.reflect.InvocationTargetException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

import org.apache.logging.log4j.core.util.ArrayUtils;
import org.junit.Assert;
import org.apache.commons.io.FileUtils;
import org.zeroturnaround.zip.ZipUtil;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.MethodOrderer.OrderAnnotation;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;
import org.junit.jupiter.api.condition.EnabledIfSystemProperty;
import software.amazon.awssdk.services.dynamodb.model.DynamoDbException;

import org.ama.dtk.DtkAccess;
import datalabs.etl.dag.notify.sns.DagNotifier;


class CoreBuilderTaskTests {
    protected static final Logger LOGGER = LoggerFactory.getLogger(CoreBuilderTaskTests.class);

    @BeforeEach
    void beforeEach() {
    }

    @Test
    @DisplayName("Test DtkAccess.load() will throw an exception if the file arguments are invalid.")
    void dtkAccessLoadThrowsExceptionForInvalidFilePaths() {
        DtkAccess link = new DtkAccess();
        boolean success = false;

        try {
            link.load("bogus/path", "fake/path");
        } catch (java.lang.Exception exception) {
            CoreBuilderTaskTests.LOGGER.info("Expected exception: " + exception.toString());
            success = true;
        }

        Assertions.assertTrue(success);
    }

    @Test
    @DisplayName("Test loadOutputFiles return")
    void stageInputFilesTest() throws IOException, InvocationTargetException, IllegalAccessException, InstantiationException, NoSuchMethodException {
        String[] inputFiles = {"input/prior_link", "input/current_link"};
        boolean success = false;
        ArrayList<byte[]> data = new ArrayList<byte[]>();

        for (String fileToZip : inputFiles) {
            File zipFile = new File(fileToZip + ".zip");
            ZipUtil.pack(new File(fileToZip), zipFile);
            byte[] byteInput = Files.readAllBytes(zipFile.toPath());
            data.add(byteInput);
        }

        Map<String, String> parameters = new HashMap();
        parameters.put("releaseDate", "20230101");
        parameters.put("host", "host");
        parameters.put("username", "username");
        parameters.put("password", "password");
        parameters.put("port", "port");

        CoreBuilderTask coreBuilderTask = new CoreBuilderTask(parameters, data);
        coreBuilderTask.loadSettings();

        try {
            coreBuilderTask.stageInputFiles();
            success = true;
        } catch (java.lang.Exception exception) {
            CoreBuilderTaskTests.LOGGER.info("Expected exception: " + exception.toString());
        }


        Assertions.assertTrue(success);
    }

    @Test
    @DisplayName("Test loadOutputFiles return")
    void loadOutputFilesTest() throws InvocationTargetException, IllegalAccessException, InstantiationException, NoSuchMethodException {
        ArrayList<byte[]> data = new ArrayList<byte[]>();
        int index = 0;
        List<String> outputFileNames = new ArrayList<String>() {{
            add("internal_Property.txt");
            add("internal_Type.txt");
            add("RelationshipGroup.txt");
        } };

        Map<String, String> parameters = new HashMap();
        parameters.put("releaseDate", "20230101");
        parameters.put("host", "host");
        parameters.put("username", "username");
        parameters.put("password", "password");
        parameters.put("port", "port");
        ArrayList<byte[]>byteData = new ArrayList<byte[]>();
        File output = new File("output");

        CoreBuilderTask coreBuilderTask = new CoreBuilderTask(parameters, data);
        coreBuilderTask.loadSettings();

        try {
            byteData = coreBuilderTask.loadOutputFiles(output);
            for (byte[] file: byteData){
                Files.write(Paths.get(outputFileNames.get(index)) , file);
                index++;
            }

            Assert.assertEquals(FileUtils.readLines(new File("output/RelationshipGroup.txt")),
                    FileUtils.readLines(new File("RelationshipGroup.txt"))
            );
            Assert.assertEquals(FileUtils.readLines(new File("output/internal_Property.txt")),
                    FileUtils.readLines(new File("internal_Property.txt"))
            );
            Assert.assertEquals(FileUtils.readLines(new File("output/internal_Type.txt")),
                    FileUtils.readLines(new File("internal_Type.txt"))
            );
        } catch (java.lang.Exception exception) {
            CoreBuilderTaskTests.LOGGER.info("Expected exception: " + exception.toString());
        }
    }
}
