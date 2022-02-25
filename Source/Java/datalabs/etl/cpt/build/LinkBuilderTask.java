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

public class LinkBuilderTask extends Task {
    private static final Logger LOGGER = LoggerFactory.getLogger(LinkBuilderTask.class);

    public LinkBuilderTask(Map<String, String> parameters)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        super(parameters, LinkBuilderParameters.class);
    }

    public void run() {
        LinkBuilderParameters parameters = (LinkBuilderParameters) this.parameters;
        DtkAccess priorLink = LinkBuilderTask.loadLink("dtk-versions/" + parameters.priorDtkVersion + "/");
        DtkAccess core = LinkBuilderTask.loadLink(parameters.coreDirectory + "/");

        LinkBuilderTask.buildLink(priorLink, core, parameters.hcpcsInputDirectory);

        LinkBuilderTask.updateEmTables(priorLink, core, parameters);

        LinkBuilderTask.createHeadings(priorLink, core, parameters);

        LinkBuilderTask.exportConcepts(link, parameters.exportDirectory);

        LinkBuilderTask.createExtracts(link, parameters.extractDirectory);

        LinkBuilderTask.createDistribution(parameters.exportDirectory);
    }

	private static DtkAccess loadLink(String directory) throws Exception {
		DtkAccess link = new DtkAccess();

		link.load(
            directory + ExporterFiles.PropertyInternal.getFileNameExt(),
			directory + ExporterFiles.RelationshipGroup.getFileNameExt()
        );

		return link;
	}

    private static void buildLink(DtkAccess priorLink, DtkAccess core, LinkBuilderParameters parameters) throws Exception {
        Path directory = Paths.get(parameters.hcpcsInputDirectory);

        ConceptIdFactory.init(core);

        BuildDtkFiles files = new BuildDtk.BuildDtkFiles(
            directory.resolve(parameters.hcpcsDataFile).toString(),
            null, null, null, null, null
        );

        BuildDtk linkBuilder = new BuildDtk(
            priorLink,
            core,
            parameters.revisionDate,
            parameters.hcpsTerminationDate,
            files
        );

        linkBuilder.run();
    }

    private static void updateEmTables(DtkAccess priorLink, DtkAccess core, LinkBuilderParameters parameters)
            throws IOException {
        Path inputDirectory = Paths.get(parameters.emInputDirectory);
        Path outputDirectory = Paths.get(parameters.emOutputDirectory);

        Files.createDirectories(outputDirectory);

        IntroEmTables introEmTables = new IntroEmTables(priorLink, core);

        introEmTables.buildTableFiles(inputDirectory, parameters.emDataFile, outputDirectory);

        introEmTables.updateEmTables(outputDirectory);
    }

    private static void createHeadings(DtkAccess priorLink, DtkAccess core, LinkBuilderParameters parameters)
            throws IOException {
        Path outputDirectory = Paths.get(parameters.headingsOutputDirectory);
        HeadingsWorkbookBuilder workBook = new HeadingsWorkbookBuilder(priorLink, core);

        Files.createDirectories(outputDirectory);

        workBook.createHeadings(core.getConcept(DtkConceptIds.CPT_ROOT_ID).getDescendants(),
            outputDirectory.resolve(parameters.headingDataFile).toString()
        );
    }

    private static ArrayList<DtkConcept> getConcepts(DtkAccess link) {
        ArrayList<DtkConcept> concepts = link.getConcepts();

        DtkConcept.sort(concepts);

        return concepts;
    }

    private static void exportConcepts(DtkAccess link, String directory) throws IOException {
        ArrayList<DtkConcept> concepts = LinkBuilderTask.getConcepts(link);

        Files.createDirectories(Paths.get(directory);

        LinkBuilderTask.exportPsvConcepts(link, concepts, directory);

        LinkBuilderTask.exportXmlConcepts(link, concepts, directory);

        LinkBuilderTask.exportOwlConcepts(link, concepts, directory);
    }

    private static void createExtracts(DtkAccess link, String directory) throws IOException {
        Files.createDirectories(Paths.get(parameters.extractDirectory));

        Extracts extracts = new Extracts(link, directory);

        ArrayList<DtkConcept> concepts = DtkConcept.sort(LinkBuilderTask.getAllConcepts(link));

        extracts.extract(concepts);
    }

    public static void createDistribution(String directory, LinkBuilderParameters parameters) throws Exception {
        final String versionsDirectory = "dtk-versions/";
        final String version = parameters.version;
        final String incrementalVersion = parameters.incrementalVersion;
        final String annualVersion = parameters.annualVersion;
        DtkAccess link = LinkBuilderTask.loadLink(directory);
        DtkAccess linkIncremental = LinkBuilderTask.loadLink(versionsDirectory + incrementalVersion + "/");
        DtkAccess linkAnnual = LinkBuilderTask.loadLink(versionsDirectory + annualVersion + "/");

        Builder distribution = new Builder(
            link,
            parameters.linkDate,
            linkIncremental,
            parameters.linkIncrementalDate,
            linkAnnual,
            parameters.linkAnnualDate,
            Collections.singletonList(parameters.revisionDate),
            Paths.get(parameters.priorHistoryDirectory),
            Paths.get(parameters.indexFile),
            Paths.get(parameters.guidelinesQAFile),
            Paths.get(parameters.editsFile),
            Paths.get(parameters.outputDirectory)
        );

        distribution.index_format_2021 = true;

        linkAnnual.getConcepts().forEach(
            concept -> concept.setCoreSequence(0)
        );

        distribution.build();
    }

    private static void exportPsvConcepts(DtkAccess link, ArrayList<DtkConcept> concepts, String directory) {
        Exporter exporter = new Exporter(link, directory);

        exporter.setDelimiter(Delimiter.Pipe);

        exporter.export(concepts);
    }

    private static void exportXmlConcepts(DtkAccess link, ArrayList<DtkConcept> concepts, String directory) {
        ExporterXml expXml = new ExporterXml(link, directory);

        expXml.export(concepts);
    }

    private static void exportPsvConcepts(DtkAccess link, ArrayList<DtkConcept> concepts, String directory) {
        ExporterOwl expOwl = new ExporterOwl(link, directory);

        expOwl.export(concepts)
    }

    private static ArrayList<DtkConcept> getAllConcepts(DtkAccess link) {
        ArrayList<DtkConcept> concepts = new ArrayList<>();
        List<Integer> roots = DtkConceptIds.getRoots(false);

        for (int id : roots) {
            DtkConcept root = link.getConcept(id);

            if (root != null) {
                concepts.add(root);
                concepts.addAll(root.getDescendants());
            } else {
                LOGGER.error("None for: " + id);
            }
        }

        Collections.sort(concepts);

        return concepts;
    }
}
