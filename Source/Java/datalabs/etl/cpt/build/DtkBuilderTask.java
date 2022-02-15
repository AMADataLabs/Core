package datalabs.etl.cpt.build;

import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Map;

import org.ama.dtk.Builder;
import org.ama.dtk.Delimiter;
import org.ama.dtk.DtkAccess;
import org.ama.dtk.Exporter;
import org.ama.dtk.ExporterFiles;
import org.ama.dtk.ExporterOwl;
import org.ama.dtk.ExporterXml;
import org.ama.dtk.core.BuildDtk.BuildDtkFiles;
import org.ama.dtk.corea.IntroEmTables;
import org.ama.dtk.extracts.Extracts;
import org.ama.dtk.headings.HeadingsWorkbookBuilder;
import org.ama.dtk.model.DtkConcept;
import org.ama.dtk.model.DtkConceptIds;
import org.ama.dtk.model.PropertyType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import datalabs.task.Task;
import datalabs.etl.cpt.build.CoreBuilderTask;

public class DtkBuilderTask extends Task {

    private static final Logger logger = LoggerFactory.getLogger(DtkBuilderTask.class);

    public DtkBuilderTask(Map<String, String> parameters) throws IllegalAccessException, InstantiationException,
            InvocationTargetException, NoSuchMethodException {
        super(parameters);
    }

    public void run() {
        DtkAccess priorDtk = DtkBuilderTask.loadDtk("dtk-versions/2021u05/");
        DtkAccess dtk = DtkBuilderTask.loadDtk(CoreBuilderTask.outDir + "/");

        ConceptIdFactory.init(dtk);

        buildFiles(priorDtk, dtk);

        try {
            updateEmTables();
        } catch (IOException e) {
            e.printStackTrace();
        }

        try {
            createHeading(priorDtk, dtk);
        } catch (IOException e) {
            e.printStackTrace();
        }

        try {
            buildWorkBookRoles(dtk);
        } catch (IOException e) {
            e.printStackTrace();
        }

        ArrayList<DtkConcept> cons = dtk.getConcepts();
        DtkConcept.sort(cons);

        try {
            exportFiles(dtk);
        } catch (IOException e) {
            e.printStackTrace();
        }

        try {
            extractFiles(dtk);
        } catch (IOException e) {
            e.printStackTrace();
        }

        try {
            build(Paths.get("target", "builddtk_export" + "2022").toString());
        } catch (Exception e) {
            e.printStackTrace();
        }

    }

    public void build(String directory) throws Exception {
        final String versions_directory = "dtk-versions/";
        final String version = "2022";
        final String incVersion = "2021u05";
        final String annVersion = "2021";
        DtkAccess dtk = DtkBuilderTask.loadDtk(directory);
        DtkAccess dtkInc = DtkBuilderTask.loadDtk(versions_directory + incVersion + "/");
        DtkAccess dtkAnn = DtkBuilderTask.loadDtk(versions_directory + annVersion + "/");

        Builder builder = new Builder(dtk, "20210901", dtkInc, "20210501", dtkAnn, "20200901",
            Arrays.asList("20210101"), Paths.get("dtk-versions/", incVersion, "changes"),
            null,
            Paths.get(versions_directory, version, "00inputs", "no-op.txt"),
            Paths.get(versions_directory, version, "00inputs", "reviewed used input.xlsx"),
            Paths.get("target", "build" + version)
        );

        builder.index_format_2021 = true;
        dtkAnn.getConcepts().forEach(con -> con.setCoreSequence(0));

        builder.build();
    }

    private ArrayList<DtkConcept> getConcepts(DtkAccess dtk) {
        ArrayList<DtkConcept> cons = new ArrayList<>();
        List<Integer> roots = DtkConceptIds.getRoots(false);
        for (int id : roots) {
            DtkConcept root = dtk.getConcept(id);
            if (root != null) {
                cons.add(root);
                cons.addAll(root.getDescendants());
            } else {
                logger.error("None for: " + id);
            }
        }
        Collections.sort(cons);
        return cons;
    }

