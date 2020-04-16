package main

import (
	"fmt"
	"log"
	"os"
	"path/filepath"
)


func Path() (repo_path string) {
	script_path = ScriptPath()

	repo_path = filepath.Abs(script_path + string(os.PathSeparator) + "..")

	return
}


func ScriptPath() string {
	script_path, error := filepath.Abs(filepath.Dir(os.Args[0]))

	if error != nil {
		log.Fatal(error)
	}

	return script_path
}
