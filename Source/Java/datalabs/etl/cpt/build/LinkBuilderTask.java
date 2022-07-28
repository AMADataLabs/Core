package datalabs.etl.cpt.build;

import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;

import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

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
import datalabs.task.TaskException;

public class LinkBuilderTask extends Task {
    private static final Logger LOGGER = LoggerFactory.getLogger(LinkBuilderTask.class);

    public LinkBuilderTask(Map<String, String> parameters)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        super(parameters, LinkBuilderParameters.class);
    }

    public void run() throws TaskException {
        try {
            LinkBuilderParameters parameters = (LinkBuilderParameters) this.parameters;

            stageInputFiles();

            DtkAccess priorLink = LinkBuilderTask.loadLink("./prior_link_data");
            DtkAccess core = LinkBuilderTask.loadLink("./current_link_data");

            LinkBuilderTask.buildLink(priorLink, core, parameters);

            LinkBuilderTask.updateEmTables(priorLink, core, parameters);

            LinkBuilderTask.createHeadings(priorLink, core, parameters);

            LinkBuilderTask.exportConcepts(core, parameters.exportDirectory);

            LinkBuilderTask.createExtracts(core, parameters.extractDirectory);

            LinkBuilderTask.createDistribution(parameters);
        } catch (Exception exception) {  // CPT Link code throws Exception, so we have no choice but to catch it
            throw new TaskException(exception.getMessage());
        }
    }

	private static DtkAccess loadLink(String directory) throws Exception {
		DtkAccess link = new DtkAccess();

		link.load(
            directory + ExporterFiles.PropertyInternal.getFileNameExt(),
			directory + ExporterFiles.RelationshipGroup.getFileNameExt()
        );

		return link;
	}

    private static void buildLink(DtkAccess priorLink, DtkAccess core, LinkBuilderParameters parameters)
            throws Exception {
        Path directory = Paths.get(parameters.hcpcsInputDirectory);

        ConceptIdFactory.init(core);

        BuildDtkFiles files = new BuildDtk.BuildDtkFiles(
            directory.resolve(parameters.hcpcsDataFile).toString(),
                // where is the headings and front matter input coming in?
                parameters.headings, parameters.consumer_and_clinician_descriptors, parameters.coding_tips,
                parameters.front_matter, parameters.rvus
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
            throws Exception {
        Path inputDirectory = Paths.get(parameters.emInputDirectory);
        Path outputDirectory = Paths.get(parameters.emOutputDirectory);

        Files.createDirectories(outputDirectory);

        IntroEmTables introEmTables = new IntroEmTables(priorLink, core);

        introEmTables.buildTableFiles(inputDirectory, parameters.emDataFile, outputDirectory);

        introEmTables.updateEmTables(outputDirectory);
    }

    private static void createHeadings(DtkAccess priorLink, DtkAccess core, LinkBuilderParameters parameters)
            throws Exception {
        Path outputDirectory = Paths.get(parameters.headingsOutputDirectory);
        HeadingsWorkbookBuilder workBook = new HeadingsWorkbookBuilder(priorLink, core);

        Files.createDirectories(outputDirectory);

        workBook.createHeadings(core.getConcept(DtkConceptIds.CPT_ROOT_ID).getDescendants(),
            // where is the heqading data file input coming from?
            outputDirectory.resolve(parameters.headingDataFile).toString()
        );
    }

    private static ArrayList<DtkConcept> getConcepts(DtkAccess link) {
        ArrayList<DtkConcept> concepts = link.getConcepts();

        DtkConcept.sort(concepts);

        return concepts;
    }

    private static void exportConcepts(DtkAccess link, String directory) throws Exception {
        ArrayList<DtkConcept> concepts = LinkBuilderTask.getConcepts(link);

        Files.createDirectories(Paths.get(directory));

        LinkBuilderTask.exportPsvConcepts(link, concepts, directory);

        LinkBuilderTask.exportXmlConcepts(link, concepts, directory);

        LinkBuilderTask.exportOwlConcepts(link, concepts, directory);
    }

    private static void createExtracts(DtkAccess link, String directory) throws Exception {
        Files.createDirectories(Paths.get(directory));

        Extracts extracts = new Extracts(link, directory);

        ArrayList<DtkConcept> concepts = LinkBuilderTask.getAllConcepts(link);

        DtkConcept.sort(concepts);

        extracts.extract(concepts);
    }

    public static void createDistribution(LinkBuilderParameters parameters) throws Exception {
        final String versionsDirectory = "dtk-versions/";
        final String version = parameters.version;
        final String incrementalVersion = parameters.incrementalVersion;
        final String annualVersion = parameters.annualVersion;
        DtkAccess link = LinkBuilderTask.loadLink(parameters.exportDirectory);

        // do we need another input directory for these two? we have priorLink which is different than this
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
            // where is the input for priorHistory directory?
            Paths.get(parameters.priorHistoryDirectory),
            Paths.get(parameters.indexFile),
            // where is the guidelinesqa file input?
            Paths.get(parameters.guidelinesQAFile),
            // where is the guidelinesqa file input?
            Paths.get(parameters.editsFile),
            Paths.get(parameters.outputDirectory)
        );

        distribution.index_format_2021 = true;

        linkAnnual.getConcepts().forEach(
            concept -> concept.setCoreSequence(0)
        );

        distribution.build();
    }

    private static void exportPsvConcepts(DtkAccess link, ArrayList<DtkConcept> concepts, String directory)
            throws Exception {
        Exporter exporter = new Exporter(link, directory);

        exporter.setDelimiter(Delimiter.Pipe);

        exporter.export(concepts);
    }

    private static void exportXmlConcepts(DtkAccess link, ArrayList<DtkConcept> concepts, String directory)
            throws Exception {
        ExporterXml expXml = new ExporterXml(link, directory);

        expXml.export(concepts);
    }

    private static void exportOwlConcepts(DtkAccess link, ArrayList<DtkConcept> concepts, String directory)
            throws Exception {
        ExporterOwl expOwl = new ExporterOwl(link, directory);

        expOwl.export(concepts);
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

    private void stageInputFiles() throws IOException{
        this.extract_zip_files(this.data.get(0), "./prior_link_data");
        this.extract_zip_files(this.data.get(1), "./current_link_data");
        parameters.hcpcsDataFile = this.data.get(2); // ./HCPC.xlsx
        parameters.headings = this.data.get(3);
        parameters.consumer_and_clinician_descriptors = this.data.get(4); // ./cpt_professional.docx
        parameter.coding_tips = this.data.get(5); //./coding_tips_attach.xlsx
        parameters.front_matter = this.data.get(6);
        parameters.rvus = this.get(7); // ./cpt_rvu.txt
        parameters.indexFile = this.data.get(8) // ./cpt_index.docx

    }

    private void extract_zip_files(byte[] zip, String directory) throws IOException{
        ByteArrayInputStream byteStream = new ByteArrayInputStream(zip);
        ZipInputStream zipStream = new ZipInputStream(byteStream);
        ZipEntry file = null;

        while((file = zipStream.getNextEntry())!=null) {
            this.write_zip_entry_to_file(file, directory, zipStream);
        }
    }

    private void write_zip_entry_to_file(ZipEntry zipEntry, String directory, ZipInputStream stream) throws IOException{
        byte[] data = new byte[(int) zipEntry.getSize()]
        String fileName = zipEntry.getName();
        File file = new File(directory + File.separator + fileName);
        FileOutputStream fileOutputStream = new FileOutputStream(file);

        new File(file.getParent()).mkdirs();

        while (stream.read(data, 0, data.length) > 0) {
            fileOutputStream.write(data, 0, data.length);
        }

        fileOutputStream.close();

    }

}
