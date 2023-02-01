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
import java.util.Arrays;
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
    static final Path DATA_PATH = System.getProperty("data.directory", "/tmp");
    static final Path INPUT_PATH = DATA_PATH.resolve("input");
    static final Path OUTPUT_PATH = DATA_PATH.resolve("output");
    static final Path CURRENT_CORE_PATH = INPUT_PATH.resolve("current_core");
    static final Path INCREMENTAL_CORE_PATH = INPUT_PATH.resolve("incremental_core");
    static final Path ANNUAL_CORE_PATH = INPUT_PATH.resolve("annual_core");
    static final Path PRIOR_LINK_PATH = INPUT_PATH.resolve("prior_link");
    static final Path PRIOR_HISTORY_PATH = PRIOR_LINK_PATH.resolve("dtk");
    static final Path EXPORT_PATH = OUTPUT_PATH.resolve("export");
    static final Path EXTRACTS_PATH = OUTPUT_PATH.resolve("extracts");
    static final Path HCPCS_PATH = INPUT_PATH.resolve("HCPCS.xlsx");
    static final Path CONSUMER_AND_CLINICIAN_DESCRIPTORS_PATH = INPUT_PATH.resolve("cdcterms.xlsx");
    static final Path CODING_TIPS_PATH = INPUT_PATH.resolve("coding_tips_attach.xlsx");
    static final Path RVU_PATH = INPUT_PATH.resolve("cpt_rvu.txt");
    static final Path FRONT_MATTER_PATH = INPUT_PATH.resolve("front_matter.docx");
    static final Path EM_INPUT_PATH = INPUT_PATH.resolve("em");
    static final Path EM_OUTPUT_PATH = OUTPUT_PATH.resolve("em");
    static final Path INDEX_PATH = INPUT_PATH.resolve("cpt_index.docx");
    static final Path EDITS_PATH = INPUT_PATH.resolve("reviewed_used_input.xlsx");


    public LinkBuilderTask(Map<String, String> parameters, ArrayList<byte[]> data)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        super(parameters, data, LinkBuilderParameters.class);
    }

    public ArrayList<byte[]> run() throws TaskException {
        ArrayList<byte[]> outputFiles;

        try {
            LinkBuilderParameters parameters = (LinkBuilderParameters) this.parameters;

            stageInputFiles();

            LinkBuilderTask.buildLink(parameters);

            LinkBuilderTask.exportConcepts(core);

            LinkBuilderTask.createExtracts(core);

            LinkBuilderTask.createDistribution(parameters);

            outputFiles = loadOutputFiles();
        } catch (Exception exception) {  // CPT Link code throws Exception, so we have no choice but to catch it
            throw new TaskException(exception);
        }

        return outputFiles;
    }

	private static DtkAccess loadLink(String directory) throws Exception {
		DtkAccess link = new DtkAccess();

		link.load(
                directory + '/' + ExporterFiles.PropertyInternal.getFileNameExt(),
                directory + '/' + ExporterFiles.RelationshipGroup.getFileNameExt()
        );

		return link;
	}

    private static void buildLink(LinkBuilderParameters parameters)
            throws Exception {
        DtkAccess core = LinkBuilderTask.loadLink(CURRENT_CORE_PATH.toString());
        DtkAccess incrementalCore = LinkBuilderTask.loadLink(INCREMENTAL_CORE_PATH.toString());

        ConceptIdFactory.init(core);

        BuildDtkFiles files = new BuildDtk.BuildDtkFiles(
                HCPCS_PATH.toString(),
                null, CONSUMER_AND_CLINICIAN_DESCRIPTORS_PATH.toString(),
                CODING_TIPS_PATH.toString(), FRONT_MATTER_PATH.toString(), RVU_PATH.toString()
        );

        BuildDtk linkBuilder = new BuildDtk(
            currentLink,
            core,
            parameters.revisionDate,
            parameters.hcpsTerminationDate,
            files
        );

        linkBuilder.run();
    }

    private void updateEmTables(DtkAccess annualLink, DtkAccess core, Properties settings)
            throws Exception {
        Files.createDirectories(EM_OUTPUT_PATH);

        IntroEmTables introEmTables = new IntroEmTables(annualLink, core);

        introEmTables.buildTableFiles(EM_INPUT_PATH, null, EM_OUTPUT_PATH);

        introEmTables.updateEmTables(EM_OUTPUT_PATH);
    }

    private static ArrayList<DtkConcept> getConcepts(DtkAccess link) {
        ArrayList<DtkConcept> concepts = link.getConcepts();

        DtkConcept.sort(concepts);

        return concepts;
    }

    private void exportConcepts(DtkAccess link) throws Exception {
        ArrayList<DtkConcept> concepts = LinkBuilderTask.getConcepts(link);

        Files.createDirectories(EXPORT_PATH);

        LinkBuilderTask.exportPsvConcepts(link, concepts, directory);

        LinkBuilderTask.exportXmlConcepts(link, concepts, directory);

        LinkBuilderTask.exportOwlConcepts(link, concepts, directory);
    }

    private void createExtracts(DtkAccess link) throws Exception {
        Files.createDirectories(EXTRACTS_PATH);

        Extracts extracts = new Extracts(link, directory);

        ArrayList<DtkConcept> concepts = LinkBuilderTask.getAllConcepts(link);

        DtkConcept.sort(concepts);

        extracts.extract(concepts);
    }

    public void createDistribution(LinkBuilderParameters parameters)
            throws Exception {
        DtkAccess currentCore = LinkBuilderTask.loadLink(CURRENT_CORE_PATH.toString());
        DtkAccess incrementalCore = LinkBuilderTask.loadLink(INCREMENTAL_CORE_PATH.toString());
        DtkAccess annualCore = LinkBuilderTask.loadLink(ANNUAL_CORE_PATH.toString());

        Builder distribution = new Builder(
            currentCore,
            parameters.linkDate,
            incrementalCore,
            parameters.linkIncrementalDate,
            annualCore,
            parameters.linkAnnualDate,
            Collections.singletonList(parameters.revisionDate),
            PRIOR_HISTORY_PATH,
            INDEX_PATH,
            null,
            EDITS_PATH,
            OUTPUT_PATH
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

    void stageInputFiles() throws IOException{
        this.extractZipFiles(this.data.get(0), ANNUAL_CORE_PATH.toString());
        this.extractZipFiles(this.data.get(1), INCREMENTAL_CORE_PATH.toString());
        this.extractZipFiles(this.data.get(2), CURRENT_CORE_PATH.toString());

        this.extractBytes(HCPCS_PATH.toString(), this.data.get(3));
        this.extractBytes(CONSUMER_AND_CLINICIAN_DESCRIPTORS_PATH.toString(), this.data.get(4));
        this.extractBytes(CODING_TIPS_PATH.toString(),this.data.get(5));
        this.extractBytes(FRONT_MATTER_PATH.toString(), this.data.get(6));
        this.extractBytes(RVU_PATH.toString(), this.data.get(7));
        this.extractBytes(indexPath.toString(), this.data.get(8));
        this.extractBytes(editsPath.toString(),this.data.get(9));

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
        String fileName = zipEntry.getName();
        File file = new File(directory + File.separator + fileName);

        new File(file.getParent()).mkdirs();

        if (!zipEntry.isDirectory()){
            byte[] data = new byte[1024];
            FileOutputStream fileOutputStream = new FileOutputStream(file);

            while (stream.read(data, 0, data.length) > 0) {
                fileOutputStream.write(data, 0, data.length);
            }
            fileOutputStream.close();
        }

    }

    private void extractBytes(String path, byte[] data) throws IOException{
        FileOutputStream fileOutputStream = new FileOutputStream(path);
        fileOutputStream.write(data);
        fileOutputStream.close();
    }

    ArrayList<byte[]> loadOutputFiles() throws Exception {
        /* FIXME:
         *  1. Determine the most recent "Publish" directory under the output path,
         *  2. Determine the most recent "Build" directory under the output path,
         *  3. Remove all directories under the output path that are not #1 or #2,
         *  4. Zip the output directory as a byte[] object,
         *  5. Return an ArrayList<byte[]> with the byte[] from #4 as the only element.
         */
        ArrayList<byte[]> outputFiles = new ArrayList<>();
        File[] files = OUTPUT_PATH.listFiles();


        Arrays.sort(files);

        for (File file: files) {
            if (file.isDirectory()) {
                ArrayList<byte[]> output = loadOutputFiles(file);

                for (byte[] outputFile: output){
                    outputFiles.add(outputFile);
                }

            } else {
                Path path = Paths.get(file.getPath());
                byte[] data = Files.readAllBytes(path);
                outputFiles.add(data);
            }

        }

        return outputFiles;
    }
}
