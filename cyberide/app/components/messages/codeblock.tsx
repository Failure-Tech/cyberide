// import React from "react";
// import { Copy } from "lucide-react";

// type CodeBlockProps = {
//   code: string;
//   language?: string;
// };

// export const CodeBlock: React.FC<CodeBlockProps> = ({ code, language = "plaintext" }) => {
//   const copyToClipboard = () => {
//     navigator.clipboard.writeText(code);
//   };

//   return (
//     <div className="relative w-full bg-gray-900 text-white rounded-md p-4 font-mono overflow-x-auto">
//       <pre className="whitespace-pre-wrap">
//         <code>{code}</code>
//       </pre>
//       <button
//         className="absolute top-2 right-2 text-white hover:text-green-300"
//         onClick={copyToClipboard}
//         aria-label="Copy code to clipboard"
//       >
//         <Copy size={16} />
//       </button>
//     </div>
//   );
// };

export function CodeBlock({ code, language }: { code: string; language: string }) {
  return (
    <pre className="bg-black text-white p-4 rounded-md overflow-x-auto">
      <code className={`language-${language}`}>{code}</code>
    </pre>
  );
}
