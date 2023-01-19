package path

import (
	"log"
	"os"
	"path/filepath"
)


func Path() (repo_path string) {
	script_path := script_path()

	// Assumes the running application resides in the Script directory within the repository
	repo_path, error := filepath.Abs(script_path + string(os.PathSeparator) + "..")

	if error != nil {
		log.Fatal(error)
	}

	return repo_path
}


func script_path() string {
	executable, err := os.Executable()
	if err != nil {
		log.Fatal(err)
	}

	script_path, err := filepath.Abs(filepath.Dir(executable))
	if err != nil {
		log.Fatal(err)
	}

	return script_path
}
