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
import java.util.Map;
import java.util.Properties;
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

import datalabs.task.Task;
import datalabs.task.TaskException;


public class CoreBuilderTask extends Task {
    private static final Logger LOGGER = LoggerFactory.getLogger(CoreBuilderTask.class);
    Properties settings = null;

    public CoreBuilderTask(Map<String, String> parameters, ArrayList<byte[]> data)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        super(parameters, null, CoreBuilderParameters.class);
    }

    public ArrayList<byte[]> run() throws TaskException {
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

            Path priorLinkPath = Paths.get(
                    settings.getProperty("input.directory"),
                    settings.getProperty("prior.link.directory")
            );
            Path currentLinkPath = Paths.get(
                    settings.getProperty("input.directory"),
                    settings.getProperty("current.link.directory")
            );

            DtkAccess priorLink = CoreBuilderTask.loadLink(priorLinkPath.toString());
            DtkAccess priorCore = CoreBuilderTask.loadLink(currentLinkPath.toString());

            CoreBuilderTask.updateConcepts(priorLink, priorCore);

            DtkAccess core = CoreBuilderTask.buildCore(priorLink, parameters.releaseDate, dbParameters);

            CoreBuilderTask.exportConcepts(core, this.settings.getProperty("output.directory"));
        } catch (Exception exception) {  // CPT Link code throws Exception, so we have no choice but to catch it
            throw new TaskException(exception);
        }

        return null;
    }

    private static DtkAccess loadLink(String directory) throws Exception {
        DtkAccess link = new DtkAccess();

        link.load(
            directory + "/" + ExporterFiles.PropertyInternal.getFileNameExt(),
            directory + "/" + ExporterFiles.RelationshipGroup.getFileNameExt()
        );

        return link;
	}

    private static void updateConcepts(DtkAccess priorLink, DtkAccess priorCore) throws IOException {
        for (DtkConcept concept : priorCore.getConcepts()) {
            if (concept.getProperty(PropertyType.CORE_ID) != null) {
                DtkConcept priorConcept = priorLink.getConcept(concept.getConceptId());

                if (priorConcept != null) {
                    priorConcept.update(PropertyType.CORE_ID, concept.getProperty(PropertyType.CORE_ID));
                } else {
                    LOGGER.warn("Concept deleted: " + concept.getLogString());
                }
            }
        }
    }

    private static DtkAccess buildCore(DtkAccess priorLink, String releaseDate, DbParameters dbParameters)
            throws Exception {
        ConceptIdFactory.init(priorLink);

        return new BuildCore(priorLink, releaseDate).walk(dbParameters, dbParameters);
    }

    private static void exportConcepts(DtkAccess core, String outputDirectory) throws Exception {
        ArrayList<DtkConcept> concepts = CoreBuilderTask.getConcepts(core);

        Files.createDirectories(Paths.get(outputDirectory));

        Exporter exporter = new Exporter(core, outputDirectory);

        exporter.setDelimiter(Delimiter.Pipe);

        exporter.export(concepts, true);
    }

    private static ArrayList<DtkConcept> getConcepts(DtkAccess link) {
        ArrayList<DtkConcept> concepts = link.getConcepts();

        DtkConcept.sort(concepts);

        return concepts;
    }

    private  void loadSettings(){
        settings = new Properties(){{
            put("output.directory", "./output/");
            put("input.directory", "./input");
            put("prior.link.directory", "/prior_link");
            put("current.link.directory", "/current_link");
        }};
    }

    private void stageInputFiles() throws IOException{
        Path priorLinkPath = Paths.get(
                settings.getProperty("input.directory"),
                settings.getProperty("prior.link.directory")
        );
        Path currentLinkPath = Paths.get(
                settings.getProperty("input.directory"),
                settings.getProperty("current.link.directory")
        );

        this.extractZipFiles(this.data.get(0), priorLinkPath.toString());
        this.extractZipFiles(this.data.get(1), currentLinkPath.toString());

    }

    private void extractZipFiles(byte[] zip, String directory) throws IOException{
        ByteArrayInputStream byteStream = new ByteArrayInputStream(zip);
        ZipInputStream zipStream = new ZipInputStream(byteStream);
        ZipEntry file = null;

        while((file = zipStream.getNextEntry())!=null) {
            this.writeZipEntryToFile(file, directory, zipStream);
        }
    }

    private void writeZipEntryToFile(ZipEntry zipEntry, String directory, ZipInputStream stream) throws IOException{
        byte[] data = new byte[(int) zipEntry.getSize()];
        String fileName = zipEntry.getName();
        File file = new File(directory + File.separator + fileName);
        FileOutputStream fileOutputStream = new FileOutputStream(file);

        new File(file.getParent()).mkdirs();


        while (stream.read(data, 0, data.length) > 0) {
            fileOutputStream.write(data, 0, data.length);
        }
        fileOutputStream.close();
    }

}
