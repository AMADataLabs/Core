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
import java.util.Properties;
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
    Properties settings = new Properties();

    public LinkBuilderTask(Map<String, String> parameters, ArrayList<byte[]> data)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        super(parameters, null, LinkBuilderParameters.class);
    }

    public ArrayList<byte[]> run() throws TaskException {
        try {
            LinkBuilderParameters parameters = (LinkBuilderParameters) this.parameters;

            stageInputFiles();

            DtkAccess priorLink = LinkBuilderTask.loadLink("./prior_link_data");
            DtkAccess core = LinkBuilderTask.loadLink("./current_link_data");

            LinkBuilderTask.buildLink(priorLink, core, parameters, this.settings);

            LinkBuilderTask.updateEmTables(priorLink, core, this.settings);

//          LinkBuilderTask.createHeadings(priorLink, core);

            LinkBuilderTask.exportConcepts(core, this.settings.get("export.directory").toString());

            LinkBuilderTask.createExtracts(core, this.settings.get("extract.directory").toString());

            LinkBuilderTask.createDistribution(parameters, this.settings);

        } catch (Exception exception) {  // CPT Link code throws Exception, so we have no choice but to catch it
            throw new TaskException(exception.getMessage());
        }

        return null;
    }

	private static DtkAccess loadLink(String directory) throws Exception {
		DtkAccess link = new DtkAccess();

		link.load(
            directory + ExporterFiles.PropertyInternal.getFileNameExt(),
			directory + ExporterFiles.RelationshipGroup.getFileNameExt()
        );

		return link;
	}

    private static void buildLink(DtkAccess priorLink, DtkAccess core, LinkBuilderParameters parameters,
                                  Properties settings)
            throws Exception {

        Path directory = Paths.get(settings.getProperty("hcpcs.input.directory"));

        ConceptIdFactory.init(core);

        BuildDtkFiles files = new BuildDtk.BuildDtkFiles(
                directory.resolve(settings.getProperty("hcpcs.data.file")).toString(),
                settings.getProperty("headings"), settings.getProperty("comsumer.and.clinician.descriptors"),
                settings.getProperty("coding.tips"), settings.getProperty("front.matter"), settings.getProperty("rvus")
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

    private static void updateEmTables(DtkAccess priorLink, DtkAccess core, Properties settings)
            throws Exception {
        Path inputDirectory = Paths.get(settings.getProperty("em.input.directory"));
        Path outputDirectory = Paths.get(settings.getProperty("em.output.directory"));

        Files.createDirectories(outputDirectory);

        IntroEmTables introEmTables = new IntroEmTables(priorLink, core);

        introEmTables.buildTableFiles(inputDirectory, settings.getProperty("em.data.file"), outputDirectory);

        introEmTables.updateEmTables(outputDirectory);
    }

//    private static void createHeadings(DtkAccess priorLink, DtkAccess core, LinkBuilderParameters parameters)
//            throws Exception {
//        Path outputDirectory = Paths.get(parameters.headingsOutputDirectory);
//        HeadingsWorkbookBuilder workBook = new HeadingsWorkbookBuilder(priorLink, core);
//
//        Files.createDirectories(outputDirectory);
//
//        workBook.createHeadings(core.getConcept(DtkConceptIds.CPT_ROOT_ID).getDescendants(),
//            outputDirectory.resolve(parameters.headingDataFile).toString()
//        );
//    }

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

    public static void createDistribution(LinkBuilderParameters parameters, Properties settings)
            throws Exception {
        DtkAccess link = LinkBuilderTask.loadLink(settings.getProperty("export.directory"));

        DtkAccess linkIncremental = LinkBuilderTask.loadLink("./current_link_data");
        DtkAccess linkAnnual = LinkBuilderTask.loadLink("./prior_link_data");

        Builder distribution = new Builder(
            link,
            parameters.linkDate,
            linkIncremental,
            parameters.linkIncrementalDate,
            linkAnnual,
            parameters.linkAnnualDate,
            Collections.singletonList(parameters.revisionDate),
            Paths.get(settings.getProperty("prior.history.directory")),
            Paths.get(settings.getProperty("index.file")),
            Paths.get(settings.getProperty("guidelines.qa.file")),
            Paths.get(settings.getProperty("edits.file")),
            Paths.get(settings.getProperty("output.directory"))
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

    private void loadSettings() {

        settings = new Properties(){{
            put("hcpcs.data.file", "");
            put("hcpcs.data.file", "./HCPC.xlsx");
            put("em.input.directory", "");
            put("em.output.directory", "");
            put("em.data.file", null);
            put("export.directory", "");
            put("extract.directory", "");
            put("prior.history.directory", "./changes/");
            put("index.file", "./cpt_index.docx/");
            put("guidelines.qa.file", null);
            put("edits.file", "./reviewed_used_input.xlsx");
            put("output.directory", "");
            put("headings", null);
            put("comsumer.and.clinician.descriptors", "./cdcterms.xlsx");
            put("conding.tips", "./coding_tips_attach.xlsx");
            put("front.matter", "./front_matter.docx");
            put("rvus", "./cpt_rvu.txt");

        }};

    }

    private void stageInputFiles() throws IOException{
        this.extractZipFiles(this.data.get(0), "./prior_link_data");
        this.extractZipFiles(this.data.get(1), "./current_link_data");
        this.extractZipFiles(this.data.get(2), "./changes");

        this.extractBytes(this.settings.getProperty("hcpcs.data.file"), this.data.get(3));
        this.extractBytes(this.settings.getProperty("consumer.and.clinician.descriptors"), this.data.get(4));
        this.extractBytes(this.settings.getProperty("coding.tips"),this.data.get(5));
        this.extractBytes(this.settings.getProperty("front.matter"), this.data.get(6));
        this.extractBytes(this.settings.getProperty("rvus"), this.data.get(7));
        this.extractBytes(this.settings.getProperty("index.file"), this.data.get(8));
        this.extractBytes(this.settings.getProperty("edits.file"),this.data.get(9));

    }

    private void extractZipFiles(byte[] zip, String directory) throws IOException{
        ByteArrayInputStream byteStream = new ByteArrayInputStream(zip);
        ZipInputStream zipStream = new ZipInputStream(byteStream);
        ZipEntry file = null;

        while((file = zipStream.getNextEntry())!=null) {
            this.writeZipEntryToFile(file, directory, zipStream);
        }
    }

    private void writeZipEntryToFile(ZipEntry zipEntry, String directory, ZipInputStream stream) throws IOException{
        byte[] data = new byte[(int) zipEntry.getSize()];
        String fileName = zipEntry.getName();
        File file = new File(directory + File.separator + fileName);
        FileOutputStream fileOutputStream = new FileOutputStream(file);

        new File(file.getParent()).mkdirs();

        while (stream.read(data, 0, data.length) > 0) {
            fileOutputStream.write(data, 0, data.length);
        }

        fileOutputStream.close();

    }

    private void extractBytes(String path, byte[] data) throws IOException{
        FileOutputStream fileOutputStream = new FileOutputStream(path);
        fileOutputStream.write(data);
        fileOutputStream.close();
    }
}
