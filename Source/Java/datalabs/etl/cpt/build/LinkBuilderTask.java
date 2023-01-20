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
    Properties settings = new Properties();

    public LinkBuilderTask(Map<String, String> parameters, ArrayList<byte[]> data)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException {
        super(parameters, data, LinkBuilderParameters.class);
    }

    public ArrayList<byte[]> run() throws TaskException {
        ArrayList<byte[]> outputFiles;

        try {
            LinkBuilderParameters parameters = (LinkBuilderParameters) this.parameters;
            loadSettings();

            Path priorLinkPath = Paths.get(
                    settings.getProperty("input.directory"),
                    settings.getProperty("prior.link.directory")
            );
            Path currentLinkPath = Paths.get(
                    settings.getProperty("input.directory"),
                    settings.getProperty("current.link.directory")
            );
            Path exportPath = Paths.get(
                    settings.getProperty("output.directory"),
                    settings.getProperty("export.directory")
            );
            Path extractPath = Paths.get(
                    settings.getProperty("input.directory"),
                    settings.getProperty("extract.directory")
            );
            Path currentCorePath = Paths.get(
                    settings.getProperty("input.directory"),
                    settings.getProperty("current.core.directory")
            );

            stageInputFiles();

            DtkAccess core = LinkBuilderTask.loadLink(currentCorePath.toString());
            DtkAccess currentLink = LinkBuilderTask.loadLink(currentLinkPath.toString());

            LinkBuilderTask.buildLink(currentLink, core, parameters, this.settings);

            LinkBuilderTask.exportConcepts(core, exportPath.toString());

            LinkBuilderTask.createExtracts(core, extractPath.toString());

            LinkBuilderTask.createDistribution(parameters, this.settings);

            File outputFilesDirectory = new File(settings.getProperty("output.directory"));
            outputFiles = loadOutputFiles(outputFilesDirectory);
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

    private static void buildLink(DtkAccess currentLink, DtkAccess core, LinkBuilderParameters parameters,
                                  Properties settings)
            throws Exception {
        Path directory = Paths.get(
                settings.getProperty("input.directory"),
                settings.getProperty("hcpcs.input.directory")
        );
        Path hcpcsPath = Paths.get(
                settings.getProperty("hcpcs.data.file")
        );
        Path consumerAndClinicianDescriptorsPath = Paths.get(
                settings.getProperty("input.directory"),
                settings.getProperty("consumer.and.clinician.descriptors")
        );
        Path codingTipsPath = Paths.get(
                settings.getProperty("input.directory"),
                settings.getProperty("coding.tips")
        );
        Path rvusPath = Paths.get(
                settings.getProperty("input.directory"),
                settings.getProperty("rvus")
        );
        Path frontMatterPath = Paths.get(
                settings.getProperty("front.matter"),
                settings.getProperty("prior.history.directory")
        );


        ConceptIdFactory.init(core);

        BuildDtkFiles files = new BuildDtk.BuildDtkFiles(
                directory.resolve(hcpcsPath.toString()).toString(),
                null, consumerAndClinicianDescriptorsPath.toString(),
                codingTipsPath.toString(), frontMatterPath.toString(), rvusPath.toString()
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

    private static void updateEmTables(DtkAccess priorLink, DtkAccess core, Properties settings)
            throws Exception {
        Path inputDirectory = Paths.get(
                settings.getProperty("input.directory"),
                settings.getProperty("em.input.directory")
        );
        Path outputDirectory = Paths.get(
                settings.getProperty("input.directory"),
                settings.getProperty("em.output.directory")
        );

        Files.createDirectories(outputDirectory);

        IntroEmTables introEmTables = new IntroEmTables(priorLink, core);

        introEmTables.buildTableFiles(inputDirectory, null, outputDirectory);

        introEmTables.updateEmTables(outputDirectory);
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

    public static void createDistribution(LinkBuilderParameters parameters, Properties settings)
            throws Exception {
        Path priorLinkPath = Paths.get(
                settings.getProperty("input.directory"),
                settings.getProperty("prior.link.directory")
        );
        Path currentLinkPath = Paths.get(
                settings.getProperty("input.directory"),
                settings.getProperty("current.link.directory")
        );
        Path exportPath = Paths.get(
                settings.getProperty("output.directory"),
                settings.getProperty("export.directory")
        );

        DtkAccess link = LinkBuilderTask.loadLink(exportPath.toString());

        DtkAccess linkIncremental = LinkBuilderTask.loadLink(currentLinkPath.toString());
        DtkAccess linkAnnual = LinkBuilderTask.loadLink(priorLinkPath.toString());

        Builder distribution = new Builder(
            link,
            parameters.linkDate,
            linkIncremental,
            parameters.linkIncrementalDate,
            linkAnnual,
            parameters.linkAnnualDate,
            Collections.singletonList(parameters.revisionDate),
            Paths.get(settings.getProperty("input.directory"), settings.getProperty("prior.history.directory")), //changes in current
            Paths.get(settings.getProperty("input.directory"), settings.getProperty("index.file")),
            null,
            Paths.get(settings.getProperty("input.directory"), settings.getProperty("edits.file")),
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

    void loadSettings() {
        String dataDirectory = System.getProperty("data.directory", "/tmp");

        settings = new Properties(){{
            put("hcpcs.data.file", "HCPCS.xlsx");
            put("hcpcs.input.directory", "/hcpcs_input_directory");
            put("em.input.directory", "/em_input");
            put("em.output.directory", "/em_output");
            put("export.directory", "/export");
            put("extract.directory", "/export");
            put("prior.history.directory", "/current_link/changes/");
            put("index.file", "cpt_index.docx");
            put("edits.file", "reviewed_used_input.xlsx");
            put("output.directory", dataDirectory + File.separator + "output");
            put("input.directory",  dataDirectory + File.separator + "input");
            put("consumer.and.clinician.descriptors", "cdcterms.xlsx");
            put("coding.tips", "coding_tips_attach.xlsx");
            put("front.matter", "front_matter.docx");
            put("rvus", "cpt_rvu.txt");
            put("prior.link.directory", "/prior_link");
            put("current.link.directory", "/current_link");
            put("current.core.directory", "/current_core");
        }};
    }

    void stageInputFiles() throws IOException{
        Path priorLinkPath = Paths.get(
                settings.getProperty("input.directory"),
                settings.getProperty("prior.link.directory")
        );
        Path currentLinkPath = Paths.get(
                settings.getProperty("input.directory"),
                settings.getProperty("current.link.directory")
        );
        Path currentCorePath = Paths.get(
                settings.getProperty("input.directory"),
                settings.getProperty("current.core.directory")
        );

        this.extractZipFiles(this.data.get(0), priorLinkPath.toString());
        this.extractZipFiles(this.data.get(1), currentLinkPath.toString());
        this.extractZipFiles(this.data.get(2), currentCorePath.toString());

        Path hcpcsPath = Paths.get(
                settings.getProperty("input.directory"),
                settings.getProperty("hcpcs.data.file")
        );
        Path consumerAndClinicianDescriptorsPath = Paths.get(
                settings.getProperty("input.directory"),
                settings.getProperty("consumer.and.clinician.descriptors")
        );
        Path codingTipsPath = Paths.get(
                settings.getProperty("input.directory"),
                settings.getProperty("coding.tips")
        );
        Path rvusPath = Paths.get(
                settings.getProperty("input.directory"),
                settings.getProperty("rvus")
        );
        Path frontMatterPath = Paths.get(
                settings.getProperty("input.directory"),
                settings.getProperty("front.matter")
        );
        Path indexPath = Paths.get(
                settings.getProperty("input.directory"),
                settings.getProperty("index.file")
        );
        Path editsPath = Paths.get(
                settings.getProperty("input.directory"),
                settings.getProperty("edits.file")
        );

        this.extractBytes(hcpcsPath.toString(), this.data.get(3));
        this.extractBytes(consumerAndClinicianDescriptorsPath.toString(), this.data.get(4));
        this.extractBytes(codingTipsPath.toString(),this.data.get(5));
        this.extractBytes(frontMatterPath.toString(), this.data.get(6));
        this.extractBytes(rvusPath.toString(), this.data.get(7));
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

    ArrayList<byte[]> loadOutputFiles(File outputDirectory) throws Exception {
        ArrayList<byte[]> outputFiles = new ArrayList<>();
        File[] files = outputDirectory.listFiles();

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
