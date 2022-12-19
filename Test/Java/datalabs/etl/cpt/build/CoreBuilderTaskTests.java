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

import org.apache.commons.io.FileUtils;
import org.junit.jupiter.api.io.TempDir;
import org.zeroturnaround.zip.ZipUtil;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.junit.Assert;
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
    @DisplayName("Test stageOutputFiles return")
    void stageInputFilesTest(@TempDir Path dataDir, @TempDir Path workingDir) throws IOException, InvocationTargetException, IllegalAccessException, InstantiationException, NoSuchMethodException {
        String[] testFiles = {"testFile1.txt", "testFile2.txt", "testFile3.txt"};
        String[] testDirectories = {"prior_link", "current_link"};
        ArrayList<byte[]> data = new ArrayList<>();

        for (String directory: testDirectories) {
            File linkDirectory = new File(workingDir + File.separator + "input" + File.separator + directory);
            linkDirectory.mkdirs();

            for (String testFile: testFiles) {
                FileWriter FileWriter = new FileWriter(linkDirectory + File.separator + testFile);
                BufferedWriter bufferedWriter = new BufferedWriter(FileWriter);
                bufferedWriter.write("content for " + testFile);
                bufferedWriter.close();
            }

            File zipFile = new File(linkDirectory + ".zip");
            System.out.println(zipFile);
            ZipUtil.pack(linkDirectory, zipFile);
            byte[] byteInput = Files.readAllBytes(zipFile.toPath());
            data.add(byteInput);
        }

        System.getProperties().setProperty("data.directory", String.valueOf(dataDir));

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

        for (String directory: testDirectories){
            assertTrue(Files.exists(
                    Paths.get(dataDir + File.separator + "input" + File.separator + directory)
            ));

            for (String testFile: testFiles){
                assertEquals(
                        Files.readString(new File(workingDir + File.separator + "input" + File.separator + directory + File.separator + testFile).toPath()).trim(),
                        Files.readString(new File(dataDir + File.separator + "input" + File.separator + directory + File.separator + testFile).toPath()).trim()
                );
            }
        }

    }

    @Test
    @DisplayName("Test loadOutputFiles return")
    void loadOutputFilesTest(@TempDir Path dataDir)
            throws InvocationTargetException, IllegalAccessException, InstantiationException, NoSuchMethodException,
            IOException {
        ArrayList<byte[]> data = new ArrayList<>();
        ArrayList<byte[]>expectedData = new ArrayList<byte[]>();
        List<String> testFiles = Arrays.asList("testFile1.txt", "testFile2.txt", "testFile3.txt");
        File dataOutputDirectory = new File(dataDir + File.separator + "output");

        dataOutputDirectory.mkdirs();

        System.getProperties().setProperty("data.directory", String.valueOf(dataDir));

        for (String testFile: testFiles) {
            FileWriter fileWriter = new FileWriter(dataOutputDirectory + File.separator + testFile);
            BufferedWriter bufferedWriter = new BufferedWriter(fileWriter);
            bufferedWriter.write("content for " + testFile);
            bufferedWriter.close();
            byte[] bytes = Files.readAllBytes(new File(dataOutputDirectory + File.separator + testFile).toPath());
            expectedData.add(bytes);
        }

        Map<String, String> parameters = new HashMap();
        parameters.put("releaseDate", "20230101");
        parameters.put("host", "host");
        parameters.put("username", "username");
        parameters.put("password", "password");
        parameters.put("port", "port");
        ArrayList<byte[]>returnedData = new ArrayList<byte[]>();

        try {
            CoreBuilderTask coreBuilderTask = new CoreBuilderTask(parameters, data);
            coreBuilderTask.loadSettings();
            returnedData = coreBuilderTask.loadOutputFiles(dataOutputDirectory);

            for (int i = 0; i < returnedData.size(); i++){
                CoreBuilderTaskTests.LOGGER.debug("Expected \"" + new String(expectedData.get(i)) + "\".");
                CoreBuilderTaskTests.LOGGER.debug("Actual \"" + new String(returnedData.get(i)) + "\".");
                // assertTrue(Arrays.equals(returnedData.get(i), expectedData.get(i)));
            }

        } catch (Exception exception) {
            CoreBuilderTaskTests.LOGGER.info("Expected exception: " + exception.toString());
        }
    }
}
