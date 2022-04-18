package datalabs.access.environment;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.Vector;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


public class VariableTree {
    static final Logger LOGGER = LoggerFactory.getLogger(VariableTree.class);

    String value;
    HashMap<String, VariableTree> branches = new HashMap<String, VariableTree>();

    private VariableTree() { }

    public static VariableTree fromEnvironment() {
        return VariableTree.generate(System.getenv());
    }

    public static VariableTree fromEnvironment(String separator) {
        return VariableTree.generate(System.getenv(), separator);
    }

    public static VariableTree generate(Map<String, String> variables) {
        return generate(variables, "__");
    }

    public static VariableTree generate(Map<String, String> variables, String separator) {
        VariableTree root = new VariableTree();

        variables.forEach(
            (key, value) -> root.insertValue(key, value, separator)
        );

        return root;
    }

    public String getValue(String[] branchPath) {
        String value = null;
        if (branchPath.length == 0) {
            value = this.value;
        } else {
            VariableTree branch = this.branches.get(branchPath[0]);

            if (branch == null) {
                throw new IllegalArgumentException("No branch \"" + branchPath[0] + "\"");
            }

            value = branch.getValue(Arrays.copyOfRange(branchPath, 1, branchPath.length));
        }

        return value;
    }

    public String[] getBranches(String[] branchPath) {
        String[] branchNames;

        if (branchPath.length == 0) {
            branchNames = this.branches.keySet().toArray(new String[this.branches.size()]);
        } else {
            VariableTree branch = this.branches.get(branchPath[0]);

            if (branch == null) {
                throw new IllegalArgumentException("No branch \"" + branchPath[0] + "\"");
            }

            branchNames = branch.getBranches(Arrays.copyOfRange(branchPath, 1, branchPath.length));
        }

        return branchNames;
    }

    public Map<String, String> getBranchValues(String[] branchPath) {
        Map<String, String> branches;

        if (branchPath.length > 0) {
            VariableTree branch = this.branches.get(branchPath[0]);

            if (branch == null) {
                throw new IllegalArgumentException("No branch \"" + branchPath[0] + "\"");
            }

            branches = branch.getBranchValues(Arrays.copyOfRange(branchPath, 1, branchPath.length));
        } else {
            branches = new HashMap<String, String>();

            this.branches.forEach(
                (name, branch) -> branches.put(name, branch.value)
            );
        }

        return branches;
    }

    void insertValue(String name, String value, String separator) {
        if (name == null) {
            this.value = value;
        } else {
            String[] nameParts = getNameParts(name, separator);

            VariableTree branch = getOrCreateBranch(nameParts[0], separator);

            branch.insertValue(nameParts[1], value, separator);
        }
    }

    String[] getNameParts(String name, String separator) {
        String[] nameParts = new String[] {name, null};

        if (name.contains(separator)) {
            nameParts = name.split(separator, 2);
        }

        return nameParts;
    }

    VariableTree getOrCreateBranch(String name, String separator) {
        VariableTree branch;

        if (!this.branches.containsKey(name)) {
            branch = new VariableTree();

            this.branches.put(name, branch);
        } else {
            branch = this.branches.get(name);
        }

        return branch;
    }
}
