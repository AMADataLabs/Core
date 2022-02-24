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
import org.ama.dtk.model.DtkConcept;
import org.ama.dtk.model.PropertyType;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import datalabs.task.Task;

public class CoreBuilderTask extends Task {
    private static final Logger logger = LoggerFactory.getLogger(CoreBuilderTask.class);

    public static final Path outputDirectory = Paths.get("target", "buildcore_export" + "2022_from2021u05");

    public CoreBuilderTask(Map<String, String> parameters) throws IllegalAccessException, InstantiationException,
            InvocationTargetException, NoSuchMethodException {
        super(parameters);
    }

    public void run() {
        DtkAccess priorDtk = CoreBuilderTask.loadDtk("dtk-versions/2021u05/");

        updateConcepts(priorDtk);

        ConceptIdFactory.init(priorDtk);
        DtkAccess dtk = new BuildCore(prior_dtk, "20220101").run();
        ArrayList<DtkConcept> cons = dtk.getConcepts();
        DtkConcept.sort(cons);

        try {
            exportConcepts(dtk);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

	private static DtkAccess loadDtk(String directory) throws Exception {
		DtkAccess dtk = new DtkAccess();

		dtk.load(
            directory + ExporterFiles.PropertyInternal.getFileNameExt(),
			directory + ExporterFiles.RelationshipGroup.getFileNameExt()
        );

		return dtk;
	}

    private void updateConcepts(DtkAccess priorDtk) {
        DtkAccess coreDtk = CoreBuilderTask.loadDtk("dtk-versions/2021core/");
        for (DtkConcept con : coreDtk.getConcepts()) {
            if (con.getProperty(PropertyType.CORE_ID) != null) {
                DtkConcept priorCon = priorDtk.getConcept(con.getConceptId());
                if (priorCon != null) {
                    priorCon.update(PropertyType.CORE_ID, con.getProperty(PropertyType.CORE_ID));
                } else {
                    logger.warn("Apparently deleted: " + con.getLogString());
                }
            }
        }
    }

    private void exportConcepts(DtkAccess dtk) throws IOException {
        Files.createDirectories(outputDirectory);
        Exporter exp = new Exporter(dtk, outputDirectory.toString());
        exp.setDelimiter(Delimiter.Pipe);
        exp.export(cons, true);
    }

}
