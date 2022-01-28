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
import org.ama.dtk.DtkAccessTest;
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
import org.ama.dtk.roles.ReferenceHierarchies;
import org.ama.dtk.roles.RolesWorkbookBuilder;
import org.ama.dtk.roles.SnomedInactivesUpdate;
import org.ama.dtk.roles.SnomedInactivesWorkbookBuilder;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.mays.snomed.ConceptBasic;
import com.mays.snomed.Snomed;
import com.mays.snomed.SnomedDb;
import com.mays.util.Sql;

import datalabs.task.Task;
import datalabs.etl.cpt.build.CoreBuilderTask;

public class DTKBuilderTask extends Task {

    private static final Logger logger = LoggerFactory.getLogger(DTKBuilderTask.class);

    public DTKBuilderTask(Map<String, String> parameters) throws IllegalAccessException, InstantiationException,
            InvocationTargetException, NoSuchMethodException {
        super(parameters);
    }

    public void run() {
        SnomedDb snomed = new SnomedDb();
        snomed.init(Sql.getConnection("target/ddb/snomed20210301", "snomed"));
        DtkAccess priorDtk = DtkAccessTest.load("2021u05");
        DtkAccess dtk = new DtkAccess();
        
        loadDtk(dtk);
        
        ConceptIdFactory.init(dtk);

        buildFiles(priorDtk, dtk);

        try {
            updateEmTables();
        } catch (IOException e) {
            e.printStackTrace();
        }

        siUpdate();

        try {
            createHeading(priorDtk, dtk);
        } catch (IOException e) {
            e.printStackTrace();
        }

        try {
            createSnomedInactive(dtk, snomed);
        } catch (IOException e) {
            e.printStackTrace();
        }

        try {
            workBookRoles(dtk);
        } catch (IOException e) {
            e.printStackTrace();
        }

        ArrayList<DtkConcept> cons = dtk.getConcepts();
        DtkConcept.sort(cons);

        try {
            fileExporter(dtk);
        } catch (IOException e) {
            e.printStackTrace();
        }

        try {
            fileExtractor(dtk);
        } catch (IOException e) {
            e.printStackTrace();
        }

        try {
            build(Paths.get("target", "builddtk_export" + "2022").toString());
        } catch (Exception e) {
            e.printStackTrace();
        }

    }

    public void build(String dir) throws Exception {
        final String version = "2022";
        final String incVersion = "2021u05";
        final String annVersion = "2021";
        DtkAccess dtk = new DtkAccess();

        dtk.load(dir + "/" + ExporterFiles.PropertyInternal.getFileNameExt(),
                dir + "/" + ExporterFiles.RelationshipGroup.getFileNameExt());

        DtkAccess dtkInc = DtkAccessTest.load(incVersion);
        DtkAccess dtkAnn = DtkAccessTest.load(annVersion);

        Builder builder = new Builder(dtk, "20210901", dtkInc, "20210501", dtkAnn, "20200901",
                Arrays.asList("20210101"), Paths.get(DtkAccessTest.directory, incVersion, "changes"),
//				Paths.get(DtkAccessTest.directory, version, "00inputs", "index",
//						"2021_CPT_Index_3rd-round_Word_doc_Changes_Tracked_07-30-2020_KO_LCJ.docx"),
                null,
//				Paths.get(DtkAccessTest.directory, version, "00inputs", "guidelines_qa.txt"),
                Paths.get(DtkAccessTest.directory, version, "00inputs", "no-op.txt"),
                Paths.get(DtkAccessTest.directory, version, "00inputs", "reviewed used input.xlsx"),
                Paths.get("target", "build" + version));

        builder.index_format_2021 = true;
//		dtkInc.getConcepts().forEach(con -> con.setCoreSequence(0));
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
    
    private void loadDtk(DtkAccess dtk) {
        String directory = CoreBuilderTask.outDir + "/";
        dtk.load(directory + ExporterFiles.PropertyInternal.getFileNameExt(), 
                directory + ExporterFiles.RelationshipGroup.getFileNameExt());
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
    
    private void siUpdate() {
        SnomedInactivesUpdate siUpdate = new SnomedInactivesUpdate(dtk, snomed);
        siUpdate.processUpdate(Paths.get("dtk-versions", "2022", "00inputs", "snomed-inactives.xlsx").toString());
        siUpdate.retireUnusedInactive();
        siUpdate.updateFsns();
        ReferenceHierarchies ref = new ReferenceHierarchies(dtk, snomed);
        ref.run();
        for (int id : DtkConceptIds.getReferenceRoots()) {
            for (DtkConcept con : dtk.getConcept(id).getDescendants()) {
                String sctid = con.getProperty(PropertyType.SNOMED_CT_Code_SCTID);
                if (sctid == null)
                    continue;
                ConceptBasic scon = snomed.getConcept(Long.parseLong(sctid));
                if (!Snomed.isStatusActive(scon.getActive()))
                    logger.error("Inactive: " + scon.getLogString());
            }
        }
    }

    private void createHeading(DtkAccess priorDtk, DtkAccess dtk) throws IOException {
        Path dir = Paths.get("target", "builddtk_headings" + "2022");
        Files.createDirectories(dir);
        HeadingsWorkbookBuilder wb = new HeadingsWorkbookBuilder(priorDtk, dtk);
        wb.createHeadings(dtk.getConcept(DtkConceptIds.CPT_ROOT_ID).getDescendants(),
                dir.resolve("headings.xlsx").toString());
    }

    private void createSnomedInactive(DtkAccess dtk, SnomedDb snomed) throws IOException {
        Path directory = Paths.get("target", "builddtk_snomedinactives" + "2022");
        Files.createDirectories(directory);
        SnomedInactivesWorkbookBuilder wb = new SnomedInactivesWorkbookBuilder(dtk, snomed);
        wb.createSnomedInactives(directory);
    }

    private void workBookRoles(DtkAccess dtk) throws IOException {
        Path directory = Paths.get("target", "builddtk_roles" + "2022");
        Files.createDirectories(directory);
        RolesWorkbookBuilder wb = new RolesWorkbookBuilder(dtk);
        wb.list(directory, "2022", "20210101");
    }

    private void fileExporter(DtkAccess dtk) throws IOException {
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

    private void fileExtractor(DtkAccess dtk) throws IOException {
        Path directory = Paths.get("target", "builddtk_extracts" + "2022");
        Files.createDirectories(directory);
        Extracts extracts = new Extracts(dtk, directory.toString());
        ArrayList<DtkConcept> extractCons = getConcepts(dtk);
        DtkConcept.sort(extractCons);
        extracts.extract(extractCons);
    }
}