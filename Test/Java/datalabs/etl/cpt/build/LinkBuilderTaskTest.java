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


class LinkBuilderTaskTests {
    protected static final Logger LOGGER = LoggerFactory.getLogger(LinkBuilderTaskTests.class);

    @BeforeEach
    void beforeEach() {
    }

    @Test
    @DisplayName("Test stageOutputFiles return")
    void stageInputFilesTest(@TempDir Path dataDir, @TempDir Path workingDir)
            throws IOException, InvocationTargetException, IllegalAccessException, InstantiationException, NoSuchMethodException {
        System.setProperty("data.path", String.valueOf(dataDir));
        LOGGER.info("Set data.path to " + System.getProperty("data.path"));
        String[] testFiles = {"testFile1.txt", "testFile2.txt", "testFile3.txt"};
        String[] testDirectories = {"annual_core", "incremental_core", "current_core", "prior_link"};
        String[] testInputFiles = {"HCPCS.xlsx", "cdcterms.xlsx", "coding_tips_attach.xlsx", "front_matter.docx",
                "cpt_rvu.txt", "cpt_index.docx", "reviewed_used_input.xlsx"};
        ArrayList<byte[]> data = new ArrayList<>();

        generateInputZipFiles(testDirectories, data, workingDir, testFiles);
        generateOtherInputFiles(testInputFiles, data, workingDir);

        stageInputFiles(dataDir, data);

        assertZipInputsMatch(dataDir, workingDir, testDirectories, testFiles);
        assertOtherInputsMatch(testInputFiles, workingDir, dataDir);
    }


    @Test
    @DisplayName("Test loadOutputFiles return")
    void loadOutputFilesTest(@TempDir Path dataDir)
            throws IOException {
        ArrayList<byte[]> data = new ArrayList<>();
        ArrayList<byte[]> expectedData = new ArrayList<byte[]>();
        List<String> testSubDirectories = Arrays.asList("testDirectory1", "testDirectory2", "testDirectory3");
        List<String> testFiles = Arrays.asList("testFile1.txt", "testFile2.txt", "testFile3.txt");
        File dataOutputDirectory = new File(dataDir + File.separator + "output");

        generateOutputFiles(dataOutputDirectory, testSubDirectories, testFiles, dataDir, expectedData);
        ArrayList<byte[]> returnedData = loadFiles(dataDir, data, dataOutputDirectory);

        assertOutputFilesMatch(returnedData, expectedData);
    }


