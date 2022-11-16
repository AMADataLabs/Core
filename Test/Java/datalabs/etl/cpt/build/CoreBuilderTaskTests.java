package datalabs.etl.cpt.build;

import java.io.*;
import java.lang.reflect.InvocationTargetException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

import org.apache.logging.log4j.core.util.ArrayUtils;
import org.apache.logging.log4j.core.util.Assert;

import org.apache.commons.io.FileUtils;
import org.junit.jupiter.api.io.TempDir;
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

import static org.junit.jupiter.api.Assertions.*;


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

        assertTrue(success);
    }

    @Test
    @DisplayName("Test loadOutputFiles return")
    void stageInputFilesTest(@TempDir Path DataDir, @TempDir Path WorkingDir) throws IOException, InvocationTargetException, IllegalAccessException, InstantiationException, NoSuchMethodException {
        String[] inputFiles = {"prior_link", "current_link"};
        System.getProperties().setProperty("data.directory", String.valueOf(DataDir));
        File inputDirectory = new File(WorkingDir+ File.separator + "input");
        ArrayList<byte[]> data = new ArrayList<byte[]>();

        inputDirectory.mkdirs();

        for (String fileToZip : inputFiles) {
            File zipFile = new File(inputDirectory + File.separator + fileToZip + ".zip");
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
        } catch (java.lang.Exception exception) {
            CoreBuilderTaskTests.LOGGER.info("Expected exception: " + exception.toString());
        }

        assertTrue(Files.exists(Paths.get(DataDir + File.separator + "input" + File.separator + "current_link")));
        assertTrue(Files.exists(Paths.get(DataDir + File.separator + "input" + File.separator + "prior_link")));

    }

    @Test
    @DisplayName("Test loadOutputFiles return")
    void loadOutputFilesTest(@TempDir Path OutputDirectory) throws InvocationTargetException, IllegalAccessException, InstantiationException, NoSuchMethodException {
        ArrayList<byte[]> data = new ArrayList<byte[]>();
        int index = 0;
        List<String> outputFileNames = Arrays.asList(
                "internal_Property.txt",
                "internal_Type.txt",
                "RelationshipGroup.txt"
        );

        Map<String, String> parameters = new HashMap();
        parameters.put("releaseDate", "20230101");
        parameters.put("host", "host");
        parameters.put("username", "username");
        parameters.put("password", "password");
        parameters.put("port", "port");
        ArrayList<byte[]>byteData = new ArrayList<byte[]>();

        CoreBuilderTask coreBuilderTask = new CoreBuilderTask(parameters, data);
        coreBuilderTask.loadSettings();

        try {
            byteData = coreBuilderTask.loadOutputFiles(new File("output"));
            for (byte[] file: byteData){
                Files.write(
                        Paths.get(OutputDirectory + File.separator + "output" + File.separator + outputFileNames.get(index)),
                        file);
                index++;
            }

            for (String name: outputFileNames){
                assertTrue(byteData.size() > 0);
                assertTrue(Files.exists(
                        Paths.get(OutputDirectory + File.separator + "output" + File.separator + name)
                ));
                assertTrue(FileUtils.contentEquals(
                        new File(OutputDirectory + File.separator + "output" + File.separator + name),
                        new File("output" + File.separator + name))
                );
                assertTrue(new File(OutputDirectory + File.separator + "output" + File.separator + name).length() > 0);
            }

        } catch (Exception exception) {
            CoreBuilderTaskTests.LOGGER.info("Expected exception: " + exception.toString());
        }
    }
}
