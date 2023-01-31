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
        String[] testFiles = {"testFile1.txt", "testFile2.txt", "testFile3.txt"};
        String[] testDirectories = {"current_core", "incremental_core", "annual_core", "prior_link"};
        String[] testInputFiles = {"HCPCS.xlsx", "cdcterms.xlsx", "coding_tips_attach.xlsx", "front_matter.docx",
                "cpt_rvu.txt", "cpt_index.docx", "reviewed_used_input.xlsx"};
        ArrayList<byte[]> data = new ArrayList<>();

        generateInputZipFiles(testDirectories, data, workingDir, testFiles);
        generateOtherInputFiles(testInputFiles, data, workingDir);

        stageInputFiles(dataDir, data);

        assertZipInputsMatch(dataDir, workingDir, testDirectories, testFiles);
        assertOtherInputsMatch(testInputFiles, workingDir, dataDir);
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

            byte[] byteInput = Files.readAllBytes(
                    new File(workingDir + File.separator + "input" + File.separator + file).toPath()
            );
            data.add(byteInput);

        }
    }

    void stageInputFiles(Path dataDir, ArrayList<byte[]> data) throws InvocationTargetException, IllegalAccessException, InstantiationException, NoSuchMethodException {
        System.getProperties().setProperty("data.directory", String.valueOf(dataDir));

        Map<String, String> parameters = new HashMap();
        parameters.put("hcpsTerminationDate", "20220101");
        parameters.put("linkDate", "2023");
        parameters.put("linkIncrementalDate", "2022u05");
        parameters.put("linkAnnualDate", "2022");
        parameters.put("revisionDate", "20230101");

        LinkBuilderTask linkBuilderTask = new LinkBuilderTask(parameters, data);
        linkBuilderTask.loadSettings();

        try {
            linkBuilderTask.stageInputFiles();
        } catch (java.lang.Exception exception) {
            LinkBuilderTaskTests.LOGGER.info("Expected exception: " + exception.toString());
        }
    }

    void assertZipInputsMatch(Path dataDir, Path workingDir, String[] testDirectories, String[] testFiles) throws IOException {
        for (String directory : testDirectories) {
            LOGGER.info("Path: " + dataDir + File.separator + "input" + File.separator + directory);
            assertTrue(Files.exists(
                    Paths.get(dataDir + File.separator + "input" + File.separator + directory)
            ));

            for (String testFile : testFiles) {
                assertEquals(
                        Files.readString(new File(workingDir + File.separator + "input" + File.separator + directory + File.separator + testFile).toPath()).trim(),
                        Files.readString(new File(dataDir + File.separator + "input" + File.separator + directory + File.separator + testFile).toPath()).trim()
                );
            }
        }
    }

    void assertOtherInputsMatch(String[] testInputFiles, Path workingDir, Path dataDir) throws IOException {
        for (String testInput : testInputFiles){
            assertEquals(
                    Files.readString(new File(workingDir + File.separator + "input" + File.separator + testInput).toPath()).trim(),
                    Files.readString(new File(dataDir + File.separator + "input" + File.separator + testInput).toPath()).trim()
            );
        }
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
        ArrayList<byte[]> returnedData = loadOutputFiles(dataDir, data, dataOutputDirectory);

        assertOutputFilesMatch(returnedData, expectedData);
    }

    // FIXME
    // void generateOutputFiles(File dataOutputDirectory, List<String> testSubDirectories, List<String> testFiles, Path dataDir, ArrayList<byte[]> expectedData)
    //         throws IOException {
    //     dataOutputDirectory.mkdirs();
    //
    //     for (String testDirectory: testSubDirectories){
    //         File directory = new File(dataDir + File.separator + "output" + File.separator + testDirectory);
    //         directory.mkdirs();
    //
    //         for (String testFile: testFiles) {
    //             FileWriter fileWriter = new FileWriter(directory + File.separator + testFile);
    //             BufferedWriter bufferedWriter = new BufferedWriter(fileWriter);
    //             bufferedWriter.write("content for " + testFile);
    //             bufferedWriter.close();
    //             byte[] bytes = Files.readAllBytes(new File(directory + File.separator + testFile).toPath());
    //             expectedData.add(bytes);
    //         }
    //     }
    // }
    //
    // ArrayList<byte[]> loadOutputFiles(Path dataDir, ArrayList<byte[]> data, File dataOutputDirectory){
    //     System.getProperties().setProperty("data.directory", String.valueOf(dataDir));
    //
    //     Map<String, String> parameters = new HashMap();
    //     parameters.put("releaseDate", "20230101");
    //     parameters.put("host", "host");
    //     parameters.put("username", "username");
    //     parameters.put("password", "password");
    //     parameters.put("port", "port");
    //     ArrayList<byte[]>returnedData = new ArrayList<byte[]>();
    //
    //     try {
    //         CoreBuilderTask coreBuilderTask = new CoreBuilderTask(parameters, data);
    //         coreBuilderTask.loadSettings();
    //         returnedData = coreBuilderTask.loadOutputFiles(dataOutputDirectory);
    //     } catch (Exception exception) {
    //         CoreBuilderTaskTests.LOGGER.info("Expected exception: " + exception.toString());
    //     }
    //
    //     return returnedData;
    // }
    //
    // void assertOutputFilesMatch(ArrayList<byte[]> returnedData, ArrayList<byte[]> expectedData){
    //     for (int i = 0; i < returnedData.size(); i++){
    //         assertArrayEquals(returnedData.get(i), expectedData.get(i));
    //     }
    // }
}