    @Test
    @DisplayName("Test determination of the publish path")
    void getPublishPathTest(@TempDir Path dataDir)
            throws IOException, InvocationTargetException, IllegalAccessException, InstantiationException, NoSuchMethodException {
        System.setProperty("data.path", String.valueOf(dataDir));
        Files.createDirectories(dataDir.resolve("output").resolve("publish20230131_11223344"));
        Map<String, String> parameters = new HashMap() {{
            put("EXECUTION_TIME", "2023-09-01T00:00:00");
        }};

        LinkBuilderTask linkBuilderTask = new LinkBuilderTask(parameters, new ArrayList<byte[]>());

        Path publishPath = linkBuilderTask.getPublishPath();

        LOGGER.info("Actual Publish Path: " + publishPath.toString());
        LOGGER.info("Expected Publish Path Prefix: " + dataDir.resolve("output").toString() + "publish"));
        assertTrue(publishPath.toString().startsWith(dataDir.resolve("output").toString() + "publish"));
    }


    void generateInputZipFiles(String[] testDirectories, ArrayList<byte[]> data, Path workingDir, String[] testFiles)
            throws IOException {
        for (String directory : testDirectories) {
            File testDirectory = new File(workingDir + File.separator + "input" + File.separator + directory);
            testDirectory.mkdirs();

            for (String testFile : testFiles) {
                FileWriter FileWriter = new FileWriter(testDirectory + File.separator + testFile);
                BufferedWriter bufferedWriter = new BufferedWriter(FileWriter);
                bufferedWriter.write("content for " + testFile);
                bufferedWriter.close();
            }

            File zipFile = new File(testDirectory + ".zip");
            ZipUtil.pack(testDirectory, zipFile);
            byte[] byteInput = Files.readAllBytes(zipFile.toPath());
            data.add(byteInput);
        }
    }


    void generateOtherInputFiles(String[] testInputFiles, ArrayList<byte[]> data, Path workingDir) throws IOException {
        for (String file: testInputFiles){
            FileWriter FileWriter = new FileWriter(workingDir + File.separator + "input" + File.separator + file);
            BufferedWriter bufferedWriter = new BufferedWriter(FileWriter);
            bufferedWriter.write("content for " + file);
            bufferedWriter.close();

            byte[] byteInput = Files.readAllBytes(workingDir.resolve("input").resolve(file));
            data.add(byteInput);
        }
    }


    void stageInputFiles(Path dataDir, ArrayList<byte[]> data) throws InvocationTargetException, IllegalAccessException, InstantiationException, NoSuchMethodException {
        Map<String, String> parameters = new HashMap() {{
            put("EXECUTION_TIME", "2023-09-01T00:00:00");
        }};

        LinkBuilderTask linkBuilderTask = new LinkBuilderTask(parameters, data);

        try {
            linkBuilderTask.stageInputFiles();
        } catch (java.lang.Exception exception) {
            LinkBuilderTaskTests.LOGGER.info("Expected exception: " + exception.toString());
        }
    }


    void assertZipInputsMatch(Path dataDir, Path workingDir, String[] testDirectories, String[] testFiles) throws IOException {
        for (String directory : testDirectories) {
            LOGGER.info("Data Path: " + dataDir.resolve("input").resolve(directory));
            assertTrue(Files.exists(dataDir.resolve("input").resolve(directory)));

            for (String testFile : testFiles) {
                assertEquals(
                        Files.readString(workingDir.resolve("input").resolve(directory).resolve(testFile)).trim(),
                        Files.readString(dataDir.resolve("input").resolve(directory).resolve(testFile)).trim()
                );
            }
        }
    }


    void assertOtherInputsMatch(String[] testInputFiles, Path workingDir, Path dataDir) throws IOException {
        for (String filename : testInputFiles){
            LOGGER.info("Working File Path: " + workingDir.resolve("input").resolve(filename).toString());
            LOGGER.info("Staged File Path: " + dataDir.resolve("input").resolve(filename).toString());
            String workingFileContent = Files.readString(workingDir.resolve("input").resolve(filename)).trim();
            String stagedFileContent = Files.readString(dataDir.resolve("input").resolve(filename)).trim();

            LOGGER.info("Working File Content: " + workingFileContent);
            LOGGER.info("Staged File Content: " + stagedFileContent);
            assertEquals(workingFileContent, stagedFileContent);
        }
    }


    void generateOutputFiles(File dataOutputDirectory, List<String> testSubDirectories, List<String> testFiles, Path dataDir, ArrayList<byte[]> expectedData)
            throws IOException {
        dataOutputDirectory.mkdirs();

        for (String testDirectory: testSubDirectories){
            File directory = new File(dataDir + File.separator + "output" + File.separator + testDirectory);
            directory.mkdirs();

            for (String testFile: testFiles) {
                FileWriter fileWriter = new FileWriter(directory + File.separator + testFile);
                BufferedWriter bufferedWriter = new BufferedWriter(fileWriter);
                bufferedWriter.write("content for " + testFile);
                bufferedWriter.close();
                byte[] bytes = Files.readAllBytes(new File(directory + File.separator + testFile).toPath());
                expectedData.add(bytes);
            }
        }
    }


    ArrayList<byte[]> loadFiles(Path dataDir, ArrayList<byte[]> data, File dataOutputDirectory){
        System.getProperties().setProperty("data.directory", String.valueOf(dataDir));

        Map<String, String> parameters = new HashMap() {{
            put("EXECUTION_TIME", "2023-09-01T00:00:00");
        }};
        ArrayList<byte[]> returnedData = new ArrayList<byte[]>();

        try {
            LinkBuilderTask linkBuilderTask = new LinkBuilderTask(parameters, data);
            returnedData = linkBuilderTask.loadOutputFiles();
        } catch (Exception exception) {
            LinkBuilderTaskTests.LOGGER.info("Expected exception: " + exception.toString());
        }

        return returnedData;
    }


    void assertOutputFilesMatch(ArrayList<byte[]> returnedData, ArrayList<byte[]> expectedData){
        for (int i = 0; i < returnedData.size(); i++){
            assertArrayEquals(returnedData.get(i), expectedData.get(i));
        }
    }
}
