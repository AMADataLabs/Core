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
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

import datalabs.task.TaskException;

import org.ama.dtk.Exporter;
import org.ama.dtk.ExporterFiles;
import org.ama.dtk.DtkAccess;
import org.ama.dtk.legacy.Legacy;
import org.ama.dtk.model.DtkConcept;
import org.ama.dtk.model.PropertyType;
import org.apache.poi.ss.usermodel.Row;
import org.apache.poi.xssf.usermodel.XSSFSheet;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.mays.util.poi.PoiUtil;

import datalabs.task.Task;


public class ConsumerClinicianDescriptorsBuilderTask extends Task {
    private static final Logger LOGGER = LoggerFactory.getLogger(ConsumerClinicianDescriptorsBuilderTask.class);
    Properties settings = null;

    public ConsumerClinicianDescriptorsBuilderTask(Map<String, String> parameters, ArrayList<byte[]> data)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException
    {
        super(parameters, data, ConsumerClinicianDescriptorsParameters.class);
    }

    public ArrayList<byte[]> run() throws TaskException{
        ArrayList<byte[]> outputFiles;

        try {
            ConsumerClinicianDescriptorsParameters parameters = (ConsumerClinicianDescriptorsParameters) this.parameters;

            stageInputFiles();
            loadSettings();

            String outputDirectory =  settings.getProperty("output.directory") + File.separator + parameters.versionNew + File.separator;
            Files.createDirectories(Paths.get(outputDirectory));

            ConsumerClinicianDescriptorsBuilderTask descriptorsBuilder = new ConsumerClinicianDescriptorsBuilderTask(
                    (Map<String, String>) parameters,
                    this.data
            );

            DtkAccess current_link = ConsumerClinicianDescriptorsBuilderTask.loadLink(parameters.versionOld);
            DtkAccess core = ConsumerClinicianDescriptorsBuilderTask.loadLink(parameters.versionNew);
            List<DtkConcept> concepts = new Legacy(core).getConceptsSorted(false, false);

            descriptorsBuilder.createDescriptors(concepts, outputDirectory, current_link);

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

    public void createDescriptors(List<DtkConcept> concepts, String outputFile, DtkAccess current_link) throws Exception {
        XSSFWorkbook workbook = new XSSFWorkbook();
        XSSFSheet clinicianSheet = workbook.createSheet("Clinician");
        XSSFSheet consumerSheet = workbook.createSheet("Consumer");
        createHeaders(consumerSheet, clinicianSheet);
        checkTerms(consumerSheet, clinicianSheet, concepts, current_link);

        PoiUtil.write(workbook, outputFile);
    }

    public static void createHeaders(XSSFSheet consumerSheet, XSSFSheet clinicianSheet) throws  Exception{
        PoiUtil.createHeader(clinicianSheet, "Concept Id", "CPT Code", "Descriptor", "Prior Descriptor", "Clinician Term");
        PoiUtil.createHeader(consumerSheet, "Concept Id", "CPT Code", "Descriptor", "Prior Descriptor", "Consumer Term");
    }

    public static void checkTerms(XSSFSheet consumerSheet, XSSFSheet clinicianSheet, List<DtkConcept> concepts,
                                  DtkAccess current_link) throws Exception {
        for (DtkConcept concept : concepts) {
            if (!concept.shouldHaveConsumerTerm() && !concept.shouldHaveClinicianTerm())
                continue;

            String code = concept.getProperty(PropertyType.CPT_Code);
            DtkConcept conceptOld = current_link.getConcept(concept.getConceptId());
            boolean changedDescriptor = conceptOld != null && !conceptOld.getDescriptor().equals(concept.getDescriptor());

            createConsumerRowIfRequired(consumerSheet, concept, changedDescriptor, conceptOld, code);
            createClinicianRowIfRequired(clinicianSheet, concept, code, changedDescriptor, conceptOld);
        }
    }

    public static void createConsumerRowIfRequired(XSSFSheet consumerSheet, DtkConcept concept, Boolean changedDescriptor,
                                         DtkConcept conceptOld, String code) throws Exception{
        if (concept.shouldHaveConsumerTerm()) {
            createConsumerRow(consumerSheet, concept, changedDescriptor, conceptOld, code);
        }
    }

    public static void createConsumerRow(XSSFSheet consumerSheet, DtkConcept concept, Boolean changedDescriptor,
                                         DtkConcept conceptOld, String code) throws Exception{
        if (concept.getProperty(PropertyType.Consumer_Friendly_Descriptor) == null) {
            PoiUtil.createRow(
                    consumerSheet,
                    consumerSheet.getLastRowNum() + 1,
                    "" + concept.getConceptId(),
                    code,
                    concept.getDescriptor()
            );
        } else if (changedDescriptor) {
            PoiUtil.createRow(
                    consumerSheet,
                    consumerSheet.getLastRowNum() + 1,
                    "" + concept.getConceptId(),
                    code,
                    concept.getDescriptor(),
                    conceptOld.getDescriptor(),
                    concept.getProperty(PropertyType.Consumer_Friendly_Descriptor)
            );
        }
    }

    public static void createClinicianRowIfRequired(XSSFSheet clinicianSheet, DtkConcept concept, String code,
                                          Boolean changedDescriptor, DtkConcept conceptOld) throws Exception {
        if (concept.shouldHaveClinicianTerm()) {
            createClinicianRow(clinicianSheet, concept, code, changedDescriptor, conceptOld);
        }
    }

    public static void createClinicianRow(XSSFSheet clinicianSheet, DtkConcept concept, String code,
                                          Boolean changedDescriptor, DtkConcept conceptOld) throws Exception{
        if (concept.getProperty(PropertyType.Clinician_Descriptor) == null) {
            PoiUtil.createRow(
                    clinicianSheet,
                    clinicianSheet.getLastRowNum() + 1,
                    "" + concept.getConceptId(),
                    code,
                    concept.getDescriptor()
            );
            PoiUtil.createRow(clinicianSheet, clinicianSheet.getLastRowNum() + 1);

        } else if (changedDescriptor) {
            Row rowClinician = PoiUtil.createRow(
                    clinicianSheet,
                    clinicianSheet.getLastRowNum() + 1,
                    "" + concept.getConceptId(),
                    code,
                    concept.getDescriptor(),
                    conceptOld.getDescriptor()
            );
            boolean firstProperty = true;

            for (String descriptor : concept.getProperties(PropertyType.Clinician_Descriptor)) {
                if (!firstProperty)
                    rowClinician = PoiUtil.createRow(clinicianSheet, clinicianSheet.getLastRowNum() + 1);

                PoiUtil.setCellValue(rowClinician, 4, descriptor);
                firstProperty = false;
            }
        }
    }

    void loadSettings(){
        String dataDirectory = System.getProperty("data.directory", "/tmp");

        settings = new Properties(){{
            put("output.directory", dataDirectory + File.separator + "output");
            put("input.directory", dataDirectory + File.separator + "input");
            put("current.core.directory", "/current_core");
        }};
    }

    void stageInputFiles() throws IOException {
        Path currentCorePath = Paths.get(
                settings.getProperty("input.directory"),
                settings.getProperty("current.core.directory")
        );
        
        this.extractZipFiles(this.data.get(1), currentCorePath.toString());

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

    ArrayList<byte[]> loadOutputFiles(File outputDirectory) throws Exception {
        ArrayList<byte[]> outputFiles = new ArrayList<>();

        for (File file: outputDirectory.listFiles()){
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
