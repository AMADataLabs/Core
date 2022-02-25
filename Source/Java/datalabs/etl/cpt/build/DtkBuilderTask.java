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
        DtkAccess priorLink;
        try {
            priorLink = DtkBuilderTask.loadLink("dtk-versions/" +
                    ((DtkBuilderTaskParameters) this.parameters).priorDtkVersion +
                    "/"
            );
            DtkAccess link;
            link = DtkBuilderTask.loadLink(CoreBuilderTask.outputDirectory + "/");

            buildFiles(priorLink, link);
            ConceptIdFactory.init(link);
            updateEmTables(priorLink, link);

            ArrayList<DtkConcept> concepts = link.getConcepts();
            DtkConcept.sort(concepts);
            exportFiles(link, concepts);

            extractFiles(link);

            build(Paths.get(((DtkBuilderTaskParameters) this.parameters).exportDirectory).toString());
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void build(String directory) throws Exception {
        final String versionsDirectory = "dtk-versions/";
        final String version = ((DtkBuilderTaskParameters) this.parameters).version;
        final String incrementalVersion = ((DtkBuilderTaskParameters) this.parameters).incrementalVersion;
        final String annualVersion = ((DtkBuilderTaskParameters) this.parameters).annualVersion;
        DtkAccess link = DtkBuilderTask.loadLink(directory);
        DtkAccess linkIncremental = DtkBuilderTask.loadLink(versionsDirectory + incrementalVersion + "/");
        DtkAccess linkAnnual = DtkBuilderTask.loadLink(versionsDirectory + annualVersion + "/");

        Builder builder = new Builder(link, ((DtkBuilderTaskParameters) this.parameters).linkDate,
                linkIncremental,
                ((DtkBuilderTaskParameters) this.parameters).linkIncrementalDate,
                linkAnnual,
                ((DtkBuilderTaskParameters) this.parameters).linkAnnualDate,
                Collections.singletonList(((DtkBuilderTaskParameters) this.parameters).revisionDate),
                Paths.get(((DtkBuilderTaskParameters) this.parameters).priorHistoryDirectory),
                Paths.get(((DtkBuilderTaskParameters) this.parameters).indexFile),
                Paths.get(((DtkBuilderTaskParameters) this.parameters).guidelinesQAFile),
                Paths.get(((DtkBuilderTaskParameters) this.parameters).editsFile),
                Paths.get(((DtkBuilderTaskParameters) this.parameters).outputDirectory)
        );

        builder.index_format_2021 = true;
        linkAnnual.getConcepts().forEach(con -> con.setCoreSequence(0));

        builder.build();
    }

    private ArrayList<DtkConcept> getConcepts(DtkAccess link) {
        ArrayList<DtkConcept> concepts = new ArrayList<>();
        List<Integer> roots = DtkConceptIds.getRoots(false);
        for (int id : roots) {
            DtkConcept root = link.getConcept(id);
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

	private static DtkAccess loadLink(String directory) throws Exception {
		DtkAccess link = new DtkAccess();

		link.load(
            directory + ExporterFiles.PropertyInternal.getFileNameExt(),
			directory + ExporterFiles.RelationshipGroup.getFileNameExt()
        );

		return link;
	}

    private void buildFiles(DtkAccess priorLink, DtkAccess link) throws Exception {
        Path directory = Paths.get(((DtkBuilderTaskParameters) this.parameters).hcpcsInputDirectory);

//			BuildDtkFiles files = new BuildDtk.BuildDtkFiles(dir.resolve("HCPC2020_ANWEB_w_disclaimer.xls").toString(),
//					dir.resolve("headings update.xlsx").toString(),
//					dir.resolve("cdfcdterms20200815w81206-7.xlsx").toString(),
//					dir.resolve("codingTips attach.xlsx").toString(),
//					dir.resolve("44398_CPT Prof 2021_00_FM iv-xix.docx").toString(),
//					dir.resolve("CPTRVU20T_q1.txt").toString());

        BuildDtkFiles files = new BuildDtk.BuildDtkFiles(directory.resolve(
                ((DtkBuilderTaskParameters) this.parameters).hcpcsDataFile).toString(),
                null, null, null, null, null
        );
        new BuildDtk(priorLink,
                link,
                ((DtkBuilderTaskParameters) this.parameters).revisionDate,
                ((DtkBuilderTaskParameters) this.parameters).hcpsTerminationDate,
                files
        ).run();
    }

    private void updateEmTables(DtkAccess priorLink, DtkAccess link) throws IOException {
        // Note: 2021 for this sample code
        Path directory = Paths.get(((DtkBuilderTaskParameters) this.parameters).emInputDirectory);
        Path outDirectory = Paths.get(((DtkBuilderTaskParameters) this.parameters).emOutputDirectory);
        Files.createDirectories(outDirectory);
        IntroEmTables introEmTables = new IntroEmTables(priorLink, link);
        try {
            introEmTables.buildTableFiles(directory,
                    ((DtkBuilderTaskParameters) this.parameters).emDataFile,
                    outDirectory
            );
            introEmTables.updateEmTables(outDirectory);
        } catch (Exception exception) {
            exception.printStackTrace();
        }
    }

    private void createHeading(DtkAccess priorLink, DtkAccess link) throws IOException {
        Path outputDirectory = Paths.get(((DtkBuilderTaskParameters) this.parameters).headingsOutputDirectory);
        Files.createDirectories(outputDirectory);
        HeadingsWorkbookBuilder workBook = new HeadingsWorkbookBuilder(priorLink, link);
        try {
            workBook.createHeadings(link.getConcept(DtkConceptIds.CPT_ROOT_ID).getDescendants(),
                    outputDirectory.resolve(((DtkBuilderTaskParameters) this.parameters).headingDataFile).toString());
        } catch (Exception exception) {
            exception.printStackTrace();
        }
    }

    private void exportFiles(DtkAccess link, ArrayList<DtkConcept> concepts) throws IOException {
        Path directory = Paths.get(((DtkBuilderTaskParameters) this.parameters).exportDirectory);
        Files.createDirectories(directory);
        Exporter exporter = new Exporter(link, directory.toString());
        exporter.setDelimiter(Delimiter.Pipe);
        try {
            exporter.export(concepts);
            ExporterXml expXml = new ExporterXml(link, directory.toString());
            expXml.export(concepts);
            ExporterOwl expOwl = new ExporterOwl(link, directory.toString());
            expOwl.export(concepts);
        } catch (Exception exception) {
            exception.printStackTrace();
        }
    }

    private void extractFiles(DtkAccess link) throws IOException {
        Path directory = Paths.get(((DtkBuilderTaskParameters) this.parameters).extractDirectory);
        Files.createDirectories(directory);
        Extracts extracts = new Extracts(link, directory.toString());
        ArrayList<DtkConcept> extractConcepts = getConcepts(link);
        DtkConcept.sort(extractConcepts);
        try {
            extracts.extract(extractConcepts);
        } catch (Exception exception) {
            exception.printStackTrace();
        }
    }
}
