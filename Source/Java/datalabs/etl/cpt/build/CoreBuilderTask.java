package datalabs.etl.cpt.build;

import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Map;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

import org.ama.dtk.Delimiter;
import org.ama.dtk.DtkAccess;
import org.ama.dtk.Exporter;
import org.ama.dtk.ExporterFiles;
import org.ama.dtk.core.BuildCore;
import org.ama.dtk.core.ConceptIdFactory;
import org.ama.dtk.model.DtkConcept;
import org.ama.dtk.model.PropertyType;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import datalabs.task.Task;
import datalabs.task.TaskException;


public class CoreBuilderTask extends Task {
    private static final Logger LOGGER = LoggerFactory.getLogger(CoreBuilderTask.class);

    public CoreBuilderTask(Map<String, String> parameters)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        super(parameters);
    }

    public void run() throws TaskException {
        try {
            CoreBuilderParameters parameters = (CoreBuilderParameters) this.parameters;
            stageInputFiles();
            DtkAccess priorLink = CoreBuilderTask.loadLink("./prior_link_data/");
            DtkAccess priorCore = CoreBuilderTask.loadLink("./current_link_data/");

            CoreBuilderTask.updateConcepts(priorLink, priorCore);

            DtkAccess core = CoreBuilderTask.buildCore(priorLink, parameters.releaseDate);

            CoreBuilderTask.exportConcepts(core, parameters.outputDirectory);
        } catch (Exception exception) {  // CPT Link code throws Exception, so we have no choice but to catch it
            throw new TaskException(exception);
        }
    }

    private static DtkAccess loadLink(String directory) throws Exception {
        DtkAccess link = new DtkAccess();

        link.load(
            directory + ExporterFiles.PropertyInternal.getFileNameExt(),
            directory + ExporterFiles.RelationshipGroup.getFileNameExt()
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

    private static DtkAccess buildCore(DtkAccess priorLink, String releaseDate) throws Exception {
        ConceptIdFactory.init(priorLink);

        return new BuildCore(priorLink, releaseDate).walk();
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

    private static void stageInputFiles(){
        this.extract_zip_files(this.data.get(0), "./prior_link_data");
        this.extract_zip_files(this.data.get(1), "./current_link_data");
    }

    private void extract_zip_files(byte[] zip, String directory) {
        ByteArrayInputStream byteStream = new ByteArrayInputStream(zip);
        ZipInputStream zipStream = new ZipInputStream(byteStream);

        while(zipStream.available()) {
            file = zipStream.getNextEntry();

            this.write_zip_entry_to_file(file, directory)
        }
    }

    private void write_zip_entry_to_file(ZipEntry file, String directory) {
        int length = file.getSize();
        byte[] data = new byte[length];

        file.read(data, 0, length);
        String fileName = file.getName();
        File newFile = new File(directory + File.separator + fileName);
        new File(newFile.getParent()).mkdirs();
        FileOutputStream fileOutputStream = new FileOutputStream(newFile);

        while (length > 0) {
            fos.write(data, 0, data);
        }

        fileOutputStream.close();
    }

}
