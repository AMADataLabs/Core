package datalabs.cpt.build;

import java.lang.reflect.InvocationTargetException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Map;
import java.util.Vector;

import org.ama.dtk.Delimiter;
import org.ama.dtk.DtkAccess;
import org.ama.dtk.DtkAccessTest;
import org.ama.dtk.Exporter;
import org.ama.dtk.model.DtkConcept;
import org.ama.dtk.model.PropertyType;
import org.junit.Test;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import datalabs.task.Task;

public class CoreBuilderTask extends Task {
    private static final Logger logger = LoggerFactory.getLogger(CoreBuilderTask.class);

    public static final Path out_dir = Paths.get("target", "buildcore_export" + "2022_from2021u05");

    public CoreBuilderTask(Map<String, String> parameters) throws IllegalAccessException, InstantiationException,
            InvocationTargetException, NoSuchMethodException {
        super(parameters);
    }


    @Test
    public void walk() throws Exception {
        DtkAccess prior_dtk = DtkAccessTest.load("2021u05");
        {
            DtkAccess core_dtk = DtkAccessTest.load("2021core");
            for (DtkConcept con : core_dtk.getConcepts()) {
                if (con.getProperty(PropertyType.CORE_ID) != null) {
                    DtkConcept prior_con = prior_dtk.getConcept(con.getConceptId());
                    if (prior_con != null) {
                        prior_con.update(PropertyType.CORE_ID, con.getProperty(PropertyType.CORE_ID));
                    } else {
                        logger.warn("Apparently deleted: " + con.getLogString());
                    }
                }
            }
        }
        ConceptIdFactory.init(prior_dtk);
        DtkAccess dtk = new BuildCore(prior_dtk, "20220101").walk();
        ArrayList<DtkConcept> cons = dtk.getConcepts();
        DtkConcept.sort(cons);
        {
            Files.createDirectories(out_dir);
            Exporter exp = new Exporter(dtk, out_dir.toString());
            exp.setDelimiter(Delimiter.Pipe);
            exp.export(cons, true);
        }
    }

    public void run() {

    }
}