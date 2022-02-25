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
        DtkAccess priorLink;
        try {
            priorLink = CoreBuilderTask.loadLink("dtk-versions/" +
                    ((CoreBuilderTaskParameters) this.parameters).priorLinkVersion +
                    "/"
            );
            updateConcepts(priorLink);

            ConceptIdFactory.init(priorLink);
            DtkAccess link = new BuildCore(priorLink, ((CoreBuilderTaskParameters) this.parameters).releaseDate).walk();
            ArrayList<DtkConcept> concepts = link.getConcepts();
            DtkConcept.sort(concepts);
            exportConcepts(link, concepts);

        } catch (IOException exception) {
            exception.printStackTrace();
        }
    }

	private static DtkAccess loadLink(String directory) {
		DtkAccess link = new DtkAccess();

        try {
            link.load(directory + ExporterFiles.PropertyInternal.getFileNameExt(),
                    directory + ExporterFiles.RelationshipGroup.getFileNameExt()
            );
        } catch (Exception e) {
            e.printStackTrace();
        }

        return link;
	}

    private void updateConcepts(DtkAccess priorLink) throws IOException {
        DtkAccess coreDtk = CoreBuilderTask.loadLink("dtk-versions/" +
                ((CoreBuilderTaskParameters) this.parameters).currentLinkVersion +
                "/"
        );
        for (DtkConcept concept : coreDtk.getConcepts()) {
            if (concept.getProperty(PropertyType.CORE_ID) != null) {
                DtkConcept priorConcept = priorLink.getConcept(concept.getConceptId());
                if (priorConcept != null) {
                    priorConcept.update(PropertyType.CORE_ID, concept.getProperty(PropertyType.CORE_ID));
                } else {
                    logger.warn("Apparently deleted: " + concept.getLogString());
                }
            }
        }
    }

<<<<<<< HEAD
    private void exportConcepts(DtkAccess dtk) throws IOException {
        Files.createDirectories(outputDirectory);
        Exporter exp = new Exporter(dtk, outputDirectory.toString());
=======
    private void exportConcepts(DtkAccess link, ArrayList<DtkConcept> concepts) throws IOException {
        Files.createDirectories(outputDirectory);
        Exporter exp = new Exporter(link, outputDirectory.toString());
>>>>>>> story/DL-2413
        exp.setDelimiter(Delimiter.Pipe);
        try {
            exp.export(concepts, true);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

}
