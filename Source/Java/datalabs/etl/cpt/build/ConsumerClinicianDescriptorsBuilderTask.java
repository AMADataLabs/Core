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
import org.ama.dtk.DtkAccess;
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
    private DtkAccess linkOld;
    private DtkAccess linkNew;

    public ConsumerClinicianDescriptorsBuilderTask(Map<String, String> parameters, ArrayList<byte[]> data)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException
    {
        super(parameters, data, ConsumerClinicianDescriptorsParameters.class);
    }

    public ArrayList<byte[]> run(){
        ArrayList<byte[]> outputFiles = null;
        List<DtkConcept> concepts = new DtkConcept();

        try {
            stageInputFiles();
            loadSettings();

            createConsumerClinician(concepts, settings.getProperty("output.directory"));
            File outputFilesDirectory = new File(settings.getProperty("output.directory"));
            outputFiles = loadOutputFiles(outputFilesDirectory);

        } catch (Exception e) {
            e.printStackTrace();
        }

        return outputFiles;
    }

    public void createConsumerClinician(List<DtkConcept> concepts, String outFile) throws Exception {
        XSSFWorkbook workbook = new XSSFWorkbook();
        XSSFSheet clinicianSheet = workbook.createSheet("Clinician");
        XSSFSheet consumerSheet = workbook.createSheet("Consumer");
        PoiUtil.createHeader(clinicianSheet, "Concept Id", "CPT Code", "Descriptor", "Prior Descriptor", "Clinician Term");
        PoiUtil.createHeader(consumerSheet, "Concept Id", "CPT Code", "Descriptor", "Prior Descriptor", "Consumer Term");
        for (DtkConcept con : concepts) {
            checkConsumerTerm(consumerSheet, con);
            checkClinicianTerm(clinicianSheet, con);
        }

        PoiUtil.write(workbook, outFile);
    }

    public void checkConsumerTerm(XSSFSheet consumerSheet, DtkConcept con) throws Exception{
        if (!con.shouldHaveConsumerTerm() && !con.shouldHaveClinicianTerm())
            continue;
        String code = con.getProperty(PropertyType.CPT_Code);
        DtkConcept conceptOld = linkOld.getConcept(con.getConceptId());
        boolean changedDescriptor = conceptOld != null && !conceptOld.getDescriptor().equals(con.getDescriptor());
        if (con.shouldHaveConsumerTerm()) {
            if (con.getProperty(PropertyType.Consumer_Friendly_Descriptor) == null) {
                PoiUtil.createRow(consumerSheet, consumerSheet.getLastRowNum() + 1, "" + con.getConceptId(), code,
                        con.getDescriptor());
            } else if (changedDescriptor) {
                PoiUtil.createRow(consumerSheet, consumerSheet.getLastRowNum() + 1, "" + con.getConceptId(), code,
                        con.getDescriptor(), conceptOld.getDescriptor(),
                        con.getProperty(PropertyType.Consumer_Friendly_Descriptor));
            }
        }
    }

    public void checkClinicianTerm(XSSFSheet clinicianSheet, DtkConcept con){
        if (con.shouldHaveClinicianTerm()) {
            if (con.getProperty(PropertyType.Clinician_Descriptor) == null) {
                PoiUtil.createRow(clinicianSheet, clinicianSheet.getLastRowNum() + 1, "" + con.getConceptId(), code,
                        con.getDescriptor());
                PoiUtil.createRow(clinicianSheet, clinicianSheet.getLastRowNum() + 1);
            } else if (changedDescriptor) {
                Row clinicianRow = PoiUtil.createRow(clinicianSheet, clinicianSheet.getLastRowNum() + 1, "" + con.getConceptId(), code,
                        con.getDescriptor(), con_old.getDescriptor());
                boolean first_row = true;
                for (String cd : con.getProperties(PropertyType.Clinician_Descriptor)) {
                    if (!first_row)
                        clinicianRow = PoiUtil.createRow(clinicianSheet, clinicianSheet.getLastRowNum() + 1);
                    PoiUtil.setCellValue(clinicianRow, 4, cd);
                    first_row = false;
                }
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
