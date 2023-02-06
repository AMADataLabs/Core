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

import datalabs.parameter.Parameters;
import datalabs.task.TaskException;

import org.ama.dtk.Exporter;
import org.ama.dtk.ExporterFiles;
import org.ama.dtk.DtkAccess;
import org.ama.dtk.legacy.Legacy;
import org.ama.dtk.model.DtkConcept;
import org.ama.dtk.model.PropertyType;
import org.ama.dtk.terms.ConsumerClinicianWorkbookBuilder;
import org.apache.poi.ss.usermodel.Row;
import org.apache.poi.xssf.usermodel.XSSFSheet;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.mays.util.poi.PoiUtil;

import datalabs.task.Task;


public class ConsumerClinicianDescriptorsBuilderTask extends Task {
    private static final Logger LOGGER = LoggerFactory.getLogger(ConsumerClinicianDescriptorsBuilderTask.class);
    Properties settings = new Properties();

    public ConsumerClinicianDescriptorsBuilderTask(Map<String, String> parameters, ArrayList<byte[]> data)
            throws IllegalAccessException, InstantiationException, InvocationTargetException, NoSuchMethodException
    {
        super(parameters, data, ConsumerClinicianDescriptorsBuilderParameters.class);
    }

    public ArrayList<byte[]> run() throws TaskException{
        ArrayList<byte[]> outputFiles;

        try {
            ConsumerClinicianDescriptorsBuilderParameters parameters
                = (ConsumerClinicianDescriptorsBuilderParameters) this.parameters;

            stageInputFiles();
            loadSettings();

            Path currentLinkPath = Paths.get(
                    settings.getProperty("input.directory"),
                    settings.getProperty("current.link.directory")
            );
            Path incrementalCorePath = Paths.get(
                    settings.getProperty("input.directory"),
                    settings.getProperty("incremental.core.directory")
            );

            String outputDirectory =  settings.getProperty("output.directory") + File.separator + parameters.versionNew + File.separator;
            Files.createDirectories(Paths.get(outputDirectory));

            DtkAccess incrementalCore = ConsumerClinicianDescriptorsBuilderTask.loadLink(incrementalCorePath.toString());
            DtkAccess currentLink = ConsumerClinicianDescriptorsBuilderTask.loadLink(currentLinkPath.toString());
            List<DtkConcept> concepts = new Legacy(currentLink).getConceptsSorted(false, false);

            ConsumerClinicianWorkbookBuilder descriptorBuilder = new ConsumerClinicianWorkbookBuilder(incrementalCore, currentLink);
            descriptorBuilder.createConsumerClinican(concepts, outputDirectory + "cdfcdterms.xlsx");

            File outputFilesDirectory = new File(settings.getProperty("output.directory"));
            outputFiles = loadOutputFiles(outputFilesDirectory);
        } catch (Exception exception) {  // CPT Link code throws Exception, so we have no choice but to catch it
            throw new TaskException(exception);
        }
        return outputFiles;
    }

    void stageInputFiles() throws IOException {
        Path linkBuilderOutputPath = Paths.get(
                settings.getProperty("input.directory"),
                settings.getProperty("link.builder.output.directory")
        );
        Path currentLinkPath = Paths.get(
                settings.getProperty("input.directory"),
                settings.getProperty("current.link.directory")
        );

        this.extractZipFiles(this.data.get(0), linkBuilderOutputPath.toString());
        this.extractZipFiles(this.data.get(1), currentLinkPath.toString());
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

    void loadSettings(){
        String dataDirectory = System.getProperty("data.directory", "tmp");

        settings = new Properties(){{
            put("output.directory", dataDirectory + File.separator + "output");
            put("input.directory", dataDirectory + File.separator + "input");
            put("incremental.core.directory", "incremental_core");
            put("current.link.directory", "current_link");
        }};
    }

    private static DtkAccess loadLink(String directory) throws Exception {
        DtkAccess link = new DtkAccess();

        link.load(
                directory + '/' + ExporterFiles.PropertyInternal.getFileNameExt(),
                directory + '/' + ExporterFiles.RelationshipGroup.getFileNameExt()
        );
        return link;
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
