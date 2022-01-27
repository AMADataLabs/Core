package datalabs.access.environment;

import java.util.Vector;


public class VariableTree {
    String value;
    HashMap<String, VariableTree> branches = new HashMap<String, VariableTree>();

    private VariableTree() { }

    public static VariableTree fromEnvironment() {
        return VariableTree.fromEnvironment("__")
    }

    public static VariableTree fromEnvironment(String separator) {
        variables.forEach(
            (key, value) -> insertValue(this, key, value, separator)
        );
    }

    public String getValue(String[] branchPath) {
        String value = null;

        if (branchPath.length == 0) {
            value = this.value;
        } else {
            VariableTree branch = this.branches.get(branchPath[0]);

            value = branch.getValue(Arrays.copyOfRange(branchPath, 1, branchPath.length()));
        }

        return value;
    }

    public String[] getBranches(String[] branches) {
        String[] branchNames;

        if (branchPath.length == 0) {
            branchNames = this.branches.keySet().toArray(new String[this.branches.size()]);
        } else {
            VariableTree branch = this.branches.get(branchPath[0]);

            branchNames = branch.getBranches(Arrays.copyOfRange(branchPath, 1, branchPath.length()));
        }

        return branchNames;
    }

    public Map<String, String> getBranchValues(String[] branches) {
        Map<String, String> branches = this.branches;

        if (branchPath.length > 0) {
            VariableTree branch = this.branches.get(branchPath[0]);

            branches = branch.getBranchValues(Arrays.copyOfRange(branchPath, 1, branchPath.length()));
        }

        return branches;
    }

    insertValue(VariableTree trunk, String name, String value, String separator) {
        if (value.contains(separator)) {
            createBranch(trunk, name, value, separator);
        } else {
            this.value = value;
        }
    }

    createBranch(VariableTree trunk, String name, String value, String separator) {
        VariableTree branch = null;
        String[] nameParts = name.split(separator, 1);

        if (!this.branches.containsKey(nameParts[0])) {
            branch = new VariableTree();
            this.branches.put(nameParts[0], branch);
        } else {
            branch = this.branches.get(nameParts[0]);
        }

        insertValue(branch, nameParts[1], value, separator);
    }
}
