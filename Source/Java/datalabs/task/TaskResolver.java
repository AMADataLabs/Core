package datalabs.task;

import java.util.Map;


public interface TaskResolver {
    public Class getTaskClass(Map<String, String> parameters);
}
