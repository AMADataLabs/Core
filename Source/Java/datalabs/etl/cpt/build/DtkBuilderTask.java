package datalabs.etl.cpt.build;

import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;

import org.ama.dtk.Builder;
import org.ama.dtk.Delimiter;
import org.ama.dtk.DtkAccess;
import org.ama.dtk.Exporter;
import org.ama.dtk.ExporterFiles;
import org.ama.dtk.ExporterOwl;
import org.ama.dtk.ExporterXml;
import org.ama.dtk.core.BuildDtk;
import org.ama.dtk.core.BuildDtk.BuildDtkFiles;
import org.ama.dtk.core.ConceptIdFactory;
import org.ama.dtk.corea.IntroEmTables;
import org.ama.dtk.extracts.Extracts;
import org.ama.dtk.headings.HeadingsWorkbookBuilder;
import org.ama.dtk.model.DtkConcept;
import org.ama.dtk.model.DtkConceptIds;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import datalabs.task.Task;

public class DtkBuilderTask extends Task {

    private static final Logger logger = LoggerFactory.getLogger(DtkBuilderTask.class);

    public DtkBuilderTask(Map<String, String> parameters) throws IllegalAccessException, InstantiationException,
            InvocationTargetException, NoSuchMethodException {
        super(parameters, DtkBuilderTaskParameters.class);
    }

    public void run() {
        DtkAccess priorDtk = null;
        try {
            priorDtk = DtkBuilderTask.loadDtk("dtk-versions/2021u05/");
            DtkAccess dtk = null;
            dtk = DtkBuilderTask.loadDtk(CoreBuilderTask.outputDirectory + "/");

            buildFiles(priorDtk, dtk);
            ConceptIdFactory.init(dtk);
            updateEmTables(priorDtk, dtk);

            ArrayList<DtkConcept> concepts = dtk.getConcepts();
            DtkConcept.sort(concepts);
            exportFiles(dtk, concepts);

            extractFiles(dtk);

            build(Paths.get("target", "builddtk_export" + "2022").toString());
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void build(String directory) throws Exception {
        final String versionsDirectory = "dtk-versions/";
        final String version = "2022";
        final String incVersion = "2021u05";
        final String annVersion = "2021";
        DtkAccess dtk = DtkBuilderTask.loadDtk(directory);
        DtkAccess dtkInc = DtkBuilderTask.loadDtk(versionsDirectory + incVersion + "/");
        DtkAccess dtkAnn = DtkBuilderTask.loadDtk(versionsDirectory + annVersion + "/");

        Builder builder = new Builder(dtk, "20210901", dtkInc, "20210501", dtkAnn, "20200901",
                Collections.singletonList("20210101"), Paths.get("dtk-versions/", incVersion, "changes"),
            null,
            Paths.get(versionsDirectory, version, "00inputs", "no-op.txt"),
            Paths.get(versionsDirectory, version, "00inputs", "reviewed used input.xlsx"),
            Paths.get("target", "build" + version)
        );

        builder.index_format_2021 = true;
        dtkAnn.getConcepts().forEach(con -> con.setCoreSequence(0));

        builder.build();
    }

    private ArrayList<DtkConcept> getConcepts(DtkAccess dtk) {
        ArrayList<DtkConcept> concepts = new ArrayList<>();
        List<Integer> roots = DtkConceptIds.getRoots(false);
        for (int id : roots) {
            DtkConcept root = dtk.getConcept(id);
            if (root != null) {
                concepts.add(root);
                concepts.addAll(root.getDescendants());
            } else {
                logger.error("None for: " + id);
            }
        }
        Collections.sort(concepts);
        return concepts;
    }

	private static DtkAccess loadDtk(String directory) throws Exception {
		DtkAccess dtk = new DtkAccess();

		dtk.load(
            directory + ExporterFiles.PropertyInternal.getFileNameExt(),
			directory + ExporterFiles.RelationshipGroup.getFileNameExt()
        );

		return dtk;
	}

    private void buildFiles(DtkAccess priorDtk, DtkAccess dtk) throws Exception {
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

    private void updateEmTables(DtkAccess priorDtk, DtkAccess dtk) throws IOException {
        // Note: 2021 for this sample code
        Path directory = Paths.get("dtk-versions", "2021", "00inputs", "intro-em-tables");
        Path outDirectory = Paths.get("target", "builddtk_introemtables" + "2022");
        Files.createDirectories(outDirectory);
        IntroEmTables introEmTables = new IntroEmTables(priorDtk, dtk);
        try {
            introEmTables.buildTableFiles(directory, "44398_CPT Prof 2021_00_FM xx-xxvii.docx", outDirectory);
            introEmTables.updateEmTables(outDirectory);
        } catch (Exception exception) {
            exception.printStackTrace();
        }
    }

    private void createHeading(DtkAccess priorDtk, DtkAccess dtk) throws IOException {
        Path dir = Paths.get("target", "builddtk_headings" + "2022");
        Files.createDirectories(dir);
        HeadingsWorkbookBuilder workBook = new HeadingsWorkbookBuilder(priorDtk, dtk);
        try {
            workBook.createHeadings(dtk.getConcept(DtkConceptIds.CPT_ROOT_ID).getDescendants(),
                    dir.resolve("headings.xlsx").toString());
        } catch (Exception exception) {
            exception.printStackTrace();
        }
    }

    private void exportFiles(DtkAccess dtk, ArrayList<DtkConcept> concepts) throws IOException {
        Path directory = Paths.get("target", "builddtk_export" + "2022");
        Files.createDirectories(directory);
        Exporter exporter = new Exporter(dtk, directory.toString());
        exporter.setDelimiter(Delimiter.Pipe);
        try {
            exporter.export(concepts);
            ExporterXml expXml = new ExporterXml(dtk, directory.toString());
            expXml.export(concepts);
            ExporterOwl expOwl = new ExporterOwl(dtk, directory.toString());
            expOwl.export(concepts);
        } catch (Exception exception) {
            exception.printStackTrace();
        }
    }

    private void extractFiles(DtkAccess dtk) throws IOException {
        Path directory = Paths.get("target", "builddtk_extracts" + "2022");
        Files.createDirectories(directory);
        Extracts extracts = new Extracts(dtk, directory.toString());
        ArrayList<DtkConcept> extractCons = getConcepts(dtk);
        DtkConcept.sort(extractCons);
        try {
            extracts.extract(extractCons);
        } catch (Exception exception) {
            exception.printStackTrace();
        }
    }
}
