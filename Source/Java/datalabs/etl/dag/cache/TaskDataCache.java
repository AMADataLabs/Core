package datalabs.etl.dag.cache;

import java.util.Vector;


public static abstract TaskDataCache {
    public static enum Direction {
        INPUT, OUTPUT
    }

    public abstract Vector<byte[]> extractData();

    public abstract void loadData(Vector<byte[]> outputData);
}
