package venv

import (
	"fmt"
	_ "io"
	"log"
	"os"
	"os/exec"
	"path"
	"runtime"
	"strings"
)


func RunInVirtualEnvironment(environment_path string, command_path string, arguments []string) {
	if runtime.GOOS == "windows" {
		command := VEnvCommand{"PowerShell.exe", []string{}, environment_path, command_path, arguments}

		command.Run()
	} else {
		command := VEnvCommand{"bash", []string{}, environment_path, command_path, arguments}

		command.Run()
	}
}


func ActivateVirtualEnvironment(environment_path string) {
	if runtime.GOOS == "windows" {
		command := VEnvCommand{"PowerShell.exe", []string{"-NoExit"}, environment_path, "", []string{}}

		command.Run()
	} else {
		command := VEnvCommand{"bash", []string{}, environment_path, "/bin/bash", []string{}}

		command.Run()
	}
}


type VEnvCommand struct {
	ShellPath string
	ShellArgs []string
	VirtualEnvPath string
	CommandPath string
	CommandArgs []string
}


func (venv_cmd VEnvCommand) Run() {
	var command *exec.Cmd

	switch runtime.GOOS {
	case "linux":
		command = venv_cmd.LinuxCommand()
	case "windows":
		command = venv_cmd.WindowsCommand()
	}

	command.Stdout = os.Stdout
	command.Stderr = os.Stderr
	command.Stdin = os.Stdin

	if err := command.Run(); err != nil {
		log.Fatal(err)
	}
}


func (venv_cmd VEnvCommand) LinuxCommand() *exec.Cmd {
	command_args := []string{venv_cmd.CommandPath}
	command_args = append(command_args, venv_cmd.CommandArgs...)
	args := venv_cmd.ShellArgs
	args = append(args, "-c", strings.Join(command_args, " "))

	venv_cmd.SetupLinuxEnvironment()

	return exec.Command(venv_cmd.ShellPath, args...)
}


func (venv_cmd VEnvCommand) WindowsCommand() *exec.Cmd {
	args := venv_cmd.ShellArgs
	args = append(args, path.Join(venv_cmd.VirtualEnvPath, "Scripts", "Activate.ps1"), ";", venv_cmd.CommandPath)
	args = append(args, venv_cmd.CommandArgs...)

	return exec.Command(venv_cmd.ShellPath, args...)
}


func (venv_cmd VEnvCommand) SetupLinuxEnvironment() {
	os.Setenv("VIRTUAL_ENV", venv_cmd.VirtualEnvPath)
	os.Setenv("PATH", fmt.Sprintf("%s/bin:%s", venv_cmd.VirtualEnvPath, os.Getenv("PATH")))
}
