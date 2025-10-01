import { useEffect, useState } from "react";
import { usePythonConsole } from "react-py";
import { ConsoleState } from "react-py/dist/types/Console";

const Console = () => {
    const [input, setInput] = useState("");
    const [output, setOutput] = useState<String | any>("");

    const { runPython, stdout, stderr, isLoading, isRunning, banner, consoleState } = usePythonConsole();

    useEffect(() => {
        setOutput((prev: string) => [...prev, stdout])
    }, [stdout]);

    useEffect(() => {
        setOutput((prev: string) => [...prev, stderr])
    }, [stderr]);

    const getPrompt = () => {
        return (
            consoleState === ConsoleState.incomplete ? "..." : ">>>"
        )
    }

    const run = () => {
        setOutput((prev: string) => [...prev, getPrompt() + input + "\n"]);
        runPython(input);
    }

    return (
        <>
            {isLoading ? <p>Loading...</p> : <p>Ready!</p>}
            <p>
                <b>Output</b>
            </p>
            <pre>
                {banner}
                <br />
            </pre>
            <pre>
                {getPrompt()}
                <form>
                    <textarea 
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Enter code in shell here"
                    />
                    <input 
                        type="submit"
                        value={!isRunning ? "Run" : "Running"}
                        disabled={isLoading || isRunning}
                        onClick={(e) => {
                            e.preventDefault();
                            run();
                        }}
                    />
                </form>
            </pre>
        </>
    )
}

export default Console;