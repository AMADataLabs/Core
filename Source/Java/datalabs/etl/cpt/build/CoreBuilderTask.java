package datalabs.etl.cpt.build;

import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Map;
import java.util.Properties;
import java.util.Scanner;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

import org.ama.dtk.Delimiter;
import org.ama.dtk.DtkAccess;
import org.ama.dtk.Exporter;
import org.ama.dtk.ExporterFiles;
import org.ama.dtk.core.BuildCore;
import org.ama.dtk.core.CoreDb;
import org.ama.dtk.core.CoreResourceDb;
import org.ama.dtk.core.DbParameters;
import org.ama.dtk.core.ConceptIdFactory;
import org.ama.dtk.model.DtkConcept;
import org.ama.dtk.model.PropertyType;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.zeroturnaround.zip.ZipUtil;

import datalabs.task.Task;
import datalabs.task.TaskException;


public class CoreBuilderTask extends Task {
    private static final Logger LOGGER = LoggerFactory.getLogger(CoreBuilderTask.class);
    Properties settings = null;

    public CoreBuilderTask(Map<String, String> parameters, ArrayList<byte[]> data)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        super(parameters, data, CoreBuilderParameters.class);
    }

    public ArrayList<byte[]> run() throws TaskException {
        ArrayList<byte[]> outputFiles;

        try {
            CoreBuilderParameters parameters = (CoreBuilderParameters) this.parameters;

            DbParameters dbParameters = new DbParameters(
                    parameters.host,
                    parameters.username,
                    parameters.password,
                    Integer.parseInt(parameters.port)
            );

            loadSettings();
            stageInputFiles();

            Path annualCorePath = Paths.get(
                    settings.getProperty("input.directory"),
                    settings.getProperty("annual.core.directory")
            );

            Path incrementalCorePath = Paths.get(
                    settings.getProperty("input.directory"),
                    settings.getProperty("incremental.core.directory")
            );

            DtkAccess annualCore = CoreBuilderTask.loadLink(annualCorePath.toString());
            DtkAccess incrementalCore = CoreBuilderTask.loadLink(incrementalCorePath.toString());

            CoreBuilderTask.updateConcepts(annualCore, incrementalCore);

            DtkAccess core = CoreBuilderTask.buildCore(incrementalCore, parameters.executionTime, dbParameters);

            CoreBuilderTask.exportConcepts(core, this.settings.getProperty("output.directory"));

            File outputFilesDirectory = new File(settings.getProperty("output.directory"));
            outputFiles = loadOutputFiles(outputFilesDirectory);

        } catch (Exception exception) {  // CPT Link code throws Exception, so we have no choice but to catch it
            throw new TaskException(exception);
        }

        return outputFiles;
    }

    void loadSettings(){
        String dataDirectory = System.getProperty("data.directory", "/tmp");

        settings = new Properties(){{
            put("output.directory", dataDirectory + File.separator + "output");
            put("input.directory", dataDirectory + File.separator + "input");
            put("annual.core.directory", "/annual_core");
            put("incremental.core.directory", "/incremental_core");
        }};
    }

    void stageInputFiles() throws IOException{
        Path annualCorePath = Paths.get(
                settings.getProperty("input.directory"),
                settings.getProperty("annual.core.directory")
        );
        Path incrementalCorePath = Paths.get(
                settings.getProperty("input.directory"),
                settings.getProperty("incremental.core.directory")
        );

        this.extractZipFiles(this.data.get(0), annualCorePath.toString());
        this.extractZipFiles(this.data.get(1), incrementalCorePath.toString());
    }

    private static DtkAccess loadLink(String directory) throws Exception {
        DtkAccess link = new DtkAccess();

        link.load(
            directory + "/" + ExporterFiles.PropertyInternal.getFileNameExt(),
            directory + "/" + ExporterFiles.RelationshipGroup.getFileNameExt()
        );

        return link;
	}

    private static void updateConcepts(DtkAccess annualCore, DtkAccess incrementalCore) throws IOException {
        for (DtkConcept concept : incrementalCore.getConcepts()) {
            if (concept.getProperty(PropertyType.CORE_ID) != null) {
                DtkConcept annualConcept = annualCore.getConcept(concept.getConceptId());

                if (annualCore != null) {
                    annualConcept.update(PropertyType.CORE_ID, concept.getProperty(PropertyType.CORE_ID));
                } else {
                    LOGGER.warn("Concept deleted: " + concept.getLogString());
                }
            }
        }
    }

    private static DtkAccess buildCore(DtkAccess incrementalCore, String releaseDate, DbParameters dbParameters)
            throws Exception {
        ConceptIdFactory.init(incrementalCore);

        return new BuildCore(incrementalCore, releaseDate).walk(dbParameters, dbParameters);
    }

    private static void exportConcepts(DtkAccess core, String outputDirectory) throws Exception {
        ArrayList<DtkConcept> concepts = CoreBuilderTask.getConcepts(core);

        Files.createDirectories(Paths.get(outputDirectory));

        Exporter exporter = new Exporter(core, outputDirectory);

        exporter.setDelimiter(Delimiter.Pipe);

        exporter.export(concepts, true);
    }

    private void extractZipFiles(byte[] zip, String directory) throws IOException{
        ByteArrayInputStream byteStream = new ByteArrayInputStream(zip);
        ZipInputStream zipStream = new ZipInputStream(byteStream);
        ZipEntry file = null;

        new File(directory).mkdirs();

        while((file = zipStream.getNextEntry())!=null) {
            this.writeZipEntryToFile(file, directory, zipStream);
        }
        zipStream.closeEntry();
        zipStream.close();
    }

    private static ArrayList<DtkConcept> getConcepts(DtkAccess link) {
        ArrayList<DtkConcept> concepts = link.getConcepts();

        DtkConcept.sort(concepts);

        return concepts;
    }

    private void writeZipEntryToFile(ZipEntry zipEntry, String directory, ZipInputStream stream) throws IOException{
        String fileName = zipEntry.getName();
        File file = new File(directory + File.separator + fileName);

        new File(file.getParent()).mkdirs();

        if (!zipEntry.isDirectory()){
            int bytesRead;
            byte[] data = new byte[1024];
            FileOutputStream fileOutputStream = new FileOutputStream(file);

            while ((bytesRead = stream.read(data, 0, data.length)) != -1) {
                fileOutputStream.write(data, 0, bytesRead);
            }
            fileOutputStream.close();
        }

    }

    ArrayList<byte[]> loadOutputFiles(File outputDirectory) throws Exception {
        ArrayList<byte[]> outputFile = new ArrayList<>();
        File zipFile = new File(outputDirectory + ".zip");
        ZipUtil.pack(outputDirectory, zipFile);

        byte[] byteInput = Files.readAllBytes(zipFile.toPath());
        outputFile.add(byteInput);

        return outputFile;
    }
}
