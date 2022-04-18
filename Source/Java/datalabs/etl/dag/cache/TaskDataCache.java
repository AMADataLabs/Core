package datalabs.etl.dag.cache;

import java.util.Vector;


public abstract class TaskDataCache {
    public static enum Direction {
        INPUT, OUTPUT
    }

    public abstract Vector<byte[]> extractData();

    public abstract void loadData(Vector<byte[]> outputData);
}
