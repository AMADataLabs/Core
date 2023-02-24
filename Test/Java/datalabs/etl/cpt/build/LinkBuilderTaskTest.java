package datalabs.etl.cpt.build;

import java.io.BufferedWriter;
import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.List;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

import org.apache.logging.log4j.core.util.ArrayUtils;
import org.apache.commons.io.FileUtils;
import org.junit.Assert;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.MethodOrderer.OrderAnnotation;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;
import org.junit.jupiter.api.io.TempDir;
import org.junit.jupiter.api.condition.EnabledIfSystemProperty;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.zeroturnaround.zip.ZipUtil;
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
    throws IOException, InvocationTargetException, IllegalAccessException, InstantiationException, NoSuchMethodException {
        ArrayList<byte[]> data = new ArrayList<>();
        ArrayList<byte[]> expectedData = new ArrayList<byte[]>();
        String datestamp = ZonedDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"));
        ArrayList<String> testSubDirectories = new ArrayList<String>() {{
            add("publish" + datestamp + "_112233");
            add("build" + datestamp + "_112233");
            add("export");
        }};
        List<String> testFiles = Arrays.asList("testFile1.txt", "testFile2.txt", "testFile3.txt");
        Path dataOutputDirectory = dataDir.resolve("output");

        generateOutputFiles(dataOutputDirectory, testSubDirectories, testFiles, dataDir);
        ls(dataDir);
        ls(dataDir.resolve("output"));
        ArrayList<byte[]> outputs = loadOutputFiles(dataDir, data);

        assertEquals(1, outputs.size());
        assertZippedOutputsMatch(outputs.get(0), testSubDirectories.subList(0, 2), testFiles);
    }

    @Test
    @DisplayName("Test determination of the publish path")
    void getPublishPathTest(@TempDir Path dataDir)
            throws IOException, InvocationTargetException, IllegalAccessException, InstantiationException, NoSuchMethodException {
        System.setProperty("data.path", String.valueOf(dataDir));
        String timestamp = ZonedDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));
        Files.createDirectories(dataDir.resolve("output").resolve("publish" + timestamp));
        Map<String, String> parameters = new HashMap() {{
            put("EXECUTION_TIME", "2023-09-01T00:00:00");
        }};

        LinkBuilderTask linkBuilderTask = new LinkBuilderTask(parameters, new ArrayList<byte[]>());
        LOGGER.info("Expected Publish Path: " + dataDir.resolve("output").resolve("publish20230901_112233").toString());

        Path publishPath = linkBuilderTask.getPublishPath();
        LOGGER.info("Actual Publish Path: " + publishPath.toString());

        assertTrue(publishPath.toString().startsWith(dataDir.resolve("output").resolve("publish").toString()));
    }

    @Test
    @DisplayName("Test determination of the build path")
    void getBuildPathTest(@TempDir Path dataDir)
            throws IOException, InvocationTargetException, IllegalAccessException, InstantiationException, NoSuchMethodException {
        System.setProperty("data.path", String.valueOf(dataDir));
        String timestamp = ZonedDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));
        Files.createDirectories(dataDir.resolve("output").resolve("build" + timestamp));
        Map<String, String> parameters = new HashMap() {{
            put("EXECUTION_TIME", "2023-09-01T00:00:00");
        }};

        LinkBuilderTask linkBuilderTask = new LinkBuilderTask(parameters, new ArrayList<byte[]>());
        LOGGER.info("Expected Build Path: " + dataDir.resolve("output").resolve("build" + timestamp).toString());

        Path buildPath = linkBuilderTask.getBuildPath();
        LOGGER.info("Actual Build Path: " + buildPath.toString());

        assertTrue(buildPath.toString().startsWith(dataDir.resolve("output").resolve("build").toString()));
    }

    @Test
    @DisplayName("Test for checking folder name change")
    void renameFolderToLinkTest(@TempDir Path dataDir)
            throws IOException, InvocationTargetException, IllegalAccessException, InstantiationException, NoSuchMethodException {

        System.setProperty("data.path", String.valueOf(dataDir));

        Map<String, String> parameters = new HashMap() {{
            put("EXECUTION_TIME", "2023-09-01T00:00:00");
        }};
        String datestamp = ZonedDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"));
        ArrayList<String> testSubDirectories = new ArrayList<String>() {{
            add("publish" + datestamp + "_112233");
            add("build" + datestamp + "_112233");
            add("export");
        }};
        List<String> testFiles = Arrays.asList("dtk", "testFile2.txt", "testFile3.txt");
        Path dataOutputDirectory = dataDir.resolve("output");

        generateOutputFiles(dataOutputDirectory, testSubDirectories, testFiles, dataDir);

        LinkBuilderTask linkBuilderTask = new LinkBuilderTask(parameters, new ArrayList<byte[]>());

        linkBuilderTask.renameFolderToLink();

        assertTrue(Files.exists(Path.of(dataOutputDirectory + File.separator + "publish" + datestamp + "_112233" + File.separator + "CPT Link")));
    }

    void generateInputZipFiles(String[] testDirectories, ArrayList<byte[]> data, Path workingDir, String[] testFiles)
            throws IOException {
        for (String directory : testDirectories) {
            File testDirectory = new File(workingDir.resolve("input").resolve(directory).toString());
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

    void stageInputFiles(Path dataDir, ArrayList<byte[]> data)
            throws InvocationTargetException, IllegalAccessException, InstantiationException, NoSuchMethodException {
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

    void generateOutputFiles(Path dataOutputDirectory, List<String> testSubDirectories, List<String> testFiles, Path dataDir)
            throws IOException {
        dataOutputDirectory.toFile().mkdirs();

        for (String testDirectory: testSubDirectories){
            Path directory = dataOutputDirectory.resolve(testDirectory);

            directory.toFile().mkdirs();

            for (String testFilename: testFiles) {
                Path testFilePath = directory.resolve(testFilename);
                FileWriter fileWriter = new FileWriter(testFilePath.toFile());
                BufferedWriter bufferedWriter = new BufferedWriter(fileWriter);

                bufferedWriter.write("content for " + testFilename);
                bufferedWriter.close();

                byte[] bytes = Files.readAllBytes(testFilePath);
            }
        }
    }

    ArrayList<byte[]> loadOutputFiles(Path dataDir, ArrayList<byte[]> data)
            throws IOException, InvocationTargetException, IllegalAccessException, InstantiationException, NoSuchMethodException {
        System.getProperties().setProperty("data.path", String.valueOf(dataDir));

        Map<String, String> parameters = new HashMap() {{
            put("EXECUTION_TIME", "2023-09-01T00:00:00");
        }};

        LinkBuilderTask linkBuilderTask = new LinkBuilderTask(parameters, data);

        return linkBuilderTask.loadOutputFiles();
    }

    void assertZippedOutputsMatch(byte[] outputZip, List<String> expectedDirectories, List<String> expectedFiles) throws IOException {
        ZipInputStream zipStream = new ZipInputStream(new ByteArrayInputStream(outputZip));
        List<Path> expectedPaths = generateExpectedOutputPaths(expectedDirectories, expectedFiles);
        int matchCount = 0;
        ZipEntry zipEntry = null;

        while((zipEntry = zipStream.getNextEntry()) != null) {
            LOGGER.info("Zip entry name: " + zipEntry.getName());
            if (expectedPaths.contains(Paths.get(zipEntry.getName()))) {
                matchCount += 1;
            }
        }
        assertEquals(expectedPaths.size(), matchCount);
    }

    void ls(Path directory) throws IOException {
        LOGGER.info("Files in " + directory.toString() + ":");
        try (DirectoryStream<Path> listing = Files.newDirectoryStream(directory)) {
            for (Path path : listing) {
                if (Files.isDirectory(path)) {
                    System.out.println(path.toString() + "/");
                } else {
                    System.out.println(path.toString());
                }
            }
        }
    }
    List<Path> generateExpectedOutputPaths(List<String> expectedDirectories, List<String> expectedFiles) throws IOException {
        ArrayList<Path> expectedOutputPaths = new ArrayList<Path>();
        for (String directory : expectedDirectories) {
            expectedOutputPaths.add(Paths.get(directory));

            for (String file: expectedFiles) {
                expectedOutputPaths.add(Paths.get(directory, file));
            }
        }

        return expectedOutputPaths;
    }
}
