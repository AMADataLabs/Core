package datalabs.etl.cpt.build;

import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Map;

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


public class CoreBuilderTask extends Task {
    private static final Logger logger = LoggerFactory.getLogger(CoreBuilderTask.class);

    public final Path outputDirectory = Paths.get(((CoreBuilderTaskParameters) this.parameters).outputDirectory);

    public CoreBuilderTask(Map<String, String> parameters) throws IllegalAccessException, InstantiationException,
            InvocationTargetException, NoSuchMethodException {
        super(parameters);
    }

    public void run() {
        DtkAccess priorDtk = null;
        try {
            priorDtk = CoreBuilderTask.loadDtk("dtk-versions/" +
                    ((CoreBuilderTaskParameters) this.parameters).priorDtkVersion +
                    "/"
            );
            updateConcepts(priorDtk);

            ConceptIdFactory.init(priorDtk);
            DtkAccess dtk = new BuildCore(priorDtk, ((CoreBuilderTaskParameters) this.parameters).releaseDate).walk();
            ArrayList<DtkConcept> concepts = dtk.getConcepts();
            DtkConcept.sort(concepts);
            exportConcepts(dtk, concepts);

        } catch (IOException exception) {
            exception.printStackTrace();
        }
    }

	private static DtkAccess loadDtk(String directory) throws IOException {
		DtkAccess dtk = new DtkAccess();

        try {
            dtk.load(directory + ExporterFiles.PropertyInternal.getFileNameExt(),
                    directory + ExporterFiles.RelationshipGroup.getFileNameExt()
            );
        } catch (Exception e) {
            e.printStackTrace();
        }

        return dtk;
	}

    private void updateConcepts(DtkAccess priorDtk) throws IOException {
        DtkAccess coreDtk = CoreBuilderTask.loadDtk("dtk-versions/" +
                ((CoreBuilderTaskParameters) this.parameters).currentDtkVersion +
                "/"
        );
        for (DtkConcept concept : coreDtk.getConcepts()) {
            if (concept.getProperty(PropertyType.CORE_ID) != null) {
                DtkConcept priorConcept = priorDtk.getConcept(concept.getConceptId());
                if (priorConcept != null) {
                    priorConcept.update(PropertyType.CORE_ID, concept.getProperty(PropertyType.CORE_ID));
                } else {
                    logger.warn("Apparently deleted: " + concept.getLogString());
                }
            }
        }
    }

    private void exportConcepts(DtkAccess dtk, ArrayList<DtkConcept> concepts) throws IOException {
        Files.createDirectories(outputDirectory);
        Exporter exp = new Exporter(dtk, outputDirectory.toString());
        exp.setDelimiter(Delimiter.Pipe);
        try {
            exp.export(concepts, true);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

}
