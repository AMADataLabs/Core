package datalabs.etl.cpt.build;

import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FilenameFilter;
import java.io.FileOutputStream;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.text.SimpleDateFormat;
import java.time.Instant;
import java.time.format.DateTimeFormatter;
import java.time.ZonedDateTime;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Date;
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
import org.zeroturnaround.zip.ZipUtil;

import datalabs.task.Task;
import datalabs.task.TaskException;

public class LinkBuilderTask extends Task {
    private static final Logger LOGGER = LoggerFactory.getLogger(LinkBuilderTask.class);
    final Path DATA_PATH = Paths.get(System.getProperty("data.path", "/tmp"));
    final Path INPUT_PATH = DATA_PATH.resolve("input");
    final Path OUTPUT_PATH = DATA_PATH.resolve("output");
    final Path CURRENT_CORE_PATH = INPUT_PATH.resolve("current_core");
    final Path INCREMENTAL_CORE_PATH = INPUT_PATH.resolve("incremental_core");
    final Path ANNUAL_CORE_PATH = INPUT_PATH.resolve("annual_core");
    final Path PRIOR_LINK_PATH = INPUT_PATH.resolve("prior_link");
    final Path PRIOR_HISTORY_PATH = PRIOR_LINK_PATH.resolve("dtk");
    final Path EXPORT_PATH = OUTPUT_PATH.resolve("export");
    final Path EXTRACTS_PATH = OUTPUT_PATH.resolve("extracts");
    final Path HCPCS_PATH = INPUT_PATH.resolve("HCPCS.xlsx");
    final Path CONSUMER_AND_CLINICIAN_DESCRIPTORS_PATH = INPUT_PATH.resolve("cdcterms.xlsx");
    final Path CODING_TIPS_PATH = INPUT_PATH.resolve("coding_tips_attach.xlsx");
    final Path RVU_PATH = INPUT_PATH.resolve("cpt_rvu.txt");
    final Path FRONT_MATTER_PATH = INPUT_PATH.resolve("front_matter.docx");
    final Path EM_INPUT_PATH = INPUT_PATH.resolve("em");
    final Path EM_OUTPUT_PATH = OUTPUT_PATH.resolve("em");
    final Path INDEX_PATH = INPUT_PATH.resolve("cpt_index.docx");
    final Path EDITS_PATH = INPUT_PATH.resolve("reviewed_used_input.xlsx");