	private static DtkAccess loadDtk(String directory) throws Exception {
		DtkAccess dtk = new DtkAccess();

		dtk.load(
            directory + ExporterFiles.PropertyInternal.getFileNameExt(),
			directory + ExporterFiles.RelationshipGroup.getFileNameExt()
        );

		return dtk;
	}

    private void buildFiles(DtkAccess priorDtk, DtkAccess dtk) {
        Path directory = Paths.get("dtk-versions", "2022", "00inputs");

//			BuildDtkFiles files = new BuildDtk.BuildDtkFiles(dir.resolve("HCPC2020_ANWEB_w_disclaimer.xls").toString(),
//					dir.resolve("headings update.xlsx").toString(),
//					dir.resolve("cdfcdterms20200815w81206-7.xlsx").toString(),
//					dir.resolve("codingTips attach.xlsx").toString(),
//					dir.resolve("44398_CPT Prof 2021_00_FM iv-xix.docx").toString(),
//					dir.resolve("CPTRVU20T_q1.txt").toString());

        BuildDtkFiles files = new BuildDtk.BuildDtkFiles(directory.resolve("HCPC2021_JULY_ANWEB_v2.xlsx").toString(),
                null, null, null, null, null);
        new BuildDtk(priorDtk, dtk, "20220101", "20220101", files).run();
    }

    private void updateEmTables() throws IOException {
        // Note: 2021 for this sample code
        Path directory = Paths.get("dtk-versions", "2021", "00inputs", "intro-em-tables");
        Path outDirectory = Paths.get("target", "builddtk_introemtables" + "2022");
        Files.createDirectories(outDirectory);
        IntroEmTables intro_em_tables = new IntroEmTables(priorDtk, dtk);
        intro_em_tables.buildTableFiles(directory, "44398_CPT Prof 2021_00_FM xx-xxvii.docx", outDirectory);
        intro_em_tables.updateEmTables(outDirectory);

    }

    private void createHeading(DtkAccess priorDtk, DtkAccess dtk) throws IOException {
        Path dir = Paths.get("target", "builddtk_headings" + "2022");
        Files.createDirectories(dir);
        HeadingsWorkbookBuilder wb = new HeadingsWorkbookBuilder(priorDtk, dtk);
        wb.createHeadings(dtk.getConcept(DtkConceptIds.CPT_ROOT_ID).getDescendants(),
                dir.resolve("headings.xlsx").toString());
    }

    private void buildWorkBookRoles(DtkAccess dtk) throws IOException {
        Path directory = Paths.get("target", "builddtk_roles" + "2022");
        Files.createDirectories(directory);
        RolesWorkbookBuilder wb = new RolesWorkbookBuilder(dtk);
        wb.list(directory, "2022", "20210101");
    }

    private void exportFiles(DtkAccess dtk) throws IOException {
        Path directory = Paths.get("target", "builddtk_export" + "2022");
        Files.createDirectories(directory);
        Exporter exp = new Exporter(dtk, directory.toString());
        exp.setDelimiter(Delimiter.Pipe);
        exp.export(cons);
        ExporterXml expXml = new ExporterXml(dtk, directory.toString());
        expXml.export(cons);
        ExporterOwl expOwl = new ExporterOwl(dtk, directory.toString());
        expOwl.export(cons);
    }

    private void extractFiles(DtkAccess dtk) throws IOException {
        Path directory = Paths.get("target", "builddtk_extracts" + "2022");
        Files.createDirectories(directory);
        Extracts extracts = new Extracts(dtk, directory.toString());
        ArrayList<DtkConcept> extractCons = getConcepts(dtk);
        DtkConcept.sort(extractCons);
        extracts.extract(extractCons);
    }
}
