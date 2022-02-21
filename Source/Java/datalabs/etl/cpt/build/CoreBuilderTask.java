package datalabs.etl.cpt.build;

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

    public final Path outDir = Paths.get(((CoreBuilderTaskParameters) this.parameters).output_directory);

    public CoreBuilderTask(Map<String, String> parameters) throws IllegalAccessException, InstantiationException,
            InvocationTargetException, NoSuchMethodException {
        super(parameters);
    }

    public void run() {
        DtkAccess priorDtk = null;
        try {
            priorDtk = CoreBuilderTask.loadDtk(
                    "dtk-versions/" +
                    ((CoreBuilderTaskParameters) this.parameters).prior_dtk_version +
                    "/"
            );
        } catch (Exception e) {
            e.printStackTrace();
        }

        try {
            updateConcepts(priorDtk);
        } catch (Exception e) {
            e.printStackTrace();
        }

        ConceptIdFactory.init(priorDtk);
        DtkAccess dtk = new BuildCore(priorDtk, ((CoreBuilderTaskParameters) this.parameters).release_date).walk();
        ArrayList<DtkConcept> cons = dtk.getConcepts();
        DtkConcept.sort(cons);

        try {
            exportConcepts(dtk, cons);
        } catch (Exception e) {
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

    private void updateConcepts(DtkAccess priorDtk) throws Exception {
        DtkAccess coreDtk = CoreBuilderTask.loadDtk(
                "dtk-versions/" +
                ((CoreBuilderTaskParameters) this.parameters).current_dtk_version +
                "/"
        );
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

    private void exportConcepts(DtkAccess dtk, ArrayList<DtkConcept> cons) throws Exception {
        Files.createDirectories(outDir);
        Exporter exp = new Exporter(dtk, outDir.toString());
        exp.setDelimiter(Delimiter.Pipe);
        exp.export(cons, true);
    }

}
