package datalabs.etl.dag.cache;

import java.util.ArrayList;


public abstract class TaskDataCache {
    public static enum Direction {
        INPUT, OUTPUT
    }

    public abstract ArrayList<byte[]> extractData();

    public abstract void loadData(ArrayList<byte[]> outputData);
}
