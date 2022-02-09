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

	public static Status fromValue(String value) {
		System.out.println(value);
		Status instance = null;

	    for (Status status : values()) {
			System.out.println(status.value);
	        if (value.equals(status.value)) {
	            instance = status;
	        }
	    }
	    return instance;
	}
}
