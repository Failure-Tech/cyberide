"use client";
import React, { useState } from "react";
import { PythonProvider, usePython, usePythonConsole } from "react-py";
import Console from "./console";
import dynamic from "next/dynamic";

const DeepChat = dynamic(
    () => import("deep-chat-react").then((mod) => mod.DeepChat),
    {
        ssr: false
    }
);

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
            <DeepChat
                connect={{
                    url: "http://localhost:5000/chatbot",
                    method: "POST",

                }}
                // directConnection={{
                //     gemini: {"chat": true, "key": process.env.GOOGLE_API_KEY, "validateKeyProperty": true}
                // }}
                // stream={true}
            />
        </>
    )
}

export default Playground;