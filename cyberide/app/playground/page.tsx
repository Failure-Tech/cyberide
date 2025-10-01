"use client";
import React, { useState } from "react";
import { PythonProvider, usePython, usePythonConsole } from "react-py";
import Console from "./console";

const Playground = () => {
    const [input, setInput] = useState("");
    const [output, setOutput] = useState("");

    const packages = {
        official: ['asciitree'],
        micropip: ['python-cowsay'],
    }

    const { runPython, readFile, writeFile, mkdir, rmdir, stdout, stderr, isLoading, isRunning } = usePython();
    // const { runPythonConsole, stdoutConsole, stderrConsole, isLoadingConsole, isRunningConsole, banner, consoleState } = usePythonConsole();

    // Helper functions
    const read = () => {
        const file = readFile("");
        console.log(file);
    }

    const write = () => {
        const write = writeFile("", "");
        console.log(write);
    }

    return (
        <>
            <PythonProvider packages={packages}>
                <main>
                    {isLoading ? <p>Loading...</p> : <p>Ready!</p>}
                    <form>
                        <textarea
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Enter your code here"
                        />
                        <input 
                            type="submit"
                            value={!isRunning ? "Run" : "Running..."}
                            disabled={isLoading || isRunning}
                            onClick={(e) => {
                                e.preventDefault();
                                runPython(input);
                            }}
                        />
                    </form>
                    <p>Output</p>
                    <pre>
                        <code>{stdout}</code>
                    </pre>
                    <p>Error</p>
                    <pre>
                        <code>{stderr}</code>
                    </pre>
                </main>
            </PythonProvider>
            <Console />
        </>
    )
}

export default Playground;