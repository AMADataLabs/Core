package main

import (
	"bytes"
	"crypto/sha256"
	_ "encoding/xml"
	"fmt"
	"io/ioutil"
	"log"
	"math"
	"os"
	"os/exec"
	"net/http"
	"net/url"
	"path"
	"path/filepath"
	"runtime"
)

func main() {
	config := get_config()

	archive_file := get_download_archive_if_absent(config)

	install_archive(config, archive_file)

	log.Printf("Installation complete.")
}


func get_download_archive_if_absent(config Config) (archive_file string) {
	download_file := os_specific_download_file(config)
    info, err := os.Stat(download_file)

    if os.IsNotExist(err) {
    	archive_file = get_download_archive(config, download_file)
    } else if !info.Mode().IsRegular() {
    	log.Fatalf("Invalid file %s.", download_file)
    } else {
    	archive_file = download_file
    }

    return
}


func get_download_archive(config Config, download_file string) (archive_file string) {
	// TODO: use a temporary file
	archive_file = download_file
	download_url := get_download_url(config.base_url, download_file)
	download_checksum := get_download_checksum(download_url)
	log.Printf("Download URL: %s", download_url)
	log.Printf("Download checksum: %s", download_checksum)

	archive_data := read_resource(download_url)
	log.Printf("Size of Go archive: %d MB", int(math.Round(float64(len(archive_data))/1024/1024)))

	assert_checksum(download_checksum, archive_data)

	write_file(archive_file, archive_data)
	log.Printf("Wrote file '%s'", archive_file)

	return
}


func install_archive(config Config, filename string) {
	switch runtime.GOOS {
	case "linux":
		install_linux_archive(config, filename)
	case "windows":
		run_windows_installer(config, filename)
	}
}


func get_download_url(download_base_url *url.URL, filename string) (*url.URL) {
	download_url, err := url.Parse(download_base_url.String() + filename)
	if err != nil {
		log.Fatal(err)
	}

	return download_url
}


func get_download_checksum(download_url *url.URL) (download_checksum []byte) {
	if download_checksum_url, err := url.Parse(download_url.String() + ".sha256"); err == nil {
		download_checksum = read_resource(download_checksum_url)
	} else {
		log.Fatal(err)
	}

	return
}


func read_resource(url *url.URL) (content []byte) {
	response, _ := http.Get(url.String())
	content, _ = ioutil.ReadAll(response.Body)

	response.Body.Close()

	return
}


func assert_checksum(checksum, data []byte) {
	calculated_checksum := sha256.Sum256(data)
	log.Printf("Archive checksum: %x", calculated_checksum)

	if bytes.Equal(calculated_checksum[:], checksum) {
		log.Fatalf("Bad Go archive checksum: %s.", calculated_checksum)
	}
}


func write_file(filename string, data []byte) (string) {
	if err := ioutil.WriteFile(filename, data, 0655); err != nil {
		log.Fatal(err)
	}

	return filename
}


func os_specific_download_file(config Config) (name string) {
	extension := os_specific_download_extension()
	name = fmt.Sprintf("go%s.%s-%s.%s", config.version, runtime.GOOS, config.architecture, extension)

	return
}


func os_specific_download_extension() (extension string) {
	switch runtime.GOOS {
	case "linux":
		extension = "tar.gz"
	case "windows":
		extension = "msi"
	default:
		log.Fatal(fmt.Sprintf("Unsupported OS '%s'", runtime.GOOS))
	}

	return
}

func install_linux_archive(config Config, filename string) {
	installation_directory := path.Join(config.linux_installation_directory, "go"+config.version)

	make_directory(installation_directory)

	uncompress_archive(filename, installation_directory)

	set_directory_permissions_recursively(installation_directory)
}

func run_windows_installer(config Config, filename string) {
	log.Printf("Installing MSI package %s.", filename)
	command := exec.Command("Msiexec.exe", "/i", filename)

	if err := command.Run(); err != nil {
		log.Fatal(err)
	}
}


func make_directory(directory string) {
    info, err := os.Stat(directory)
    if os.IsNotExist(err) {
        if err = os.MkdirAll(directory, 0744); err != nil {
        	log.Fatal(err)
        }
    } else if !info.IsDir() {
    	log.Fatalf("A file already exists with the path %s.", directory)
    }
}


func uncompress_archive(filename, directory string) {
	log.Printf("Installing Linux tarball %s.", filename)
	command := exec.Command("tar", "xzf", filename, "-C", directory, "--strip-components=1")

	if err := command.Run(); err != nil {
		log.Fatal(err)
	}
}


func set_directory_permissions_recursively(directory string) {
    filepath.Walk(
    	directory,
    	func(path string, info os.FileInfo, err error) error {
	        if err != nil {
	            log.Fatalf(err.Error())
	        }

	        if info.IsDir() {
        		os.Chmod(path, 0755)
	        }

	        return nil
	    },
	)
}



func get_config() (config Config) {
	// TODO: populate from a configuration file or environment variables
	download_base_url := "https://dl.google.com/go/"
	if download_base_url, err := url.Parse(download_base_url); err == nil {
		config = Config{"1.14.2", "amd64", download_base_url, "/usr/local"}

		fmt.Printf("Config: %v\n", config)
	} else {
		log.Fatalf("Invalid download base URL %s", download_base_url)
	}

	return
}


type Config struct {
	version string
	architecture string
	base_url *url.URL
	linux_installation_directory string
}
