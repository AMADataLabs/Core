package datalabs.etl.dag.state;


public enum Status {
	UNKNOWN("Unknown"),
    PENDING("Pending"),
    RUNNING("Running"),
    FINISHED("Finished"),
    FAILED("Failed");

    private String value;

    Status(String value) {
        this.value = value;
    }

    public String getValue() {
        return this.value;
    }
}
