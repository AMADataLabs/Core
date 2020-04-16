package main

import (
	"fmt"
	"log"
	"os"
	"path/filepath"
)


func Path() (repo_path string) {
	script_path := ScriptPath()

	// Assumes the running application resides in the Script directory within the repository
	repo_path, error := filepath.Abs(script_path + string(os.PathSeparator) + "..")

	if error != nil {
		log.Fatal(error)
	}

	return
}


func ScriptPath() string {
	script_path, error := filepath.Abs(filepath.Dir(os.Args[0]))

	if error != nil {
		log.Fatal(error)
	}

	return script_path
}
