"use client";
import { useEffect, useState } from "react";
import { usePythonConsole } from "react-py";
import { ConsoleState } from "react-py/dist/types/Console";

const Console = () => {
  const [input, setInput] = useState("");
  const [output, setOutput] = useState<String[]>([]);

  const {
    runPython,
    stdout,
    stderr,
    isLoading,
    isRunning,
    banner,
    consoleState,
  } = usePythonConsole();

  useEffect(() => {
    if (stdout) setOutput((prev) => [...prev, stdout]);
  }, [stdout]);

  useEffect(() => {
    if (stderr) setOutput((prev) => [...prev, stderr]);
  }, [stderr]);

  const getPrompt = () =>
    consoleState === ConsoleState.incomplete ? "..." : ">>>";

  const run = () => {
    setOutput((prev) => [...prev, getPrompt() + " " + input + "\n"]);
    runPython(input);
    setInput("");
  };

  return (
    <div className="space-y-5">
      <p className="text-lg font-semibold text-gray-800">Interactive Python Shell</p>

      <div className="bg-gray-900 text-white p-4 rounded-md h-60 overflow-auto text-sm whitespace-pre-wrap">
        {banner && <pre className="text-green-400 mb-2">{banner}</pre>}
        {output.map((line, index) => (
          <div key={index} className="text-white">{line}</div>
        ))}
      </div>

      <form
        className="flex flex-col gap-3"
        onSubmit={(e) => {
          e.preventDefault();
          run();
        }}
      >
        <label className="text-sm font-medium text-gray-700">Command</label>
        <textarea
          rows={3}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter command here..."
          className="w-full px-3 py-2 bg-white border text-black border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black transition"
        />

        <button
          type="submit"
          disabled={isLoading || isRunning}
          className={`px-4 py-2 rounded-md text-white font-medium transition-all ${
            isRunning ? "bg-gray-500 cursor-not-allowed" : "bg-black hover:bg-gray-900"
          }`}
        >
          {isRunning ? "Running..." : "Run Command"}
        </button>
      </form>
    </div>
  );
};

export default Console;
