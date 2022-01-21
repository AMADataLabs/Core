package datalabs.task;

import java.util.Map;
import java.util.Vector;

import datalabs.task.Parameters;


public abstract class Task {
    private static Class PARAMETER_CLASS = null;
    private Parameters parameters = null;
    private Vector<byte[]> data = null;

    public Task(Map<String, String> parameters) {
        this.parameters = PARAMETER_CLASS.getConstructor(new Class[] {Map<String, String>}).newInstance(parameters);
    }

    public Task(String parameters, Vector<byte[]> data) {
        Task(parameters);

        this.data = data;
    }

    public abstract void run();

    public Vector<byte[]> getData() {
        return this.data;
    }
}
