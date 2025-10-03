"use client";
import React, { useState } from "react";
import { PythonProvider, usePython } from "react-py";
import dynamic from "next/dynamic";
import Console from "./console";
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import SideBar from "@/app/components/sidebar"

const DeepChat = dynamic(() => import("deep-chat-react").then((mod) => mod.DeepChat), {
  ssr: false,
});

const Playground = () => {
  const [input, setInput] = useState("");

  const packages = {
    official: ["asciitree"],
    micropip: ["python-cowsay"],
  };

  const { runPython, stdout, stderr, isLoading, isRunning } = usePython();

  return (
    <div className="w-screen flex flex-row bg-white">
        <SideBar selected={0}></SideBar>
        <PythonProvider packages={packages}>
        <div className="w-screen flex flex-row bg-white">
            {/* Left Panel - Python Editor */}
            <div className="grow h-screen flex flex-col px-10 py-8 bg-white gap-6 overflow-y-auto max-w-[65%]">
            <div className="space-y-2">
                <h1 className="text-4xl font-bold text-black">condrx Playground</h1>
                <p className="text-md text-gray-600 max-w-xl">
                Type and run Python code safely in-browser. Start building secure applications!
                </p>
            </div>

            <form className="space-y-4 w-full max-w-3xl">
                <label className="block text-sm font-medium text-gray-700">Python Script</label>
                <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                rows={8}
                placeholder="Write your Python code here..."
                className="w-full px-4 py-3 bg-white text-black border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black transition"
                />
                <SyntaxHighlighter language="python">
                {input}
                </SyntaxHighlighter>

                <button
                type="submit"
                disabled={isLoading || isRunning}
                className={`px-6 py-2 rounded-md text-white font-medium transition-all ${
                    isLoading || isRunning
                    ? "bg-gray-500 cursor-not-allowed"
                    : "bg-black hover:bg-gray-900"
                }`}
                onClick={(e) => {
                    e.preventDefault();
                    runPython(input);
                }}
                >
                {isRunning ? "Running..." : "Run Code"}
                </button>
            </form>

            <div className="space-y-4 w-full max-w-3xl">
                <div>
                <p className="text-sm font-semibold text-gray-700 mb-1">Output:</p>
                <pre className="bg-gray-900 text-green-400 p-4 rounded-md min-h-[100px] whitespace-pre-wrap overflow-auto">
                    <code>{stdout}</code>
                </pre>
                </div>

                <div>
                <p className="text-sm font-semibold text-gray-700 mb-1">Errors:</p>
                <pre className="bg-gray-900 text-red-400 p-4 rounded-md min-h-[100px] whitespace-pre-wrap overflow-auto">
                    <code>{stderr}</code>
                </pre>
                </div>
            </div>
            </div>

            {/* Right Panel - Console and Chat */}
            <div className="w-[35%] h-screen flex flex-col gap-6 p-8 bg-gray-50 overflow-y-auto border-l border-gray-200">
            <div className="bg-white rounded-xl shadow-md p-6">
                <Console />
            </div>

            <div className="bg-white rounded-xl shadow-md p-6">
                <h2 className="text-lg font-semibold text-gray-800 mb-4">Chat with condrx</h2>
                <DeepChat
                connect={{
                    url: "http://localhost:5000/chatbot",
                    method: "POST",
                }}
                />
            </div>
            </div>
        </div>
        </PythonProvider>
    </div>
  );
};

export default Playground;