    public LinkBuilderTask(Map<String, String> parameters, ArrayList<byte[]> data)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        super(parameters, data, LinkBuilderParameters.class);
        LOGGER.info("Data Path: " + DATA_PATH.toString());
    }

    public ArrayList<byte[]> run() throws TaskException {
        ArrayList<byte[]> outputFiles;

        try {
            LinkBuilderParameters parameters = (LinkBuilderParameters) this.parameters;

            stageInputFiles();

            DtkAccess annualCore = LinkBuilderTask.loadLink(ANNUAL_CORE_PATH.toString());
            DtkAccess incrementalCore = LinkBuilderTask.loadLink(INCREMENTAL_CORE_PATH.toString());
            DtkAccess currentCore = LinkBuilderTask.loadLink(CURRENT_CORE_PATH.toString());
            DtkAccess priorLink = LinkBuilderTask.loadLink(PRIOR_LINK_PATH.toString());

            buildLink(parameters, priorLink, currentCore);

            exportConcepts(currentCore);

            createExtracts(currentCore);

            generateOutputFiles(parameters, annualCore, incrementalCore, priorLink);

            outputFiles = loadOutputFiles();
        } catch (Exception exception) {  // CPT Link code throws Exception, so we have no choice but to catch it
            throw new TaskException(exception);
        }

        return outputFiles;
    }

    void stageInputFiles() throws IOException{
        this.extractZipFiles(this.data.get(0), ANNUAL_CORE_PATH.toString());
        this.extractZipFiles(this.data.get(1), INCREMENTAL_CORE_PATH.toString());
        this.extractZipFiles(this.data.get(2), CURRENT_CORE_PATH.toString());
        this.extractZipFiles(this.data.get(3), PRIOR_LINK_PATH.toString());

        this.extractBytes(HCPCS_PATH.toString(), this.data.get(4));
        this.extractBytes(CONSUMER_AND_CLINICIAN_DESCRIPTORS_PATH.toString(), this.data.get(5));
        this.extractBytes(CODING_TIPS_PATH.toString(),this.data.get(6));
        this.extractBytes(FRONT_MATTER_PATH.toString(), this.data.get(7));
        this.extractBytes(RVU_PATH.toString(), this.data.get(8));
        this.extractBytes(INDEX_PATH.toString(), this.data.get(9));
        this.extractBytes(EDITS_PATH.toString(),this.data.get(10));
    }

    private void buildLink(LinkBuilderParameters parameters, DtkAccess priorLink, DtkAccess currentCore)
            throws Exception {
        ConceptIdFactory.init(currentCore);

        BuildDtkFiles files = new BuildDtk.BuildDtkFiles(
                HCPCS_PATH.toString(),
                null, CONSUMER_AND_CLINICIAN_DESCRIPTORS_PATH.toString(),
                CODING_TIPS_PATH.toString(), FRONT_MATTER_PATH.toString(), RVU_PATH.toString()
        );

        BuildDtk linkBuilder = new BuildDtk(
            priorLink,
            currentCore,
            LinkBuilderTask.getLinkRevision(parameters.executionTime),
            LinkBuilderTask.getHcpcsMaxTerminationDate(parameters.executionTime),
            files
        );

        linkBuilder.run();
    }

    private void exportConcepts(DtkAccess currentCore) throws Exception {
        ArrayList<DtkConcept> concepts = LinkBuilderTask.getConcepts(currentCore);

        Files.createDirectories(EXPORT_PATH);

        LinkBuilderTask.exportPsvConcepts(currentCore, concepts, EXPORT_PATH.toString());

        LinkBuilderTask.exportXmlConcepts(currentCore, concepts, EXPORT_PATH.toString());

        LinkBuilderTask.exportOwlConcepts(currentCore, concepts, EXPORT_PATH.toString());
    }

    private void createExtracts(DtkAccess currentCore) throws Exception {
        Files.createDirectories(EXTRACTS_PATH);

        Extracts extracts = new Extracts(currentCore, EXTRACTS_PATH.toString());

        ArrayList<DtkConcept> concepts = LinkBuilderTask.getAllConcepts(currentCore);

        DtkConcept.sort(concepts);

        extracts.extract(concepts);
    }

    public void generateOutputFiles(
        LinkBuilderParameters parameters,
        DtkAccess incrementalCore,
        DtkAccess annualCore,
        DtkAccess priorLink
    ) throws Exception {
        Builder outputBuilder = new Builder(
            priorLink,
            LinkBuilderTask.getPriorLinkRevision(parameters.executionTime),
            incrementalCore,
            LinkBuilderTask.getIncrementalCoreRevision(parameters.executionTime),
            annualCore,
            LinkBuilderTask.getAnnualCoreRevision(parameters.executionTime),
            Collections.singletonList(parameters.executionTime),
            PRIOR_HISTORY_PATH,
            INDEX_PATH,
            null,
            EDITS_PATH,
            OUTPUT_PATH
        );

        outputBuilder.index_format_2021 = true;

        annualCore.getConcepts().forEach(
            concept -> concept.setCoreSequence(0)
        );

        outputBuilder.build();
    }

    ArrayList<byte[]> loadOutputFiles() throws Exception {
        Path publishPath = getPublishPath();
        Path buildPath = getBuildPath();
        Path zipPath = OUTPUT_PATH.resolve("output.zip");

        ZipUtil.pack(publishPath.toString(), zipPath.toString());
        ZipUtil.pack(buildPath.toString(), zipPath.toString());
        byte[] byteInput = Files.readAllBytes(zipPath.toPath());

        return new ArrayList<byte[]>() {{
            add(Files.readAllBytes(zipPath.toPath()));
        }};
    }

    private void extractZipFiles(byte[] zip, String directory) throws IOException{
        ByteArrayInputStream byteStream = new ByteArrayInputStream(zip);
        ZipInputStream zipStream = new ZipInputStream(byteStream);
        ZipEntry file = null;

        while((file = zipStream.getNextEntry())!=null) {
            this.writeZipEntryToFile(file, directory, zipStream);
        }
    }

    private void extractBytes(String path, byte[] data) throws IOException{
        FileOutputStream fileOutputStream = new FileOutputStream(path);
        LOGGER.info("Writing file " + path.toString());

        fileOutputStream.write(data);

        fileOutputStream.close();
    }

	private static DtkAccess loadLink(String directory) throws Exception {
		DtkAccess link = new DtkAccess();

		link.load(
                directory + '/' + ExporterFiles.PropertyInternal.getFileNameExt(),
                directory + '/' + ExporterFiles.RelationshipGroup.getFileNameExt()
        );

		return link;
	}

    private static String getLinkRevision(String executionTime) {
        Date executionDate = LinkBuilderTask.getExecutionDate(executionTime);

        return new SimpleDateFormat("yyyyMMdd").format(executionDate);
    }

    private static String getHcpcsMaxTerminationDate(String executionTime) {
        Date executionDate = LinkBuilderTask.getExecutionDate(executionTime);

        return new SimpleDateFormat("yyyyMMdd").format(executionDate);
    }

    private static ArrayList<DtkConcept> getConcepts(DtkAccess link) {
        ArrayList<DtkConcept> concepts = link.getConcepts();

        DtkConcept.sort(concepts);

        return concepts;
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

    private static String getPriorLinkRevision(String executionTime) {
        Date executionDate = LinkBuilderTask.getExecutionDate(executionTime);
        String revision = null;

        switch (executionDate.getMonth()) {
            // December/January Link is January Incremental, so prior Link is Annual
            case 12:
                revision = Integer.toString(executionDate.getYear());
                break;
            case 1:
                revision = Integer.toString(executionDate.getYear() - 1);
                break;
            // April/May Link is May Incremental, so prior Link is January Incremental
            case 4:
            case 5:
                revision = Integer.toString(executionDate.getYear()) + "u01";
                break;
            // August/September Link is Annual, so prior Link is May Incremental
            case 8:
            case 9:
                revision = Integer.toString(executionDate.getYear()) + "u05";
                break;
        }

        return revision;
    }

    private static String getIncrementalCoreRevision(String executionTime) {
        Date executionDate = LinkBuilderTask.getExecutionDate(executionTime);
        String revision = null;

        switch (executionDate.getMonth()) {
            // December/January Link is January Incremental, so incremental Link is Annual
            case 12:
                revision = Integer.toString(executionDate.getYear());
                break;
            case 1:
                revision = Integer.toString(executionDate.getYear() - 1);
                break;
            // April/May Link is May Incremental, so incremental Link is January Incremental
            case 4:
            case 5:
                revision = Integer.toString(executionDate.getYear()) + "u01";
                break;
            // August/September Link is Annual, so prior Link is May Incremental
            case 8:
            case 9:
                revision = Integer.toString(executionDate.getYear()) + "u05";
                break;
        }

        return revision;
    }

    private static String getAnnualCoreRevision(String executionTime) {
        Date executionDate = LinkBuilderTask.getExecutionDate(executionTime);
        String revision = null;

        switch (executionDate.getMonth()) {
            case 12:  // we might be preparing January Incremental in December
                revision = Integer.toString(executionDate.getYear());
                break;
            default:
                revision = Integer.toString(executionDate.getYear() - 1);
        }

        return revision;
    }

    public Path getPublishPath() {
        /* <output>/publish{yyyyMMdd_HHmmss} */
        String datestamp = ZonedDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"));

        File outputDirectory = new File(OUTPUT_PATH.toString());
        File[] files = outputDirectory.listFiles(new FilenameFilter() {
            @Override
            public boolean accept(File dir, String name) {
                LOGGER.info("Testing for publish directory: " + name + " in directory " + dir.getPath());
                return name.startsWith("publish" + datestamp + "_");
            }
        });

        return Paths.get(files[0].getPath());
    }

    public Path getBuildPath() {
        /* <output>/build{yyyyMMdd_HHmmss} */
        String datestamp = ZonedDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"));

        File outputDirectory = new File(OUTPUT_PATH.toString());
        File[] files = outputDirectory.listFiles(new FilenameFilter() {
            @Override
            public boolean accept(File dir, String name) {
                LOGGER.info("Testing for build directory: " + name + " in directory " + dir.getPath());
                return name.startsWith("build" + datestamp + "_");
            }
        });

        return Paths.get(files[0].getPath());
    }

    private static Date getExecutionDate(String executionTime) {
        return Date.from(Instant.from(DateTimeFormatter.ISO_LOCAL_DATE_TIME.parse(executionTime)));
    }

    private void writeZipEntryToFile(ZipEntry zipEntry, String directory, ZipInputStream stream) throws IOException{
        String fileName = zipEntry.getName();
        String filePath = Paths.get(directory, fileName).toString();
        File file = new File(filePath);

        new File(file.getParent()).mkdirs();

        LOGGER.info("Writing extracted zip file " + filePath);

        if (!zipEntry.isDirectory()){
            byte[] data = new byte[1024];
            FileOutputStream fileOutputStream = new FileOutputStream(file);

            while (stream.read(data, 0, data.length) > 0) {
                fileOutputStream.write(data, 0, data.length);
            }
            fileOutputStream.close();
        }

    }

    // FIXME: this doesn't get called anywhere
    private void updateEmTables(DtkAccess annualLink, DtkAccess core, Properties settings)
            throws Exception {
        Files.createDirectories(EM_OUTPUT_PATH);

        IntroEmTables introEmTables = new IntroEmTables(annualLink, core);

        introEmTables.buildTableFiles(EM_INPUT_PATH, null, EM_OUTPUT_PATH);

        introEmTables.updateEmTables(EM_OUTPUT_PATH);
    }
}
