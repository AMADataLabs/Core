package main

import (
	"os"
	"path"
)

import (
    rpath "datalabs/repo/path"
    "datalabs/repo/venv"
)


func main() {
	environment_path := path.Join(rpath.Path(), "Environment", "Master")
	if len(os.Args) > 1 {
		environment_path = path.Join(rpath.Path(), "Environment", os.Args[1])
	}
    venv.ActivateVirtualEnvironment(environment_path)
}
